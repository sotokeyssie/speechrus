# Speech R' Us — sitio público

Página de la clínica para familias: servicios, pedir cita, hacer preguntas y artículos que se publican desde un panel sencillo.

No es el expediente clínico. Las citas que llegan aquí son **solicitudes**; se confirman por teléfono o WhatsApp.

## Arrancar en el PC

Doble clic en `iniciar.bat`, o:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abre [http://127.0.0.1:5055](http://127.0.0.1:5055)

## Panel para publicar artículos

[http://127.0.0.1:5055/admin/entrar](http://127.0.0.1:5055/admin/entrar)

| | |
|---|---|
| Usuario | `admin` |
| Contraseña inicial | `CambiaEsto123` |

Cámbiala en **Ajustes** la primera vez.

Desde el panel se puede:

- Escribir un artículo (título, resumen, foto, texto con negritas y listas) y **Publicar en la página**
- Ver las citas y preguntas que llegan por la web, marcarlas y llamar o abrir WhatsApp
- Cambiar teléfono, horario y direcciones

## Datos de la clínica (por defecto)

Tomados de los formularios oficiales del centro:

- Speech R' Us Corp., Plaza Monserrate II, Local 5-6, Hormigueros
- (787) 423-2481 · info.sru@centroterapiasintegradas.com
- Facebook: [speechrusterapias](https://www.facebook.com/speechrusterapias/)
- Instagram: [speechrusterapias](https://www.instagram.com/speechrusterapias/)
- Añasco: Carr. 2, Edificio Bianca, primer piso, Suite 102 · (939) 228-7905

## Publicar gratis en Render

El proyecto incluye `render.yaml`, por lo que puede publicarse como un Blueprint:

1. Sube esta carpeta a un repositorio privado de GitHub.
2. En Render, selecciona **New > Blueprint** y conecta el repositorio.
3. Cuando Render lo solicite, define `INITIAL_ADMIN_PASSWORD` con una contraseña privada y segura.
4. Confirma el servicio gratuito y espera a que termine el despliegue.

Render genera `SECRET_KEY` automáticamente y ejecuta el sitio con Gunicorn. En el plan gratuito,
el servicio puede tardar cerca de un minuto en despertar después de 15 minutos sin visitas.

El sitio utiliza SQLite (`data/site.db`). Su contenido inicial se reconstruye automáticamente,
pero las solicitudes, los cambios del panel y las imágenes subidas durante una sesión pueden
perderse cuando Render reinicie el servicio gratuito. Para una presentación funciona bien; para
uso diario se debe conectar almacenamiento persistente antes de recibir datos reales de familias.

## Presentación estática en GitHub Pages

`tools/export_github_pages.ps1` crea una copia para demostración dentro de `docs/`. Conserva las
páginas, artículos, imágenes, animaciones y el cursor. GitHub Pages no ejecuta Python ni SQLite,
por lo que los formularios abren WhatsApp y el panel administrativo no está disponible allí.
