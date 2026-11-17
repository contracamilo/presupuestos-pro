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
