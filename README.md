# PresupuestosPro

A small, self-hosted web app that lets freelancers (*autónomos*) in Spain create professional quotes (*presupuestos*) and download them as PDF — with the right VAT, withholding tax and legal wording for each type of client.

The user interface and the generated PDFs are in **Spanish (Spain)**; amounts use the Spanish format (`1.234,56 €`). This README is in English for a wider audience.

The project was built with **Spec-Driven Development** using [Spec Kit](https://github.com/github/spec-kit): every feature starts as a written specification, then a plan, a task list and an implementation that is verified against the spec. All specs live in [`specs/`](specs/).

---

## Features

**Quotes**
- Sequential numbering per year (`PRE-2026-001`), never reused, safe under concurrent use.
- Line items from a service catalogue or typed by hand; instant totals while editing (auto-save).
- Tax rules per client type (Spanish mainland, Canary Islands/Ceuta/Melilla, EU with verified VAT number, outside the EU): VAT, IRPF withholding and the mandatory legal mention.
- Native date pickers; the validity date is recalculated from the issue date unless edited by hand.
- History with search; "Back to history" keeps the active search.
- Status badges derived from existing data — **Borrador** (draft), **Enviado** (PDF downloaded), **Caducado** (expired) — with no extra data stored.

**PDF**
- Generated on the server, A4, multi-page with repeated table headers.
- Same typography and palette as the app; issuer data is frozen on the first download so later profile changes don't alter quotes already sent.
- No network access during generation: only embedded `data:` resources are allowed.

**Clients, catalogue and profile**
- Clients with category, territory, document type and country selectors that only offer valid combinations; archive and GDPR anonymisation.
- Service catalogue with units and prices.
- Freelancer profile with logo (PNG, JPG or SVG, validated by content).

**Accounts and security**
- One owner (*titular*) and optional assistants; the owner account is created from the browser on first run.
- Argon2id password hashing, server-side sessions with 8-hour expiry, lockout after 5 failed attempts.
- Strict Content Security Policy (no inline scripts or styles), same-origin checks on every write, `no-store` caching for authenticated pages.

**Operations**
- Full data export as JSON; hot, integrity-checked SQLite backups from the command line.
- Automatic, non-destructive database upgrade on start-up.

**Accessibility**
- Targets WCAG 2.1 AA: verified colour contrast, visible focus, skip link, 44 × 44 px touch targets, logical headings, reduced-motion support, usable at 320 px width and 200 % zoom.

---

## Tech stack

| Layer | Choice |
|---|---|
| Language | Python 3.12 |
| Web framework | FastAPI + Jinja2 templates (server-rendered HTML) |
| Interactivity | [HTMX](https://htmx.org/) (vendored) and a small vanilla JS file — no build step |
| Database | SQLite (single file, WAL mode) |
| PDF | WeasyPrint |
| Passwords | argon2-cffi (Argon2id) |
| Typography | [Inter](https://rsms.me/inter/) 4.1, bundled (SIL Open Font License) |
| Tests | pytest |
| Deployment | Docker Compose + Caddy (automatic HTTPS) |

No CSS framework and no JavaScript dependencies besides HTMX. All visual decisions (colours, type scale, spacing) live in a single file: [`presupuestos/static/tokens.css`](presupuestos/static/tokens.css), shared by the web app and the PDF.

---

## Repository layout

```text
presupuestos/
├── app.py              # FastAPI app: security headers, session and origin checks, error pages
├── __main__.py         # Admin CLI: reset owner password, database backup
├── db.py, schema.sql   # SQLite connection, schema and automatic upgrades
├── seguridad.py        # Passwords, sessions, login lockout
├── pdf.py              # PDF generation (fonts embedded as data: URIs)
├── dominio/            # Pure business rules (tax treatment, totals, formats, dates, statuses…)
├── rutas/              # HTTP routes: quotes, clients, catalogue, profile, accounts, export
├── templates/          # Jinja2 pages and HTMX fragments, plus the PDF template
└── static/             # tokens.css, estilos.css, app.js, htmx.min.js, fonts
tests/                  # pytest suite (domain rules, access control, upgrades, PDF content, palette)
specs/                  # Spec Kit artifacts for each feature (spec, plan, research, contracts, tasks)
docs/administracion.md  # Server administrator guide (Spanish)
```

Code identifiers are in Spanish to match the domain language of the specs.

---

## Getting started

### Run locally

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# COOKIE_SEGURA=0 allows the session cookie over plain http on localhost
RUTA_BD=datos/presupuestos.db COOKIE_SEGURA=0 .venv/bin/uvicorn presupuestos.app:app --reload
```

Open <http://127.0.0.1:8000>. On first run you will be asked to create the owner account.

**PDF downloads need WeasyPrint's system libraries (Pango).** On macOS with Homebrew:

```bash
brew install pango
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib RUTA_BD=datos/presupuestos.db COOKIE_SEGURA=0 \
  .venv/bin/uvicorn presupuestos.app:app --reload
```

On Debian/Ubuntu, install `libpango-1.0-0 libpangoft2-1.0-0`. The Docker image already includes them.

### Run the tests

```bash
.venv/bin/pytest
```

The test suite does not need the PDF system libraries: it captures the HTML sent to the PDF generator instead of rendering it.

### Deploy with Docker

```bash
cp .env.example .env        # set DOMINIO to your domain; keep COOKIE_SEGURA=1
mkdir -p datos copias && sudo chown 1000:1000 datos copias
docker compose up -d --build
```

Caddy obtains and renews the HTTPS certificate. Then open your domain straight away and create the owner account. Backups, restores and other operations are described in [`docs/administracion.md`](docs/administracion.md).

---

## Spec-Driven Development

Each feature went through the Spec Kit workflow — `specify → clarify → plan → tasks → analyze → implement` — governed by the project [constitution](.specify/memory/constitution.md): simplicity first, Spanish (Spain) everywhere, no scope creep, everything verifiable from the app, and respect for user data.

| Spec | Scope |
|---|---|
| [001 — PresupuestosPro v1](specs/001-presupuestos-pro/spec.md) | Quotes, clients, catalogue, tax rules, PDF, accounts, export and backups |
| [002 — Navigation, forms and users](specs/002-mejoras-ui-usuarios/spec.md) | Side menu, back to history, user management, owner sign-up in the browser, selectors, date pickers, logo |
| [003 — Visual redesign and accessibility](specs/003-rediseno-visual/spec.md) | Design tokens, bundled typography, status badges, PDF redesign, WCAG 2.1 AA |

Each spec folder contains the plan, research decisions, data model, contracts, a step-by-step verification guide (`quickstart.md`) and the task list. Ideas that are out of scope are tracked in [`specs/propuestas.md`](specs/propuestas.md) until they make it into a spec.

---

## License

No license has been chosen for the application code yet. The bundled Inter font is distributed under the [SIL Open Font License 1.1](presupuestos/static/fuentes/OFL.txt).
