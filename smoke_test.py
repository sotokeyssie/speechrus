"""End-to-end smoke checks against a running site or the Flask test client."""
from __future__ import annotations

import sys

from app import app


def main() -> int:
    client = app.test_client()
    fails = []

    def check(name, cond, detail=""):
        if cond:
            print(f"  ok  {name}")
        else:
            print(f" FAIL {name} {detail}")
            fails.append(name)

    home = client.get("/")
    check("GET /", home.status_code == 200 and "Cada voz merece ser escuchada" in home.text)
    check("logo on home", "/static/img/logo.jpg" in home.text)
    check("phone on home", "423-2481" in home.text)

    for path, needle in [
        ("/servicios", "Patología del habla y lenguaje"),
        ("/nosotros", "Hormigueros"),
        ("/articulos", "Señales de que tu hijo"),
        ("/cita", "Enviar pedido de cita"),
        ("/contacto", "Tu pregunta"),
        ("/privacidad", "HIPAA"),
    ]:
        r = client.get(path)
        check(f"GET {path}", r.status_code == 200 and needle in r.text, f"status={r.status_code}")

    art = client.get("/articulos/como-estimular-el-lenguaje-en-casa")
    check("article page", art.status_code == 200 and "Narrar lo que ya hacen" in art.text)

    # appointment
    r = client.get("/cita")
    csrf = r.text.split('name="csrf" value="')[1].split('"')[0]
    posted = client.post(
        "/cita",
        data={
            "csrf": csrf,
            "parent_name": "María Pérez",
            "child_name": "Lucas",
            "child_age": "4 años",
            "phone": "787-555-0101",
            "email": "maria@example.com",
            "clinic": "Hormigueros",
            "service": "Habla y lenguaje",
            "preferred": "tardes",
            "notes": "Le cuesta pedir agua",
            "website": "",
        },
        follow_redirects=True,
    )
    check("cita form", posted.status_code == 200 and "bandeja" in posted.text.lower())

    r = client.get("/contacto")
    csrf = r.text.split('name="csrf" value="')[1].split('"')[0]
    posted = client.post(
        "/contacto",
        data={
            "csrf": csrf,
            "name": "José",
            "phone": "787-555-0102",
            "email": "jose@example.com",
            "topic": "Planes médicos",
            "message": "¿Aceptan Triple-S?",
            "website": "",
        },
        follow_redirects=True,
    )
    check("info form", posted.status_code == 200 and "contestamos" in posted.text.lower())

    # admin
    login_page = client.get("/admin/entrar")
    csrf = login_page.text.split('name="csrf" value="')[1].split('"')[0]
    bad = client.post("/admin/entrar", data={"csrf": csrf, "username": "admin", "password": "wrong"})
    check("bad login rejected", bad.status_code == 200 and "incorrectos" in bad.text)

    login_page = client.get("/admin/entrar")
    csrf = login_page.text.split('name="csrf" value="')[1].split('"')[0]
    ok = client.post(
        "/admin/entrar",
        data={"csrf": csrf, "username": "admin", "password": "CambiaEsto123"},
        follow_redirects=True,
    )
    check("admin login", ok.status_code == 200 and "Escribir un artículo" in ok.text)
    check("inbox shows cita", "María Pérez" in ok.text)
    check("inbox shows pregunta", "Triple-S" in ok.text)

    nuevo = client.get("/admin/articulos/nuevo")
    check("editor page", nuevo.status_code == 200 and "Publicar en la página" in nuevo.text)
    csrf = nuevo.text.split('name="csrf" value="')[1].split('"')[0]
    saved = client.post(
        "/admin/articulos/nuevo",
        data={
            "csrf": csrf,
            "title": "Jugar con burbujas para el soplo",
            "excerpt": "Un juego de baño que trabaja soplo y turnos.",
            "category": "Consejos para familias",
            "body": "<p>Enciende la ducha, sopla y espera el turno del nene.</p>",
            "action": "publish",
        },
        follow_redirects=True,
    )
    check("publish article", saved.status_code == 200 and "publicado" in saved.text.lower())
    live = client.get("/articulos/jugar-con-burbujas-para-el-soplo")
    check("new article live", live.status_code == 200 and "soplo" in live.text)

    if fails:
        print(f"\n{len(fails)} failed")
        return 1
    print("\nall smoke checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
