"""Default clinic data and sample articles — idempotent."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from werkzeug.security import generate_password_hash

from db import execute, fetch_one, set_setting

DEFAULT_SETTINGS = {
    "clinic_name": "Speech R' Us",
    "legal_name": "Speech R' Us Corp.",
    "tagline": "Centro de Terapias Integradas",
    "phone": "(787) 423-2481",
    "phone_digits": "17874232481",
    "anasco_phone": "(939) 228-7905",
    "email": "info.sru@centroterapiasintegradas.com",
    "facebook": "https://www.facebook.com/speechrusterapias/",
    "instagram": "https://www.instagram.com/speechrusterapias/",
    "hours": "Lunes a viernes, 8:00 a. m. – 5:00 p. m.",
    "hormigueros_address": "Plaza Monserrate II, Local 5-6, Hormigueros, Puerto Rico",
    "hormigueros_maps": "https://www.google.com/maps/place/Speech+R+Us/@18.132238,-67.1132475,17z/data=!4m6!3m5!1s0x8c1d4d001f68168f:0xd17b49a95652873a!8m2!3d18.132238!4d-67.1132475!16s%2Fg%2F11m6s28l3g",
    "anasco_address": "Carr. 2, Edificio Bianca, primer piso, Suite 102, Añasco, Puerto Rico",
    "anasco_maps": "https://www.google.com/maps/search/?api=1&query=18.30177351403001,-67.15730632472926",
    "sanjuan_note": "",
    "welcome": (
        "Acompañamos a niños y sus familias, del área oeste en su desarrollo según su necesidad. "
        "Jugamos en cada sesión y nos tomamos en serio el plan. "
        "¡El bienestar de tu peque es nuestra prioridad!"
    ),
    "welcome_en": (
        "We walk with children and families in Hormigueros and Añasco. "
        "We play in session and take the plan seriously."
    ),
    "hormigueros_hours": "Monday–Friday, 8:00 a.m. – 5:00 p.m.",
    "anasco_hours": "Monday–Friday, 8:00 a.m. – 5:00 p.m.",
    "notify_email": "info.sru@centroterapiasintegradas.com",
    "smtp_host": "",
    "smtp_port": "587",
    "smtp_user": "",
    "smtp_pass": "",
}

ARTICLES = [
    {
        "slug": "terapia-de-habla-y-lenguaje",
        "title": "Terapia de habla y lenguaje",
        "excerpt": "Post de la clínica: qué es la terapia, qué conviene saber y cuándo pedir orientación.",
        "category": "Habla y lenguaje",
        "cover": "/static/img/brand/habla-1.png",
        "slides": '["/static/img/brand/habla-1.png","/static/img/brand/habla-2.png","/static/img/brand/habla-3.png","/static/img/brand/habla-4.png","/static/img/brand/habla-5.png"]',
        "body": """
<p>Las láminas de arriba son el post. Si algo de esas señales te suena, pide cita o llama: no hay que esperar a que empeore.</p>
""",
    },

    {
        "slug": "senales-de-que-tu-hijo-puede-necesitar-terapia-del-habla",
        "title": "Señales de que tu hijo puede beneficiarse de terapia del habla",
        "excerpt": "Una guía clara para mamás y papás: qué observar en casa, en la escuela y cuándo pedir una evaluación.",
        "category": "Habla y lenguaje",
        "cover": "/static/img/cover-senales.jpg",
        "body": """
<p>Cada nene tiene su ritmo. Aun así, hay señales que vale la pena no dejar pasar. Pedir una evaluación no etiqueta a tu hijo: te da un mapa.</p>
<h2>En el lenguaje</h2>
<ul>
<li>A los 18 meses dice pocas palabras o no combina gestos con sonido.</li>
<li>A los 2 años no junta dos palabras (“más agua”, “mamá ven”).</li>
<li>A los 3 años personas fuera de la familia no le entienden.</li>
<li>Se frustra, señala o llora en vez de pedir lo que quiere.</li>
</ul>
<h2>En el habla</h2>
<ul>
<li>Omite sonidos, cambia letras o se “traba” al empezar.</li>
<li>La voz se oye ronca, nasal o muy suave con frecuencia.</li>
<li>Le cuesta imitar sonidos, canciones o rimas.</li>
</ul>
<h2>Qué hacer ahora</h2>
<p>Anota ejemplos concretos (qué dijo, cuándo, con quién). Trae esa lista a la evaluación. En Speech R' Us empezamos escuchándoles a ustedes: nadie conoce a su hijo mejor que su familia.</p>
<blockquote>Una evaluación a tiempo abre puertas. Esperar “a ver si se le quita” a veces cierra las que más importan.</blockquote>
<p>Si algo de esta lista te suena familiar, pide cita. No hay pregunta pequeña cuando se trata de la voz de tu hijo.</p>
""",
    },
    {
        "slug": "como-estimular-el-lenguaje-en-casa",
        "title": "Cómo estimular el lenguaje en casa, sin convertir el juego en tarea",
        "excerpt": "Cinco rutinas cortas —baño, comida, cuento, carro y cocina— que multiplican las palabras del día a día.",
        "category": "Consejos para familias",
        "cover": "/static/img/cover-casa.jpg",
        "body": """
<p>El lenguaje no crece en un escritorio. Crece en el baño, en el carro y en la mesa. Estas rutinas caben en la vida real de una familia boricua.</p>
<h2>1. Narrar lo que ya hacen</h2>
<p>En vez de interrogar (“¿qué es esto?”), describe: “Estás echando agua. El jabón hace burbujas. ¡Qué frío!”. El nene oye el modelo completo.</p>
<h2>2. Esperar de verdad</h2>
<p>Haz una pregunta o un comentario y cuenta hasta cinco en silencio. Esa pausa es oro: le da tiempo a organizar la palabra.</p>
<h2>3. Un cuento, una noche</h2>
<p>Cinco minutos. Señala, nombra, deja que él pase la página. No hay que terminar el libro. El ritual importa más que la trama.</p>
<h2>4. Cocinar juntos</h2>
<p>Plátano, arroz, agua, caliente, más, ya. La cocina es un diccionario con olor. Dale un rol pequeño: echar, revolver, decir “listo”.</p>
<h2>5. Menos pantalla, más turno</h2>
<p>El lenguaje es un partido de ida y vuelta. Si la tele habla todo el rato, el nene no tiene turno. Apaga, siéntate al lado, juega 10 minutos a lo que él elija.</p>
<p>Si quieres un plan a la medida de tu hijo, escríbenos. Llevamos lo que funciona en sesión y te lo traducimos a la casa.</p>
""",
    },
    {
        "slug": "que-esperar-en-la-primera-evaluacion",
        "title": "Qué esperar en la primera evaluación",
        "excerpt": "Paso a paso: papeles, juego, conversación con la familia y el informe. Sin sorpresas.",
        "category": "La clínica",
        "cover": "/static/img/cover-eval.jpg",
        "body": """
<p>La primera visita no es un examen escolar. Es una conversación larga con juego en el medio. Así suele fluir en Speech R' Us.</p>
<h2>Antes de llegar</h2>
<p>Trae el plan médico si aplica, referidos, evaluaciones previas y una lista de lo que te preocupa. Si el nene usa chupete, tableta o tiene una rutina de sueño complicada, dilo: todo cuenta.</p>
<h2>Durante la cita</h2>
<ul>
<li>Hablamos con ustedes primero: historia, escuela, casa, lo que ya intentaron.</li>
<li>Luego jugamos. Observamos cómo se comunica, come, se mueve y se regula.</li>
<li>No forzamos. Si hoy no hay cooperación, igual salimos con información útil.</li>
</ul>
<h2>Después</h2>
<p>Recibes orientación clara: si hay que tratar, con qué frecuencia, qué pueden hacer en casa y cómo se coordina con la escuela o el pediatra.</p>
<blockquote>Ustedes no están “entregando” a su hijo. Están sentándose al lado del equipo.</blockquote>
<p>¿Listos para el primer paso? Pidan la cita desde esta página o llámennos. Les confirmamos horario en Hormigueros o Añasco.</p>
""",
    },
    {
        "slug": "apraxia-verbal-de-la-ninez",
        "author": "Mirelis Arocho Salgado",
        "title": "Apraxia verbal de la niñez",
        "excerpt": "Qué es la apraxia del habla infantil, qué se observa y cómo se trata con enfoques como DTTC. Del blog de Speech R' Us.",
        "category": "Habla y lenguaje",
        "cover": "/static/img/cover-apraxia.jpg",
        "published_at": "2025-02-03 00:00:00",
        "body": """
<p>La apraxia del habla infantil, también conocida como apraxia verbal de la niñez (AVN), es un trastorno neurológico motor que afecta la planificación y programación de los movimientos necesarios para hablar. Aunque los niños con AVN saben lo que quieren decir, su cerebro tiene dificultades para coordinar los movimientos musculares del habla, lo que provoca errores en la producción de sonidos, sílabas y palabras.</p>
<h2>Características</h2>
<ul>
<li>Inconsistencia en la producción de palabras: un mismo término puede pronunciarse de manera diferente en distintas ocasiones.</li>
<li>Dificultades con transiciones suaves entre sonidos y sílabas.</li>
<li>Producción lenta y laboriosa del habla.</li>
<li>Errores en la prosodia, como patrones atípicos de acentuación y entonación.</li>
<li>Mayor dificultad con palabras más largas o complejas.</li>
</ul>
<h2>La investigación de Edythe Strand</h2>
<p>La Dra. Edythe Strand ha desarrollado el enfoque DTTC (Dynamic Temporal and Tactile Cueing). Según sus investigaciones, la AVN es un trastorno de planificación motora que requiere repetición, retroalimentación multisensorial y práctica sistemática de movimientos del habla.</p>
<ul>
<li>La intervención se centra en secuencias de sonidos y palabras funcionales.</li>
<li>Las claves visuales y táctiles mejoran la precisión.</li>
<li>La terapia se adapta al nivel de cada niño, aumentando la complejidad poco a poco.</li>
</ul>
<h2>Tratamiento</h2>
<p>El método DTTC implica modelado y apoyo táctil, repetición con variabilidad, y retroalimentación inmediata. La detección temprana y una intervención intensiva son claves. Si sospechas dificultades en la producción del habla, pide una evaluación con un patólogo del habla-lenguaje.</p>
<p>Publicado originalmente en el blog de Speech R' Us por Mirelis Arocho Salgado.</p>
""",
    },
    {
        "slug": "maneras-de-estimular-el-habla-lenguaje-en-ninos",
        "author": "Mirelis Arocho Salgado",
        "title": "Maneras de estimular el habla y el lenguaje en niños",
        "excerpt": "Ocho trucos de casa para incentivar que el niño pida con gesto, sonido o palabra — del blog de la clínica.",
        "category": "Consejos para familias",
        "cover": "/static/img/blog/estimular.jpg",
        "published_at": "2020-04-25 00:00:00",
        "body": """
<p>Muchos padres se preguntan: “¿Qué puedo hacer para ayudar o estimular a mi hijo a hablar?”. La comunicación es una necesidad. Muchos niños solo necesitan un incentivo para comenzar a comunicarse con palabras: comprender que el habla sirve para conseguir lo que quieren.</p>
<ol>
<li>Come algo que le guste, en su presencia, sin ofrecerle. Cuando indique que quiere, modela un gesto, palabra o frase simple y espera a que imite. Si no imita, ayúdalo a producirla y luego dale un poco.</li>
<li>Usa el juguete preferido sin compartirlo de entrada. Modela /p/ para “por favor”, /h/ para “jugar”, o una frase como “jugar, por favor” si ya tiene palabras.</li>
<li>En la comida, da porciones pequeñas y espera a que pida más. Modela la seña de “más” o el sonido /m/.</li>
<li>Limita un poco el acceso a televisión, juguetes o el patio, de modo que necesite pedir ayuda. Objetos favoritos un poco más altos o cerrados invitan a comunicar.</li>
<li>Juegos de toma de turnos: rodar la bola, empujar un carrito. Retén el juguete un momento y espera. Si no pide, modela la palabra o el sonido inicial.</li>
<li>Contenedores con tapa apretada. Cuando quiera una galleta, dale el envase cerrado. Al devolvértelo, que pida ayuda.</li>
<li>Juguetes difíciles de operar. Úsalos varias veces, entréaselos y espera a que pida ayuda con palabras o intentos de palabras.</li>
</ol>
<p>Estos trucos enseñan el poder de la comunicación: suele funcionar más rápido que llorar. La recompensa tiene que ser inmediata, para que conecte causa y efecto. Si señala y gruñe o hace perreta, explica que no comprendes (aunque sepas lo que quiere) y modela la manera de pedir.</p>
<p>Publicado originalmente en el blog de Speech R' Us por Mirelis Arocho Salgado.</p>
""",
    },
    {
        "slug": "desorden-de-procesamiento-auditivo",
        "author": "Mirelis Arocho Salgado",
        "title": "Desorden de procesamiento auditivo",
        "excerpt": "Qué se observa cuando el oído oye bien pero el cerebro no interpreta el sonido como debería.",
        "category": "Habla y lenguaje",
        "cover": "/static/img/blog/procesamiento.jpg",
        "published_at": "2020-04-25 00:00:00",
        "body": """
<p>La manera más fácil de comunicarnos es el habla: uno emite una pregunta y espera una respuesta coherente. Eso ocurre porque el oyente interpreta lo que oyó. El procesamiento central auditivo es cómo el cerebro interpreta las señales acústicas que llegan a los oídos. El oído convierte el sonido en movimiento, luego en impulsos nerviosos. Lo que el cerebro hace con esos impulsos se llama procesamiento auditivo.</p>
<p>Cuando hay dificultad en esa área se habla de desorden de procesamiento central auditivo. En niños se puede observar:</p>
<ul>
<li>Dificultad para poner atención y recordar información presentada de forma oral</li>
<li>Audición periférica normal</li>
<li>Problemas para seguir instrucciones de varios pasos</li>
<li>Necesidad de más tiempo para procesar</li>
<li>Desempeño académico bajo o problemas de comportamiento</li>
<li>Dificultades de lenguaje (secuencias de sílabas, vocabulario, comprensión)</li>
<li>Dificultad con lectura, comprensión, deletreo y vocabulario</li>
</ul>
<p>Puede ir acompañado de autismo o ADHD, o presentarse solo, y se confunde con otros problemas. Para determinarlo hace falta una evaluación audiológica (que el oído funcione bien) y luego una evaluación de procesamiento auditivo, también con audiólogo. El patólogo del habla-lenguaje determina hasta qué punto la persona entiende y usa el lenguaje.</p>
<p>Si sospechas esta dificultad, contacta a un audiólogo o a un patólogo del habla-lenguaje.</p>
<p>Publicado originalmente en el blog de Speech R' Us por Mirelis Arocho Salgado.</p>
""",
    },
    {
        "slug": "desarrollo-tipico-del-habla-lenguaje",
        "author": "Mirelis Arocho Salgado",
        "title": "Desarrollo típico del habla y el lenguaje",
        "excerpt": "Hitos de comunicación, mes a mes y año a año, para orientarse — no para comparar. Fuente: Linguisystems, Inc.",
        "category": "Habla y lenguaje",
        "cover": "/static/img/blog/desarrollo.jpg",
        "published_at": "2020-04-25 00:00:00",
        "body": """
<p>Lista de puntos importantes en el desarrollo de la comunicación, adaptada de Linguisystems, Inc. Cada niño tiene su ritmo; esto orienta, no etiqueta.</p>
<h2>3–6 meses</h2>
<ul>
<li>Sonríe espontáneamente al contacto humano y al jugar solo</li>
<li>Sonríe a caras de la familia</li>
<li>Deja de llorar cuando le hablan</li>
<li>Muestra respuestas distintas a distintas personas</li>
</ul>
<h2>6–9 meses</h2>
<ul>
<li>Responde a “ven acá”</li>
<li>Se vuelve más activo con personas familiares</li>
<li>Muestra ansiedad al separarse de su encargado</li>
</ul>
<h2>9–12 meses</h2>
<ul>
<li>Reacciona al humor de otras personas</li>
<li>Puede temer a extraños</li>
<li>Busca atención de las personas alrededor</li>
</ul>
<h2>12–18 meses</h2>
<ul>
<li>Vocabulario expresivo de unas 5–20 palabras</li>
<li>Sigue mandatos simples, sobre todo con gestos</li>
<li>Practica la entonación imitando a los adultos</li>
<li>Combina nombres con palabras como arriba, abajo, dame</li>
</ul>
<h2>19–24 meses</h2>
<ul>
<li>Nombra objetos comunes</li>
<li>Usa preposiciones como en, a, con</li>
<li>Estructura “sustantivo + verbo”</li>
<li>La familia comprende aproximadamente 2/3 del habla</li>
<li>Vocabulario receptivo de unas 150–300 palabras</li>
<li>Sigue mandatos como “enséñame tu nariz”</li>
</ul>
<h2>25–36 meses</h2>
<ul>
<li>Usa yo y tú correctamente</li>
<li>Algunos plurales y pasado</li>
<li>Oraciones de tres palabras; unas 900 palabras</li>
<li>La familia comprende cerca del 90%</li>
<li>Cuenta experiencias; da nombre, edad y género</li>
</ul>
<h2>4 años</h2>
<ul>
<li>Al menos 4 preposiciones; conoce colores</li>
<li>Puede repetir 4 dígitos y palabras de 4 sílabas</li>
<li>Habla mucho en el juego; inventa historias</li>
</ul>
<h2>5 años</h2>
<ul>
<li>Adjetivos y adverbios en conversación; opuestos</li>
<li>Cuenta hasta 10</li>
<li>Habla inteligible, con posibles errores articulatorios</li>
<li>Sigue mandatos de 3 pasos; conceptos simples de tiempo</li>
</ul>
<p>Si algo de esta lista te preocupa en tu hijo, pide una evaluación. Publicado originalmente en el blog de Speech R' Us por Mirelis Arocho Salgado.</p>
""",
    },
]


def seed() -> None:
    for key, value in DEFAULT_SETTINGS.items():
        if fetch_one("SELECT key FROM settings WHERE key=?", (key,)) is None:
            set_setting(key, value)

    # Copy from the old site if we still have the first generated welcome.
    current = fetch_one("SELECT value FROM settings WHERE key='welcome'")
    if current and (
        current["value"].startswith("En Speech R' Us acompañamos a niñas")
        or "adultos" in current["value"]
        or "Patología del habla y lenguaje, terapia ocupacional" in current["value"]
        or current["value"] == (
            "Acompañamos a niños y familias en Hormigueros y Añasco. "
            "Jugamos en sesión y nos tomamos en serio el plan."
        )
    ):
        set_setting("welcome", DEFAULT_SETTINGS["welcome"])
    mail = fetch_one("SELECT value FROM settings WHERE key='email'")
    if mail and mail["value"] in ("centrospeechrus@yahoo.com", "", None):
        set_setting("email", DEFAULT_SETTINGS["email"])
    art = fetch_one("SELECT id, body FROM articles WHERE slug=?", ("terapia-de-habla-y-lenguaje",))
    if art and "Qué debes saber" in (art["body"] or ""):
        execute(
            "UPDATE articles SET excerpt=?, body=? WHERE slug=?",
            (
                "Post de la clínica: qué es la terapia, qué conviene saber y cuándo pedir orientación.",
                "<p>Las láminas de arriba son el post. Si algo de esas señales te suena, pide cita o llama: no hay que esperar a que empeore.</p>",
                "terapia-de-habla-y-lenguaje",
            ),
        )
    anasco = fetch_one("SELECT value FROM settings WHERE key='anasco_address'")
    if anasco and anasco["value"] in ("Añasco, Puerto Rico", "Añasco, Puerto Rico "):
        set_setting("anasco_address", DEFAULT_SETTINGS["anasco_address"])

    if fetch_one("SELECT id FROM users LIMIT 1") is None:
        execute(
            "INSERT INTO users(username, password_hash, name) VALUES(?,?,?)",
            (
                "admin",
                generate_password_hash(os.environ.get("INITIAL_ADMIN_PASSWORD", "CambiaEsto123")),
                "Administradora",
            ),
        )

    TEAM = [
        ("Mirelis Arocho Salgado", "MS, CCC-SLP"),
        ("Coralys Vélez", "MS, CCC-SLP"),
        ("Luis O. Díaz", "MS, CCC-SLP"),
        ("Denitza Tejada", "SLP"),
        ("Winedys Caraballo", "SLP"),
        ("Jeannette Rodríguez", "BS, THL"),
        ("Ashley Echevarría", "BS, THL"),
        ("Paola Muñoz", "BS, THL"),
        ("Thaís Huertas", "THL"),
        ("Jorealys Valentín", "THL"),
        ("Pamela Cancel", "THL"),
        ("Khiara Rivera", "THL"),
        ("Grissheina Martínez", "THL"),
        ("Fabiola Berrocal", "THL"),
        ("Andrea García", "OTR/L"),
        ("Dra. Rocío Martínez", "Psy.D"),
        ("Elba Méndez Barrios", "Psy.D"),
        ("Mayra Pagán", "MS, PSY"),
        ("Keishla M. Sanabria", "Oficial administrativo"),
        ("Nathan R. Lugo", "Oficial administrativo"),
    ]
    if fetch_one("SELECT id FROM team LIMIT 1") is None:
        for i, (name, cred) in enumerate(TEAM):
            execute("INSERT INTO team(name, credential, sort, visible) VALUES(?,?,?,1)", (name, cred, i))

    if fetch_one("SELECT id FROM quotes LIMIT 1") is None:
        execute(
            "INSERT INTO quotes(quote, quote_en, who, visible, sort) VALUES(?,?,?,1,0)",
            (
                "Por primera vez entendí qué podía hacer en casa, no solo en la clínica.",
                "For the first time I understood what I could do at home, not only at the clinic.",
                "Mamá de L.",
            ),
        )
        execute(
            "INSERT INTO quotes(quote, quote_en, who, visible, sort) VALUES(?,?,?,1,1)",
            (
                "Llegamos asustados. Se fueron con un plan y con calma.",
                "We arrived scared. We left with a plan and with calm.",
                "Papá de M.",
            ),
        )
        execute(
            "INSERT INTO quotes(quote, quote_en, who, visible, sort) VALUES(?,?,?,1,2)",
            (
                "El equipo se habla. Eso se nota en mi nene.",
                "The team talks to each other. You can tell in my boy.",
                "Mamá de A.",
            ),
        )

    if fetch_one("SELECT id FROM events LIMIT 1") is None:
        execute(
            """INSERT INTO events(title, title_en, when_at, place, notes, notes_en, created_at)
               VALUES(?,?,?,?,?,?,?)""",
            (
                "Orientación para familias: lenguaje en casa",
                "Family orientation: language at home",
                "Próxima fecha por confirmar",
                "Hormigueros",
                "Taller corto para papás. Cupo limitado. Llama para reservar.",
                "A short workshop for parents. Limited seats. Call to reserve.",
                datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

    execute(
        """UPDATE articles SET title_en=?, excerpt_en=?, body_en=?, category_en=?, cover_en=?
           WHERE slug=? AND (title_en='' OR title_en IS NULL)""",
        (
            "Childhood apraxia of speech",
            "What childhood apraxia is, what you may see, and how it is treated with approaches such as DTTC.",
            "<p>Childhood apraxia of speech is a motor planning disorder. The child knows what they want to say; the brain has trouble sequencing the movements. Early, intensive help matters.</p>",
            "Speech and language",
            "/static/img/cover-apraxia.jpg",
            "apraxia-verbal-de-la-ninez",
        ),
    )
    execute(
        """UPDATE articles SET title_en=?, excerpt_en=?, body_en=?, category_en=?, cover_en=?
           WHERE slug=? AND (title_en='' OR title_en IS NULL)""",
        (
            "Ways to spark speech and language at home",
            "Eight home tricks so a child asks with a gesture, a sound, or a word.",
            "<p>Language grows in the bathroom, the car, and the kitchen. Pause, model, and wait. Reward the attempt right away.</p>",
            "Tips for families",
            "/static/img/blog/estimular.jpg",
            "maneras-de-estimular-el-habla-lenguaje-en-ninos",
        ),
    )
    execute(
        """UPDATE articles SET title_en=?, excerpt_en=?, body_en=?, category_en=?, cover_en=?
           WHERE slug=? AND (title_en='' OR title_en IS NULL)""",
        (
            "Auditory processing disorder",
            "When the ear hears well but the brain does not interpret sound as it should.",
            "<p>Central auditory processing is how the brain makes sense of what the ears send. If that path is hard, a child may follow directions poorly even with normal hearing. An audiologist and a speech-language pathologist work together.</p>",
            "Speech and language",
            "/static/img/blog/procesamiento-en.svg",
            "desorden-de-procesamiento-auditivo",
        ),
    )
    execute(
        """UPDATE articles SET title_en=?, excerpt_en=?, body_en=?, category_en=?, cover_en=?
           WHERE slug=? AND (title_en='' OR title_en IS NULL)""",
        (
            "Typical speech and language development",
            "Milestones month by month and year by year — a map, not a race.",
            "<p>Every child has a pace. These milestones, adapted from Linguisystems, help you notice when a conversation with the clinic is worth having.</p>",
            "Speech and language",
            "/static/img/blog/desarrollo.jpg",
            "desarrollo-tipico-del-habla-lenguaje",
        ),
    )
    execute(
        """UPDATE articles SET title_en=?, excerpt_en=?, body_en=?, category_en=?
           WHERE slug=? AND (title_en='' OR title_en IS NULL)""",
        (
            "Speech and language therapy",
            "Clinic post: what therapy is, what to know, and when to ask.",
            "<p>The slides above are the post. If any of those signs sound like home, request a visit.</p>",
            "Speech and language",
            "terapia-de-habla-y-lenguaje",
        ),
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    blog_meta = {
        "apraxia-verbal-de-la-ninez": ("Mirelis Arocho Salgado", "/static/img/cover-apraxia.jpg"),
        "maneras-de-estimular-el-habla-lenguaje-en-ninos": ("Mirelis Arocho Salgado", "/static/img/blog/estimular.jpg"),
        "desorden-de-procesamiento-auditivo": ("Mirelis Arocho Salgado", "/static/img/blog/procesamiento.jpg"),
        "desarrollo-tipico-del-habla-lenguaje": ("Mirelis Arocho Salgado", "/static/img/blog/desarrollo.jpg"),
    }
    for slug, (author, cover) in blog_meta.items():
        execute("UPDATE articles SET author=?, cover=? WHERE slug=?", (author, cover, slug))
    for art in ARTICLES:
        if fetch_one("SELECT id FROM articles WHERE slug=?", (art["slug"],)):
            continue
        published = art.get("published_at") or now
        slides = art.get("slides") or "[]"
        execute(
            """INSERT INTO articles(slug, title, excerpt, body, cover, category, status, created_at, updated_at, published_at, slides, author)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                art["slug"],
                art["title"],
                art["excerpt"],
                art["body"].strip(),
                art["cover"],
                art["category"],
                "published",
                published,
                now,
                published,
                slides,
                art.get("author") or "",
            ),
        )
