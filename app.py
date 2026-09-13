"""Speech R' Us — sitio público y panel sencillo para artículos y solicitudes."""
from __future__ import annotations

import json
import os
import re
import secrets
import unicodedata
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

import bleach
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    Response,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from db import execute, fetch_all, fetch_one, init_db, set_setting, settings_map
from i18n import ABOUT, FAQ, FIRST_VISIT, GALLERY, HABLA_SLIDES_EN, PLANS, PRIVACY, STRINGS, SVC
from notify import notify
from seed import seed

ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT / "static" / "uploads"
ALLOWED_IMG = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Keep legacy article records working while presenting the unified character art.
ARTICLE_COVER_MAP = {
    "/static/img/cover-senales.jpg": "/static/img/characters-speech.png",
    "/static/img/cover-casa.jpg": "/static/img/characters-playroom.png",
    "/static/img/cover-eval.jpg": "/static/img/characters-listening.png",
    "/static/img/cover-apraxia.jpg": "/static/img/characters-speech.png",
    "/static/img/cover-burbujas.jpg": "/static/img/characters-playroom.png",
    "/static/img/cover-hitos.jpg": "/static/img/characters-waiting.png",
    "/static/img/cover-maneras.jpg": "/static/img/characters-playroom.png",
    "/static/img/cover-procesamiento.jpg": "/static/img/characters-listening.png",
    "/static/img/blog/estimular.jpg": "/static/img/characters-playroom.png",
    "/static/img/blog/procesamiento.jpg": "/static/img/characters-listening.png",
    "/static/img/blog/procesamiento-en.svg": "/static/img/characters-listening.png",
    "/static/img/blog/desarrollo.jpg": "/static/img/characters-waiting.png",
}

ARTICLE_SLUG_COVER_MAP = {
    "apraxia-verbal-de-la-ninez": "/static/img/articles/apraxia-personajes.png",
    "senales-de-que-tu-hijo-puede-necesitar-terapia-del-habla": "/static/img/articles/senales-personajes.png",
    "terapia-de-habla-y-lenguaje": "/static/img/articles/estimular-personajes.png",
    "jugar-con-burbujas-para-el-soplo": "/static/img/articles/burbujas-personajes.png",
    "jugar-con-burbujas-para-el-soplo-2": "/static/img/articles/burbujas-casa-personajes.png",
    "jugar-con-burbujas-para-el-soplo-3": "/static/img/articles/burbujas-juego-personajes.png",
    "como-estimular-el-lenguaje-en-casa": "/static/img/articles/casa-personajes.png",
    "maneras-de-estimular-el-habla-lenguaje-en-ninos": "/static/img/articles/maneras-personajes.png",
    "que-esperar-en-la-primera-evaluacion": "/static/img/articles/evaluacion-personajes.png",
    "desorden-de-procesamiento-auditivo": "/static/img/articles/procesamiento-auditivo-personajes.png",
    "desarrollo-tipico-del-habla-lenguaje": "/static/img/articles/desarrollo-personajes.png",
}

ALLOWED_TAGS = [
    "p", "br", "strong", "b", "em", "i", "u", "h2", "h3", "ul", "ol", "li",
    "a", "img", "blockquote", "span", "div",
]
ALLOWED_ATTRS = {
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt"],
    "*": ["class"],
}

SERVICES = {
    "es": [
        "Habla y lenguaje",
        "Evaluación",
        "Terapia ocupacional",
        "Integración sensorial",
        "Alimentación / disfagia",
        "Terapia oromotora",
        "Apraxia",
        "Psicología",
        "Entrenamiento auditivo",
        "Teleterapia",
        "No estoy segura / otro",
    ],
    "en": [
        "Speech and language",
        "Evaluation",
        "Occupational therapy",
        "Sensory integration",
        "Feeding / dysphagia",
        "Oral-motor therapy",
        "Apraxia",
        "Psychology",
        "Auditory training",
        "Teletherapy",
        "I'm not sure / other",
    ],
}
CLINICS = {"es": ["Hormigueros", "Añasco", "Cualquiera"], "en": ["Hormigueros", "Añasco", "Either"]}
CATEGORIES = {
    "es": [
        "Consejos para familias",
        "Habla y lenguaje",
        "La clínica",
        "Ocupacional",
        "Alimentación",
        "Noticias",
    ],
    "en": [
        "Tips for families",
        "Speech and language",
        "The clinic",
        "Occupational",
        "Feeding",
        "News",
    ],
}
TOPICS = {
    "es": [
        "Información general",
        "Planes médicos",
        "Evaluaciones",
        "Horarios y ubicación",
        "Teleterapia",
        "Otra",
    ],
    "en": [
        "General information",
        "Insurance plans",
        "Evaluations",
        "Hours and location",
        "Teletherapy",
        "Other",
    ],
}

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "speech-rus-site-dev-key")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


@app.after_request
def security_headers(response):
    """Small, deployment-safe browser protections for every response."""
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    return response


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def lang() -> str:
    value = session.get("lang") or request.cookies.get("sru_lang") or "es"
    return "en" if value == "en" else "es"


def t(key: str) -> str:
    pack = STRINGS.get(lang()) or STRINGS["es"]
    return pack.get(key) or STRINGS["es"].get(key) or key


def loc_img(rel: str) -> str:
    rel = (rel or "").replace("\\", "/").lstrip("/")
    if rel.startswith("static/"):
        rel = rel[7:]
    if lang() != "en":
        return rel
    p = Path(rel)
    en = str(p.with_name(p.stem + "-en" + p.suffix)).replace("\\", "/")
    if (ROOT / "static" / en).is_file():
        return en
    return rel


def img_url(rel_or_url: str) -> str:
    rel = (rel_or_url or "").replace("\\", "/")
    if rel.startswith("/static/"):
        rel = rel[8:]
    localized = loc_img(rel)
    webp = str(Path(localized).with_suffix(".webp")).replace("\\", "/")
    if (ROOT / "static" / webp).is_file():
        localized = webp
    return "/static/" + localized


def localize_article(item: dict) -> dict:
    if lang() != "en":
        return item
    for src, dst in (
        ("title_en", "title"),
        ("excerpt_en", "excerpt"),
        ("body_en", "body"),
        ("cover_en", "cover"),
        ("category_en", "category"),
    ):
        val = (item.get(src) or "").strip()
        if val:
            item[dst] = val
    en_slides = parse_slides(item.get("slides_en") or "")
    if en_slides:
        item["slide_list"] = en_slides
    return item


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or secrets.token_hex(4)


def clean_html(html: str) -> str:
    return bleach.clean(html or "", tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)


def clinic():
    data = settings_map()
    phone_digits = re.sub(r"\D", "", data.get("phone_digits") or data.get("phone") or "")
    if phone_digits and not phone_digits.startswith("1"):
        phone_digits = "1" + phone_digits
    data["phone_digits"] = phone_digits
    data["whatsapp"] = f"https://wa.me/{phone_digits}" if phone_digits else "#"
    data["tel"] = f"tel:+{phone_digits}" if phone_digits else "#"
    anasco_digits = re.sub(r"\D", "", data.get("anasco_phone") or "")
    if anasco_digits and not anasco_digits.startswith("1"):
        anasco_digits = "1" + anasco_digits
    data["anasco_tel"] = f"tel:+{anasco_digits}" if anasco_digits else "#"
    data["anasco_whatsapp"] = f"https://wa.me/{anasco_digits}" if anasco_digits else "#"
    data["h_hours"] = data.get("hormigueros_hours") or data.get("hours") or ""
    data["a_hours"] = data.get("anasco_hours") or data.get("hours") or ""
    if lang() == "en" and (data.get("welcome_en") or "").strip():
        data["welcome"] = data["welcome_en"]
    return data


def parse_slides(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(x) for x in data if x]
    except json.JSONDecodeError:
        return []
    return []


def with_slides(row):
    if row is None:
        return None
    item = dict(row)
    item["cover"] = ARTICLE_SLUG_COVER_MAP.get(
        item.get("slug"), ARTICLE_COVER_MAP.get(item.get("cover"), item.get("cover"))
    )
    if item.get("cover_en"):
        item["cover_en"] = ARTICLE_COVER_MAP.get(item["cover_en"], item["cover_en"])
    item["slide_list"] = parse_slides(item.get("slides") or "")
    return item


def published_articles(limit: int | None = None):
    sql = "SELECT * FROM articles WHERE status='published' ORDER BY published_at DESC, id DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    return [with_slides(r) for r in fetch_all(sql)]


def wa_link(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    if digits and not digits.startswith("1"):
        digits = "1" + digits
    return f"https://wa.me/{digits}" if digits else "#"


@app.template_filter("wa")
def _wa_filter(phone: str) -> str:
    return wa_link(phone)


MESES = (
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)


@app.template_filter("fecha")
def fecha(raw: str) -> str:
    if not raw:
        return ""
    try:
        d = datetime.strptime(str(raw)[:10], "%Y-%m-%d")
        if lang() == "en":
            return d.strftime("%B %d, %Y")
        return f"{d.day} de {MESES[d.month]} de {d.year}"
    except ValueError:
        return str(raw)[:10]


@app.context_processor
def inject_globals():
    L = lang()
    return {
        "clinic": clinic(),
        "lang": L,
        "t": t,
        "loc_img": loc_img,
        "img_url": img_url,
        "nav": [
            ("inicio", t("nav_inicio"), "/"),
            ("servicios", t("nav_servicios"), "/servicios"),
            ("nosotros", t("nav_nosotros"), "/nosotros"),
            ("articulos", t("nav_articulos"), "/articulos"),
            ("faq", t("nav_faq"), "/preguntas"),
            ("cita", t("nav_cita"), "/cita"),
            ("contacto", t("nav_contacto"), "/contacto"),
        ],
        "year": datetime.now().year,
        "csrf_token": session.get("csrf"),
        "habla_slides_en": HABLA_SLIDES_EN,
    }


@app.get("/lang/<code>")
def set_lang(code: str):
    chosen = "en" if code == "en" else "es"
    session["lang"] = chosen
    dest = request.args.get("next") or request.referrer or "/"
    resp = redirect(dest)
    resp.set_cookie("sru_lang", chosen, max_age=60 * 60 * 24 * 365)
    return resp


def ensure_csrf():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(24)


def valid_csrf() -> bool:
    token = request.form.get("csrf") or request.headers.get("X-CSRF-Token")
    return bool(token) and token == session.get("csrf")


def honeypot_ok() -> bool:
    return not (request.form.get("website") or "").strip()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("admin_login", next=request.path))
        return fn(*args, **kwargs)
    return wrapper


@app.before_request
def _boot():
    ensure_csrf()
    if "lang" not in session and request.cookies.get("sru_lang") in ("es", "en"):
        session["lang"] = request.cookies.get("sru_lang")


# ── Public ────────────────────────────────────────────────────────────────


@app.get("/robots.txt")
def robots_txt():
    body = f"User-agent: *\nAllow: /\nDisallow: /admin\nSitemap: {request.url_root.rstrip('/')}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@app.get("/sitemap.xml")
def sitemap_xml():
    paths = [
        "/", "/servicios", "/nosotros", "/articulos", "/preguntas", "/cita",
        "/contacto", "/privacidad", "/galeria", "/primera-visita", "/planes",
        "/talleres", "/testimonios",
    ]
    paths.extend(f"/articulos/{a['slug']}" for a in published_articles())
    root = request.url_root.rstrip("/")
    urls = "".join(f"<url><loc>{root}{path}</loc></url>" for path in paths)
    return Response(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}</urlset>",
        mimetype="application/xml",
    )


@app.get("/")
def home():
    skip = {
        "terapia-de-habla-y-lenguaje",
        "senales-de-que-tu-hijo-puede-necesitar-terapia-del-habla",
    }
    more = [localize_article(a) for a in published_articles() if a["slug"] not in skip][:3]
    quotes = fetch_all("SELECT * FROM quotes WHERE visible=1 ORDER BY sort, id LIMIT 3")
    return render_template(
        "public/home.html",
        page="inicio",
        articles=more,
        quotes=quotes,
        services_preview=SERVICES[lang()][:6],
    )


@app.get("/servicios")
def servicios():
    return render_template("public/servicios.html", page="servicios", svc=SVC[lang()], plans=PLANS[lang()])


@app.get("/nosotros")
def nosotros():
    team = fetch_all("SELECT * FROM team WHERE visible=1 ORDER BY sort, name")
    return render_template("public/nosotros.html", page="nosotros", team=team, about=ABOUT[lang()])


@app.get("/blog")
@app.get("/articulos")
def articulos():
    arts = [localize_article(a) for a in published_articles()]
    featured = next((a for a in arts if a["slug"] == "apraxia-verbal-de-la-ninez"), arts[0] if arts else None)
    rest = [a for a in arts if not featured or a["id"] != featured["id"]]
    cats = sorted({a["category"] for a in arts if a.get("category")})
    return render_template(
        "public/articulos.html",
        page="articulos",
        featured=featured,
        articles=rest,
        categories=cats,
    )


@app.get("/blog/<slug>")
@app.get("/articulos/<slug>")
def articulo(slug: str):
    row = fetch_one("SELECT * FROM articles WHERE slug=? AND status='published'", (slug,))
    if not row:
        abort(404)
    others = [with_slides(r) for r in fetch_all(
        "SELECT * FROM articles WHERE status='published' AND id!=? ORDER BY published_at DESC LIMIT 3",
        (row["id"],),
    )]
    return render_template(
        "public/articulo.html",
        page="articulos",
        article=localize_article(with_slides(row)),
        others=[localize_article(o) for o in others],
    )


@app.route("/cita", methods=["GET", "POST"])
def cita():
    if request.method == "POST":
        if not valid_csrf() or not honeypot_ok():
            abort(400)
        parent = (request.form.get("parent_name") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        if not parent or not phone:
            flash(t("cita_need"), "error")
            return render_template("public/cita.html", page="cita", services=SERVICES[lang()], clinics=CLINICS[lang()])
        execute(
            """INSERT INTO appointment_requests
               (parent_name, child_name, child_age, phone, email, clinic, service, preferred, notes, status, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,'nueva',?)""",
            (
                parent[:120],
                (request.form.get("child_name") or "").strip()[:120],
                (request.form.get("child_age") or "").strip()[:40],
                phone[:40],
                (request.form.get("email") or "").strip()[:120],
                (request.form.get("clinic") or "Hormigueros")[:40],
                (request.form.get("service") or "")[:80],
                (request.form.get("preferred") or "").strip()[:200],
                (request.form.get("notes") or "").strip()[:2000],
                utcnow(),
            ),
        )
        notify(
            "Nueva cita — Speech R' Us",
            f"{parent} / {phone} / {request.form.get('clinic')} / {request.form.get('service')}",
        )
        return render_template("public/gracias.html", page="cita", kind="cita")
    return render_template("public/cita.html", page="cita", services=SERVICES[lang()], clinics=CLINICS[lang()])


@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        if not valid_csrf() or not honeypot_ok():
            abort(400)
        name = (request.form.get("name") or "").strip()
        message = (request.form.get("message") or "").strip()
        if not name or not message:
            flash(t("info_need"), "error")
            return render_template("public/contacto.html", page="contacto", topics=TOPICS[lang()])
        execute(
            """INSERT INTO info_requests(name, phone, email, topic, message, status, created_at)
               VALUES (?,?,?,?,?,'nueva',?)""",
            (
                name[:120],
                (request.form.get("phone") or "").strip()[:40],
                (request.form.get("email") or "").strip()[:120],
                (request.form.get("topic") or "Información general")[:80],
                message[:3000],
                utcnow(),
            ),
        )
        notify("Nueva pregunta — Speech R' Us", f"{name}: {message[:400]}")
        return render_template("public/gracias.html", page="contacto", kind="info")
    return render_template("public/contacto.html", page="contacto", topics=TOPICS[lang()])


@app.get("/privacidad")
def privacidad():
    return render_template("public/privacidad.html", page="", privacy=PRIVACY[lang()])


@app.get("/preguntas")
def preguntas():
    return render_template("public/faq.html", page="faq", items=FAQ[lang()])


@app.get("/galeria")
def galeria():
    return render_template("public/galeria.html", page="nosotros", gallery=GALLERY)


@app.get("/primera-visita")
def primera_visita():
    return render_template("public/primera.html", page="nosotros", steps=FIRST_VISIT[lang()])


@app.get("/planes")
def planes():
    return render_template("public/planes.html", page="servicios", plans=PLANS[lang()])


@app.get("/talleres")
def talleres():
    rows = fetch_all("SELECT * FROM events ORDER BY when_at, id DESC")
    return render_template("public/talleres.html", page="nosotros", events=rows)


@app.get("/testimonios")
def testimonios():
    rows = fetch_all("SELECT * FROM quotes WHERE visible=1 ORDER BY sort, id")
    return render_template("public/testimonios.html", page="nosotros", quotes=rows)


# ── Admin auth ────────────────────────────────────────────────────────────


@app.route("/admin/entrar", methods=["GET", "POST"])
def admin_login():
    if session.get("user_id"):
        return redirect(url_for("admin_home"))
    if request.method == "POST":
        if not valid_csrf():
            abort(400)
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        user = fetch_one("SELECT * FROM users WHERE username=?", (username,))
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session.permanent = True
            return redirect(request.args.get("next") or url_for("admin_home"))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("admin/login.html")


@app.post("/admin/salir")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.get("/admin")
@login_required
def admin_home():
    citas = fetch_all(
        "SELECT * FROM appointment_requests ORDER BY id DESC LIMIT 40"
    )
    infos = fetch_all("SELECT * FROM info_requests ORDER BY id DESC LIMIT 40")
    arts = fetch_all("SELECT * FROM articles ORDER BY updated_at DESC LIMIT 8")
    nueva_citas = sum(1 for c in citas if c["status"] == "nueva")
    nueva_info = sum(1 for i in infos if i["status"] == "nueva")
    return render_template(
        "admin/home.html",
        citas=citas,
        infos=infos,
        articles=arts,
        nueva_citas=nueva_citas,
        nueva_info=nueva_info,
    )


# ── Articles CMS ──────────────────────────────────────────────────────────


@app.get("/admin/articulos")
@login_required
def admin_articulos():
    rows = fetch_all("SELECT * FROM articles ORDER BY updated_at DESC")
    return render_template("admin/articulos.html", articles=rows)


@app.route("/admin/articulos/nuevo", methods=["GET", "POST"])
@login_required
def admin_articulo_nuevo():
    if request.method == "POST":
        return _save_article(None)
    return render_template(
        "admin/articulo_form.html",
        article=None,
        slide_list=[],
        categories=CATEGORIES["es"],
    )


@app.route("/admin/articulos/<int:art_id>", methods=["GET", "POST"])
@login_required
def admin_articulo_editar(art_id: int):
    row = fetch_one("SELECT * FROM articles WHERE id=?", (art_id,))
    if not row:
        abort(404)
    if request.method == "POST":
        return _save_article(row)
    return render_template(
        "admin/articulo_form.html",
        article=row,
        slide_list=parse_slides(row["slides"] if "slides" in row.keys() else ""),
        categories=CATEGORIES["es"],
    )


def _unique_slug(base: str, exclude_id: int | None) -> str:
    slug = slugify(base)
    n = 2
    while True:
        if exclude_id:
            exists = fetch_one("SELECT id FROM articles WHERE slug=? AND id!=?", (slug, exclude_id))
        else:
            exists = fetch_one("SELECT id FROM articles WHERE slug=?", (slug,))
        if not exists:
            return slug
        slug = f"{slugify(base)}-{n}"
        n += 1


def _save_article(existing):
    if not valid_csrf():
        abort(400)
    title = (request.form.get("title") or "").strip()
    if not title:
        flash("El artículo necesita un título.", "error")
        return render_template(
            "admin/articulo_form.html",
            article=existing,
            slide_list=parse_slides(existing["slides"] if existing and "slides" in existing.keys() else ""),
            categories=CATEGORIES["es"],
        )
    status = "published" if request.form.get("action") == "publish" else "draft"
    body = clean_html(request.form.get("body") or "")
    excerpt = (request.form.get("excerpt") or "").strip()[:400]
    category = (request.form.get("category") or "Consejos para familias")[:80]
    slug_src = (request.form.get("slug") or title).strip()
    slug = _unique_slug(slug_src, existing["id"] if existing else None)
    cover = (request.form.get("cover") or (existing["cover"] if existing else "")).strip() or "/static/img/characters-playroom.png"
    file = request.files.get("cover_file")
    if file and file.filename:
        saved = save_upload(file)
        if saved:
            cover = saved
    slides = parse_slides(existing["slides"] if existing and "slides" in existing.keys() else "")
    if request.form.get("replace_slides"):
        slides = []
    for slide in request.files.getlist("slides"):
        if slide and slide.filename:
            saved = save_upload(slide)
            if saved:
                slides.append(saved)
    if slides and (not cover or cover in {"/static/img/cover-casa.jpg", "/static/img/characters-playroom.png"}):
        cover = slides[0]
    slides_json = json.dumps(slides)
    now = utcnow()
    published_at = now if status == "published" else (existing["published_at"] if existing else None)
    if existing and existing["status"] == "published" and status == "published":
        published_at = existing["published_at"] or now
    if existing:
        execute(
            """UPDATE articles SET slug=?, title=?, excerpt=?, body=?, cover=?, category=?,
               status=?, updated_at=?, published_at=?, slides=? WHERE id=?""",
            (slug, title, excerpt, body, cover, category, status, now, published_at, slides_json, existing["id"]),
        )
        art_id = existing["id"]
    else:
        art_id = execute(
            """INSERT INTO articles(slug, title, excerpt, body, cover, category, status, created_at, updated_at, published_at, slides)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (slug, title, excerpt, body, cover, category, status, now, now, published_at, slides_json),
        )
    flash("Artículo publicado." if status == "published" else "Borrador guardado.", "ok")
    return redirect(url_for("admin_articulo_editar", art_id=art_id))


@app.post("/admin/articulos/<int:art_id>/borrar")
@login_required
def admin_articulo_borrar(art_id: int):
    if not valid_csrf():
        abort(400)
    execute("DELETE FROM articles WHERE id=?", (art_id,))
    flash("Artículo eliminado.", "ok")
    return redirect(url_for("admin_articulos"))


@app.post("/admin/subir")
@login_required
def admin_subir():
    if not valid_csrf():
        abort(400)
    file = request.files.get("file")
    if not file or not file.filename:
        return {"ok": False, "error": "No hay archivo"}, 400
    url = save_upload(file)
    if not url:
        return {"ok": False, "error": "Formato no permitido"}, 400
    return {"ok": True, "url": url}


def save_upload(file) -> str | None:
    name = secure_filename(file.filename)
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_IMG:
        return None
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    fname = f"{secrets.token_hex(8)}{ext}"
    dest = UPLOAD_DIR / fname
    file.save(dest)
    return f"/static/uploads/{fname}"


# ── Inbox ─────────────────────────────────────────────────────────────────


@app.post("/admin/citas/<int:req_id>/estado")
@login_required
def admin_cita_estado(req_id: int):
    if not valid_csrf():
        abort(400)
    status = (request.form.get("status") or "nueva")[:20]
    if status not in {"nueva", "contactada", "agendada", "cerrada"}:
        abort(400)
    execute("UPDATE appointment_requests SET status=? WHERE id=?", (status, req_id))
    return redirect(request.referrer or url_for("admin_home"))


@app.post("/admin/info/<int:req_id>/estado")
@login_required
def admin_info_estado(req_id: int):
    if not valid_csrf():
        abort(400)
    status = (request.form.get("status") or "nueva")[:20]
    if status not in {"nueva", "respondida", "cerrada"}:
        abort(400)
    execute("UPDATE info_requests SET status=? WHERE id=?", (status, req_id))
    return redirect(request.referrer or url_for("admin_home"))


@app.route("/admin/ajustes", methods=["GET", "POST"])
@login_required
def admin_ajustes():
    if request.method == "POST":
        if not valid_csrf():
            abort(400)
        for key in (
            "clinic_name", "legal_name", "tagline", "phone", "phone_digits",
            "email", "facebook", "instagram", "hours", "hormigueros_address",
            "hormigueros_maps", "anasco_address", "anasco_maps", "anasco_phone", "welcome",
            "welcome_en", "hormigueros_hours", "anasco_hours", "notify_email",
            "smtp_host", "smtp_port", "smtp_user", "smtp_pass",
        ):
            set_setting(key, (request.form.get(key) or "").strip())
        new_pw = request.form.get("new_password") or ""
        if new_pw:
            if len(new_pw) < 8:
                flash("La contraseña nueva debe tener al menos 8 caracteres.", "error")
            else:
                execute(
                    "UPDATE users SET password_hash=? WHERE id=?",
                    (generate_password_hash(new_pw), session["user_id"]),
                )
                flash("Contraseña actualizada.", "ok")
        flash("Datos de la clínica guardados.", "ok")
        return redirect(url_for("admin_ajustes"))
    return render_template("admin/ajustes.html")


@app.route("/admin/equipo", methods=["GET", "POST"])
@login_required
def admin_equipo():
    if request.method == "POST":
        if not valid_csrf():
            abort(400)
        if request.form.get("delete_id"):
            execute("DELETE FROM team WHERE id=?", (int(request.form["delete_id"]),))
        else:
            name = (request.form.get("name") or "").strip()
            if name:
                execute(
                    "INSERT INTO team(name, credential, sort, visible) VALUES(?,?,?,1)",
                    (name[:120], (request.form.get("credential") or "")[:80], int(request.form.get("sort") or 0)),
                )
        return redirect(url_for("admin_equipo"))
    rows = fetch_all("SELECT * FROM team ORDER BY sort, name")
    return render_template("admin/lista.html", title="Equipo", kind="equipo", rows=rows)


@app.route("/admin/talleres", methods=["GET", "POST"])
@login_required
def admin_talleres():
    if request.method == "POST":
        if not valid_csrf():
            abort(400)
        if request.form.get("delete_id"):
            execute("DELETE FROM events WHERE id=?", (int(request.form["delete_id"]),))
        else:
            title = (request.form.get("title") or "").strip()
            if title:
                execute(
                    """INSERT INTO events(title, title_en, when_at, place, notes, notes_en, created_at)
                       VALUES(?,?,?,?,?,?,?)""",
                    (
                        title[:160],
                        (request.form.get("title_en") or "")[:160],
                        (request.form.get("when_at") or "")[:80],
                        (request.form.get("place") or "")[:80],
                        (request.form.get("notes") or "")[:500],
                        (request.form.get("notes_en") or "")[:500],
                        utcnow(),
                    ),
                )
        return redirect(url_for("admin_talleres"))
    rows = fetch_all("SELECT * FROM events ORDER BY id DESC")
    return render_template("admin/lista.html", title="Talleres", kind="talleres", rows=rows)


@app.route("/admin/testimonios", methods=["GET", "POST"])
@login_required
def admin_testimonios():
    if request.method == "POST":
        if not valid_csrf():
            abort(400)
        if request.form.get("delete_id"):
            execute("DELETE FROM quotes WHERE id=?", (int(request.form["delete_id"]),))
        else:
            quote = (request.form.get("quote") or "").strip()
            if quote:
                execute(
                    "INSERT INTO quotes(quote, quote_en, who, visible, sort) VALUES(?,?,?,1,0)",
                    (quote[:500], (request.form.get("quote_en") or "")[:500], (request.form.get("who") or "")[:80]),
                )
        return redirect(url_for("admin_testimonios"))
    rows = fetch_all("SELECT * FROM quotes ORDER BY sort, id")
    return render_template("admin/lista.html", title="Testimonios", kind="testimonios", rows=rows)


@app.get("/uploads/<path:name>")
def uploaded(name: str):
    return send_from_directory(UPLOAD_DIR, name)


def create_app():
    init_db()
    seed()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5055"))
    print(f"\n  Speech R' Us — sitio público")
    print(f"  http://127.0.0.1:{port}")
    print(f"  Panel: http://127.0.0.1:{port}/admin/entrar")
    print(f"  Usuario: admin   Contraseña inicial: CambiaEsto123\n")
    app.run(host="127.0.0.1", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
