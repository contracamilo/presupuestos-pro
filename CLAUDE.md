# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**PresupuestosPro**: app web autoalojada para que autónomos en España creen presupuestos con IVA/IRPF según tipo de cliente y los descarguen en PDF.

## Stack (decisiones vigentes, de specs/*/plan.md)
- Python 3.12, FastAPI + Uvicorn, Jinja2 (HTML en servidor) + HTMX local y un `app.js` mínimo. Sin SPA, sin build step.
- SQLite de la stdlib (`sqlite3`, **sin ORM ni migraciones**; WAL; `PRAGMA user_version` = 2, la subida de esquema es automática al arrancar). Una sola instancia de la app.
- PDF con WeasyPrint 70, sin acceso a red (solo recursos `data:`). Contraseñas con argon2-cffi (Argon2id), sesiones en la BD.
- Estilo: un único `presupuestos/static/tokens.css` (paleta, escalas) compartido por app y PDF; Inter incluida localmente. Sin frameworks CSS. WCAG 2.1 AA.
- Despliegue: Docker Compose + Caddy (HTTPS automático) + copias diarias con rclone.
- Arquitectura: `dominio/` = reglas puras (fiscal, cálculo en céntimos enteros, formatos, estado) sin web ni BD; `rutas/` = una por pantalla, SQL directo; el servidor es la única fuente de cálculo (pantalla y PDF).

## Decisiones transversales por spec (reutilizables en nuevas features)
- [004] El HTML de un PDF sale solo de `html_pdf(conn, datos)` (`rutas/presupuestos.py`); descarga individual y exportación lo comparten. `generar_pdf` se importa **dentro** de la función de la ruta para poder parchear `presupuestos.pdf.generar_pdf` en los tests.
- [004] «Descargado» = `emisor_congelado IS NOT NULL` (no se deduce de la etiqueta de estado, porque «Caducado» tiene prioridad). «Exportable» = descargado y `requisitos_descarga(...)` vacío.
- [004] Rutas de solo lectura que leen varias cosas: `BEGIN` + `ROLLBACK` (un único instante en WAL); el render de PDF va fuera de la transacción. Rutas que generan PDF: `def` síncrona con `Form(...)`, no `async def`, para no bloquear el bucle de eventos.
- [004] Ventanas modales: `<dialog>` nativo con `showModal()` en `app.js` (sin librería), fuera de los fragmentos que sustituye HTMX. Descargas binarias o con errores visibles: `fetch` + `Blob` desde `app.js`; los errores se devuelven como JSON `{"error": "…"}` y se muestran en un `role="alert"`.
- [004] `hidden` no funciona en elementos con `.error` o `.mensaje` (fuerzan `display`): añadir `contenedor [hidden] { display: none; }` en `estilos.css`.
- [004] Nombres de archivo para el usuario: `limpiar_nombre` (`dominio/nombre_archivo.py`) conserva tildes y «ñ»; `nombre_pdf` (descarga individual, sin tildes) no se toca.
- [004] No hay exportación de datos del negocio (JSON); la única copia de seguridad es `python -m presupuestos copia`. Exportar/importar datos está en `specs/propuestas.md` (P6).
- [002] Paleta oscura en `static/tokens-oscuro.css` (solo colores, mismos nombres que `tokens.css`). Todo color nuevo se añade a las dos hojas y, si es un par texto/fondo, a `PARES` de `tests/test_paleta.py`. Si un color debe ser igual en los dos temas (p. ej. `--color-fondo-logo`), se define solo en `tokens.css`.
- [002] El tema lo calcula el servidor con `tema_actual(request)` (cookie `tema` por dispositivo, sin BD; las páginas sin sesión siguen siempre al sistema). `base.html` lo aplica con el `media` de `<link id="tokens-oscuro">` y el `<meta name="color-scheme">` (tabla `APARIENCIA`, repetida en `app.js`). Sin destello y sin JS para pintar.
- [002] El PDF solo lee `tokens.css` (`pdf.estilos_comunes()`), así que sale siempre en claro: no enlazar `tokens-oscuro.css` desde `pdf.html`.
- [002] Para redirigir a un `volver` del usuario, solo se aceptan rutas internas que atienden GET (`_destino` en `rutas/sesion.py`, con `route.matches()`). En esta versión de FastAPI, `app.routes` envuelve los routers incluidos (`_IncludedRouter`): no se puede filtrar con `isinstance(r, APIRoute)`.

## Arranque y pruebas en local
```bash
python3.12 -m venv .venv && .venv/bin/pip install -e ".[dev]"
RUTA_BD=datos/presupuestos.db COOKIE_SEGURA=0 .venv/bin/uvicorn presupuestos.app:app --reload  # http://127.0.0.1:8000
.venv/bin/pytest                       # toda la suite
.venv/bin/pytest tests/test_acceso.py::test_x  # un solo test
```
- El PDF necesita Pango (macOS: `brew install pango` y `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`); los tests no lo necesitan.
- Al primer arranque se crea el titular desde el navegador (`/crear-titular`). Órdenes de administración (restablecer titular, copia): `python -m presupuestos`; ver `docs/administracion.md`.

## Convenciones
- Spec-Driven Development (Spec Kit): especificar → clarificar → plan → tareas → implementar. Todo cambio debe enlazar a un punto de la spec; ideas nuevas van a `specs/propuestas.md`, no se construyen.
- Todo en español de España (UI, mensajes, PDF, identificadores del código); importes `1.234,56 €`, fechas DD/MM/AAAA en pantalla y ISO en BD.
- Simplicidad ante todo: sin capas, dependencias ni configuración anticipadas.
- Seguridad: CSP estricta (sin scripts/estilos en línea), comprobación de origen en cada escritura, secretos solo en `.env` no versionado.
- Cada criterio de éxito debe poder verificarse en la app (`quickstart.md` de cada spec); los tests son apoyo.

Las reglas de producto viven en .specify/memory/constitution.md y el estado del producto en specs/README.md
