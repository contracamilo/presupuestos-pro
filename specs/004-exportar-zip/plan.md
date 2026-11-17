# Implementation Plan: PresupuestosPro v1.3 — Exportar en un .zip

**Branch**: `feature/004-exportar-zip` | **Date**: 2026-11-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-exportar-zip/spec.md`

## Summary

Sustituir la exportación en archivo de datos (`GET /exportar`) por un botón «Exportar…» en el historial que abre una ventana previa («Todo» o «Seleccionar qué exportar») y descarga un único `.zip` con los PDF de los presupuestos ya descargados (sin archivo de datos: decisión D-004-1, [research.md](./research.md) E12).

**Enfoque, en una frase**: una ventana `<dialog>` nativa en el historial, una ruta nueva `POST /exportar` que lee todo en una sola transacción de lectura, genera cada PDF con **el mismo código** que la descarga individual y empaqueta con `zipfile` de la biblioteca estándar; la descarga la lanza un pequeño trozo de JavaScript con `fetch` para poder mostrar «Preparando la copia…» y los errores.

**Lo que cambia respecto a la v1.2** (cada punto ligado a un requisito):

| Cambio | Por qué | Requisito |
|---|---|---|
| `historial.html` + `_exportar_ventana.html` (nuevo): botón «Exportar…» y `<dialog>` | Paso previo con «Todo» / «Seleccionar» | FR-301, 301a–c |
| `static/app.js`: abrir/cerrar la ventana, marcar todos, recuento, número de archivos en el botón, envío con `fetch`, estado «Preparando…» y ventana bloqueada mientras se prepara | Estado de espera y errores sin recargar | FR-301c, FR-310a, FR-311, FR-313, FR-313a |
| `rutas/exportar.py`: `GET /exportar` (JSON) → `POST /exportar` (zip de PDF) | Zip único; selección parcial | FR-302, 303, 314 |
| `rutas/presupuestos.py`: se extrae `html_pdf(conn, datos)` de `descargar_pdf` (sin cambiar su comportamiento) | El PDF del zip es el mismo que el de la descarga | FR-304 |
| `dominio/nombre_archivo.py`: `nombre_pdf_zip(numero, cliente)` y `limpiar_nombre` | «número - cliente.pdf» con tildes | FR-307, FR-308 |
| `templates/base.html`: se retira «Exportar» del menú | Su destino ya no existe | FR-314 |
| `estilos.css`: estilos de la ventana con los tokens existentes | Sistema visual de la 003 | FR-315 |

**No cambia**: esquema de datos (`user_version` sigue en 2), cálculos, estados, PDF, numeración, cuentas. **No se añade ninguna dependencia.**

Detalle y alternativas descartadas en [research.md](./research.md) (E1–E11).

## Technical Context

Sin cambios respecto a [specs/001-presupuestos-pro/plan.md](../001-presupuestos-pro/plan.md#technical-context) y a la [003](../003-rediseno-visual/plan.md#technical-context): Python 3.12, FastAPI, Jinja2, HTMX, WeasyPrint 70, SQLite (`user_version = 2`), pytest, Docker + Caddy. **No se añade ninguna dependencia** (ni de Python ni de JavaScript).

Precisiones de esta iteración:

- **Zip**: módulo `zipfile` de la biblioteca estándar, en memoria (`BytesIO`); nombres de entrada en UTF-8 (bandera que `zipfile` activa sola con nombres no ASCII; la leen Windows, macOS y Linux) (E5).
- **Ventana**: elemento `<dialog>` nativo con `showModal()` (foco atrapado, Esc, foco devuelto al botón); navegadores actuales (E1).
- **Descarga**: `fetch` + `Blob` desde `app.js`; admitido por la CSP actual (`default-src 'self'`, sin cambios) (E2).
- **Coherencia**: una transacción de lectura (`BEGIN`) en WAL para leer todo; el PDF se genera fuera de ella (E4).
- **Rendimiento**: sin objetivo nuevo más allá del de la 001 (PDF < 3 s por presupuesto); con 50 presupuestos se espera del orden de decenas de segundos, visible con «Preparando la copia…». Se mide en [quickstart.md](./quickstart.md) (E7).
- **Alcance**: 1 plantilla nueva (fragmento), 1 modificada (`historial.html`) + `base.html`; 1 ruta cambiada; ~120 líneas de JS (ventana, selección, recuento del botón y estado de espera).

No queda ningún «NEEDS CLARIFICATION».

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo lo cumple el plan | Estado |
|---|---|---|
| **I. Simplicidad ante todo** | Sin dependencias; `zipfile` estándar; `<dialog>` nativo en lugar de una biblioteca de modales; sin cola de trabajos, sin barra de progreso, sin ficheros temporales ni caché de PDF; el PDF se genera con la función ya existente. El `fetch` es la forma más simple de cumplir FR-311 y FR-313 (saber cuándo termina y mostrar errores). | ✅ |
| **II. Idioma y mercado** | Textos nuevos en español de España; nombre de los PDF con tildes y «ñ» conservadas; fecha del nombre del zip con la fecha de España que ya usa la app. | ✅ |
| **III. Cero alcance fantasma** | Solo lo de la spec: sin filtros, sin importar, sin copias programadas, sin PDF de borradores. La retirada del enlace «Exportar» del menú y de `GET /exportar` es FR-314. La exclusión de presupuestos cuyo PDF la app no puede generar (cliente anonimizado) es consecuencia de FR-304 y está en la spec (caso límite). | ✅ |
| **IV. Verificable sin leer código** | [quickstart.md](./quickstart.md) cubre cada escenario y criterio con pasos y resultado observable; los pasos técnicos van marcados «(Técnico)». | ✅ |
| **V. Datos del usuario con respeto** | Sin datos nuevos; el zip solo contiene PDF que ya se pueden descargar desde la app (sin cuentas ni contraseñas); nada se guarda en el servidor. | ✅ |

**Re-evaluación tras el diseño (Fase 1)**: ✅ sin cambios. Un punto revisado: la spec habla de «el mismo PDF que genera la app», y el código de la descarga exige condiciones (cliente no anonimizado, NIF, líneas); el plan las aplica igual a la exportación y la spec lo recoge ahora en un caso límite.

## Project Structure

### Documentation (this feature)

```text
specs/004-exportar-zip/
├── plan.md              # Este archivo
├── research.md          # Fase 0: decisiones E1–E11
├── data-model.md        # Fase 1: sin cambios de esquema; contenido de la copia
├── quickstart.md        # Fase 1: guía de comprobación en la app
├── contracts/
│   ├── rutas-http.md          # Ventana, POST /exportar y retirada de GET /exportar
│   └── archivo-exportacion.md # Estructura del zip (solo PDF)
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks; no lo crea este comando)
```

### Source Code (repository root)

```text
presupuestos/
├── rutas/
│   ├── exportar.py              # POST /exportar (zip de PDF); presupuestos_exportables
│   └── presupuestos.py          # + html_pdf(conn, datos); historial pasa los exportables
├── dominio/
│   └── nombre_archivo.py        # + limpiar_nombre, nombre_pdf_zip
├── templates/
│   ├── base.html                # sin enlace «Exportar»
│   ├── historial.html           # botón «Exportar…» + ventana
│   └── fragmentos/_exportar_ventana.html   # nuevo: <dialog>
└── static/
    ├── app.js                   # + ventana de exportación
    └── estilos.css              # + estilos del <dialog> con tokens
tests/
├── dominio/test_formato_fechas_nombre.py   # + nombres del zip
├── test_exportar_zip.py                    # nuevo (sustituye al caso JSON)
├── test_exportar_copia.py                  # se retira el test del JSON; queda test_orden_copia
└── test_acceso.py                          # /exportar pasa de GET a POST
```

**Structure Decision**: mismo proyecto único. La lógica de qué entra en la copia (presupuestos «exportables», nombres) vive en `rutas/exportar.py` y `dominio/nombre_archivo.py`; el PDF se reutiliza, no se duplica.

## Complexity Tracking

Sin violaciones de la constitución que justificar.
