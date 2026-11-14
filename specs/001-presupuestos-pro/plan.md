# Implementation Plan: PresupuestosPro v1

**Branch**: `001-presupuestos-pro` | **Date**: 2026-11-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-presupuestos-pro/spec.md`

## Summary

Herramienta web para que un autónomo en España cree presupuestos con su imagen corporativa, con IVA e IRPF calculados según el tipo de cliente, y los descargue en PDF. Cada autónomo tiene su propio servidor; titular y asistentes entran con su cuenta, y los datos no se pierden si se borra el navegador o se estropea el equipo.

**Enfoque, en una frase**: un único programa en Python (FastAPI) que muestra las pantallas, guarda todo en un solo archivo SQLite, controla quién entra y genera el PDF. Corre en un servidor pequeño en la UE, con HTTPS automático y una copia diaria fuera del servidor.

**Qué garantiza el diseño, en lenguaje de negocio**:

- **Una sola pieza que mantener**: un programa, un lenguaje, un archivo de datos. Sin aplicación de interfaz aparte ni servidor de base de datos.
- **Cálculos exactos al céntimo**: céntimos enteros y una única función de cálculo, en el servidor, para la pantalla y el PDF (SC-002, SC-003).
- **Regla fiscal en un solo sitio**, fácil de revisar con el asesor.
- **Solo entra quien el titular autoriza**, cada uno con su cuenta, y el titular puede cortar un acceso al instante (FR-034, FR-035).
- **Datos a salvo**: todo está en el servidor; cada noche se copia a otro servicio en la UE y se conservan 30 días. Como máximo se pierde un día de trabajo (SC-011).
- **Numeración sin duplicados** aunque dos personas creen presupuestos a la vez (FR-033).

Detalle y alternativas descartadas en [research.md](./research.md).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI + Uvicorn (servidor web), Jinja2 (plantillas HTML), HTMX (archivo JS servido en local, para recalcular sin recargar), WeasyPrint (PDF), argon2-cffi (contraseñas), python-multipart (subida de logo). Base de datos con `sqlite3` de la librería estándar, sin ORM.

**Storage**: SQLite, un único archivo por instalación (incluidos los logos), en modo WAL (D3).

**Testing**: pytest para reglas de cálculo y fiscales (todos los ejemplos de la spec) y control de acceso, con el cliente de pruebas de FastAPI. Verificación funcional en la app con [quickstart.md](./quickstart.md) (principio IV).

**Target Platform**: servidor Linux (VPS en la UE) con Docker Compose: contenedor de la app + Caddy (HTTPS automático). Navegadores actuales en ordenador, tableta y móvil desde 360 px.

**Project Type**: aplicación web con páginas generadas en el servidor (un único proyecto).

**Performance Goals**: recálculo percibido como instantáneo (< 300 ms por cambio, incluido el viaje al servidor); PDF de un presupuesto normal en < 3 s. Volumen: 1–5 usuarios, cientos de presupuestos.

**Constraints**: datos solo en el servidor propio, sin servicios de terceros salvo alojamiento y copias (FR-028); todo cifrado en tránsito; español de España y `1.234,56 €` (FR-030); sin desplazamiento horizontal desde 360 px (FR-031); una sola instancia de la app (SQLite).

**Scale/Scope**: una instalación por autónomo; ~11 pantallas: inicio de sesión, historial, presupuesto, clientes, catálogo, perfil, ajustes, mi cuenta, cuentas (titular), exportar; más 3 órdenes de administración.

No queda ningún "NEEDS CLARIFICATION".

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo lo cumple el plan | Estado |
|---|---|---|
| **I. Simplicidad ante todo** | Un solo programa y un solo lenguaje; páginas del servidor + HTMX en lugar de SPA; `sqlite3` estándar sin ORM ni herramienta de migraciones; un archivo de datos (copia = copiar un archivo); sesiones en la propia base de datos; administración por línea de comandos en lugar de pantallas; sin CI, sin Kubernetes, sin réplicas. Cada dependencia responde a un requisito concreto. | ✅ |
| **II. Idioma y mercado** | Interfaz, mensajes, PDF y órdenes de administración en español de España; formateador único de importes y fechas con tests (D18). | ✅ |
| **III. Cero alcance fantasma** | Nada fuera de la spec: sin recuperación por email, sin doble factor, sin importación, sin registro de autoría, sin numeración de páginas en el PDF, sin congelar la mención de Canarias, sin detección de conflictos de edición. Lo que surja va a propuestas. | ✅ |
| **IV. Verificable sin leer código** | [quickstart.md](./quickstart.md) cubre cada criterio de aceptación y de éxito con pasos y resultado observable; los pocos pasos técnicos (copias, caducidad de sesión, cambio de año) están marcados. Los tests son apoyo. | ✅ |
| **V. Datos del usuario con respeto** | Solo los campos de la spec; contraseñas con Argon2id; la exportación excluye cuentas; las credenciales de copias y secretos van en configuración del servidor no versionada (`.env`, configuración de rclone), nunca en el repositorio. | ✅ |

**Re-evaluación tras el diseño (Fase 1)**: ✅ sin cambios. Piezas añadidas que la spec no nombra, todas como la forma más simple de cumplir un requisito:

- *Caddy*: el cifrado obligatorio de FR-028 sin gestionar certificados a mano.
- *Docker Compose*: WeasyPrint necesita librerías del sistema; Docker las deja instaladas igual en local y en el servidor.
- *rclone + cron*: subir la copia diaria fuera del servidor y borrar las de más de 30 días (FR-041).
- *Tablas `logos`, `sesiones` e `intentos_acceso`*: necesarias para FR-018/CL12, FR-037 y FR-038.

No hay violaciones que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/001-presupuestos-pro/
├── plan.md              # Este archivo
├── research.md          # Fase 0: decisiones D1–D20
├── data-model.md        # Fase 1: tablas, reglas y cálculo
├── quickstart.md        # Fase 1: guía de comprobación en la app
├── contracts/
│   ├── rutas-http.md            # Pantallas y acciones de la app
│   ├── pdf-presupuesto.md       # Contenido y reglas del PDF
│   ├── archivo-exportacion.md   # Formato del archivo exportado
│   └── cli-administracion.md    # Órdenes del administrador, copias y restauración
└── tasks.md             # Fase 2 (/speckit-tasks; no lo crea este comando)
```

### Source Code (repository root)

```text
pyproject.toml               # Dependencias
Dockerfile
docker-compose.yml           # app + caddy; volúmenes de datos y copias
Caddyfile                    # Dominio y HTTPS
.env.example                 # Variables de configuración (sin valores reales)
docs/
└── administracion.md        # Instalación, alta del titular, cron de copias, restauración (FR-042)
presupuestos/
├── __main__.py              # Órdenes: crear-titular, restablecer-titular, copia
├── app.py                   # Crea la app, cabeceras de seguridad, comprobación de sesión y origen
├── db.py                    # Conexión, aplicar schema.sql, transacciones, numeración (D10)
├── schema.sql
├── seguridad.py             # Contraseñas, sesiones, bloqueo por intentos (D7, D8)
├── dominio/                 # Reglas de negocio puras: sin web ni base de datos
│   ├── tratamiento.py       # Tabla RN6
│   ├── calculo.py           # RN1–RN5 en céntimos
│   ├── validacion.py        # RN10, requisitos de descarga (FR-023), obligatorios
│   ├── fechas.py            # RN8, AAAA-MM-DD ↔ DD/MM/AAAA
│   ├── formato.py           # 1.234,56 €, cantidades, lectura de importes
│   └── nombre_archivo.py    # FR-022
├── rutas/                   # Una por pantalla (contracts/rutas-http.md)
│   ├── sesion.py
│   ├── presupuestos.py      # Incluye historial y PDF
│   ├── clientes.py
│   ├── catalogo.py
│   ├── perfil.py            # Perfil, logo y ajustes
│   ├── cuentas.py           # Mi cuenta y cuentas (titular)
│   └── exportar.py
├── pdf.py                   # WeasyPrint sin acceso a internet (D6)
├── templates/               # Jinja2: base, pantallas, fragmentos HTMX y pdf.html
└── static/
    ├── htmx.min.js
    └── estilos.css          # Diseño adaptable (FR-031)
tests/
├── dominio/                 # Ejemplos numéricos y reglas de la spec
└── test_acceso.py           # Sin sesión, solo titular, bloqueo, baja, numeración concurrente
```

**Structure Decision**: un único proyecto Python. La única separación con valor de negocio es **`dominio/`**: las reglas fiscales y de cálculo no dependen de la web ni de la base de datos, así que se prueban automáticamente con los ejemplos de la spec y se pueden revisar con un asesor sin leer el resto. Las rutas leen y escriben en la base de datos con SQL directo y usan esas reglas; no hay capas de repositorio ni de servicios.

## Complexity Tracking

Sin violaciones de la constitución que justificar.
