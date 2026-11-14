# Implementation Plan: PresupuestosPro v1.2 — Rediseño visual profesional y accesible

**Branch**: `003-rediseno-visual` | **Date**: 2026-11-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-rediseno-visual/spec.md`

## Summary

Rediseño visual de toda la app y del PDF sobre la v1.1 (001 + 002): una tipografía (Inter, incluida con la aplicación), una paleta limitada, una escala de tamaños y otra de espaciado definidas **en un único archivo** (`static/tokens.css`) que comparten la app y el PDF; componentes comunes (botones, campos, mensajes, listas, totales); etiquetas de estado de presupuesto deducidas sin guardar nada (Borrador, Enviado, Caducado; Aceptado y Rechazado solo diseñadas); y accesibilidad de nivel WCAG 2.1 AA.

**Enfoque, en una frase**: reescribir la capa de presentación (CSS y marcado de las plantillas) a partir de tokens, sin tocar rutas, cálculos ni datos; la única pieza de Python nueva es una función pura que deduce el estado.

**Lo que no es solo CSS/plantillas** (cada punto ligado a un requisito):

| Cambio | Por qué | Requisito |
|---|---|---|
| `dominio/estado.py` (función pura) y su uso en `rutas/presupuestos.py` para pasar `estado` a las plantillas | Mostrar el estado sin guardarlo | FR-209, FR-209a |
| `pdf.py`: CSS común con las fuentes insertadas como `data:` (en caché) y pasado a `pdf.html` | Misma tipografía y tokens en el PDF sin abrir el generador a archivos | FR-201, FR-217 |
| Cuatro archivos de fuente en `static/fuentes/` + licencia | Tipografía idéntica en todas partes, sin internet | FR-201, FR-218 |

Detalle y alternativas descartadas en [research.md](./research.md) (V1–V12).

## Technical Context

Sin cambios respecto a [specs/001-presupuestos-pro/plan.md](../001-presupuestos-pro/plan.md#technical-context): mismo lenguaje (Python 3.12), dependencias (FastAPI, Jinja2, HTMX, WeasyPrint 70, argon2-cffi), almacenamiento (SQLite, `user_version = 2`), pruebas (pytest), plataforma (VPS con Docker), tipo de proyecto (aplicación web de servidor con HTMX) y restricciones. **No se añade ninguna dependencia** (las fuentes son archivos estáticos, no paquetes).

Precisiones de esta iteración:

- **Tipografía**: Inter 4.x, WOFF2, pesos 400, 400 cursiva, 600 y 700 (OFL 1.1) (V2).
- **CSS**: propiedades personalizadas (`var()`), admitidas por los navegadores actuales y por WeasyPrint 70 (comprobado) (V1, V10).
- **Accesibilidad**: WCAG 2.1 AA; contrastes de la paleta calculados de antemano (V5).
- **Rendimiento**: PDF < 3 s (objetivo de la 001), comprobado con 40 líneas; fuentes de la app cacheadas por el navegador (`/static/`).
- **Alcance**: 13 plantillas de página, 14 fragmentos, `pdf.html`, `estilos.css` (reescrito), `tokens.css` (nuevo).

No queda ningún «NEEDS CLARIFICATION».

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo lo cumple el plan | Estado |
|---|---|---|
| **I. Simplicidad ante todo** | Sin dependencias, sin preprocesadores ni frameworks CSS: un archivo de tokens con variables CSS que leen la app y el PDF. Iconos en SVG en línea en una macro. Estado deducido con una función de 10 líneas en lugar de una columna. Se conservan las clases que usa `app.js` para no tocarlo. | ✅ |
| **II. Idioma y mercado** | Textos nuevos (estados, «Saltar al contenido», prefijos para lectores) en español de España; la fuente cubre todos los caracteres del español y «€»; importes con cifras tabulares en formato español sin cambios. | ✅ |
| **III. Cero alcance fantasma** | Solo lo pedido y aclarado: sin modo oscuro, sin temas por autónomo, sin filtros por estado, sin marcar Aceptado/Rechazado (solo sus etiquetas, FR-209a). El contenido del PDF no cambia. | ✅ |
| **IV. Verificable sin leer código** | [quickstart.md](./quickstart.md) cubre cada escenario y criterio con pasos y resultado observable; los pasos técnicos (pytest, tokens, red) van marcados «(Técnico)». | ✅ |
| **V. Datos del usuario con respeto** | Ningún dato nuevo ni cambio de esquema; el estado se calcula al mostrar. Sin recursos externos (fuentes incluidas), así que el navegador no revela visitas a terceros. | ✅ |

**Re-evaluación tras el diseño (Fase 1)**: ✅ sin cambios. Dos puntos revisados:
- `dominio/estado.py` es una regla de presentación de solo lectura (no cambia cálculos, rutas ni datos): compatible con FR-215 y con el principio III porque la pide la spec (FR-209).
- `tests/test_paleta.py` y `tests/test_pdf_contenido.py` amplían la política de tests de la 001 (D20); se justifican porque protegen criterios medibles de la spec (SC-202, SC-206, SC-209) que serían costosos de comprobar a mano en cada cambio (research V12).

## Project Structure

### Documentation (this feature)

```text
specs/003-rediseno-visual/
├── plan.md              # Este archivo
├── research.md          # Fase 0: decisiones V1–V12
├── data-model.md        # Fase 1: sin cambios en datos; estado deducido
├── quickstart.md        # Fase 1: guía de verificación en la app
├── contracts/
│   ├── sistema-visual.md   # Tokens, jerarquía, espaciado, componentes, pares de contraste
│   ├── estados.md          # Etiquetas de estado (texto, color, icono, forma)
│   └── pdf-diseno.md       # Aspecto del PDF (contenido sin cambios)
└── tasks.md             # Fase 2 (/speckit-tasks; no lo crea este comando)
```

### Source Code (repository root)

Estructura de la 001 sin cambios. Archivos que esta iteración toca (**nuevo**, *modificado*):

```text
presupuestos/
├── pdf.py                              # modificado: import de WeasyPrint dentro de generar_pdf; CSS común con fuentes en data: (caché) (V10)
├── dominio/
│   └── estado.py                       # NUEVO: estado(emisor_congelado, fecha_validez, hoy) y ETIQUETAS (V7)
├── rutas/
│   ├── __init__.py                     # modificado: ETIQUETAS de estado como global de Jinja
│   └── presupuestos.py                 # modificado: añade `estado` al historial y a _contexto; pasa el CSS común al PDF
├── static/
│   ├── tokens.css                      # NUEVO: paleta, tipografía, escalas, @font-face (V1–V5)
│   ├── estilos.css                     # reescrito: componentes con var(--…), mobile-first (V6, V9)
│   ├── fuentes/                        # NUEVO: Inter-Regular/Italic/SemiBold/Bold.woff2 + OFL.txt (V2)
│   └── app.js                          # sin cambios (se conservan sus clases, V11)
└── templates/
    ├── base.html                       # modificado: tokens.css, color-scheme, «Saltar al contenido», main#contenido
    ├── pdf.html                        # modificado: estilos con tokens y fuente Inter; contenido idéntico (V10)
    ├── historial.html, presupuesto.html, clientes.html, cliente.html, catalogo.html,
    │   perfil.html, ajustes.html, usuarios.html, mi_cuenta.html, entrar.html,
    │   crear_titular.html, error.html  # modificados: clases comunes, encabezados, mensajes
    └── fragmentos/
        ├── _iconos.html                # NUEVO: macro icono(nombre) con SVG en línea (V8)
        ├── _estado.html                # NUEVO: macro etiqueta_estado(estado) (V7)
        ├── _historial_lista.html       # modificado: etiqueta de estado
        ├── _respuesta_cabecera.html    # modificado: #estado-presupuesto fuera de banda
        ├── _totales.html               # modificado: tabla con th scope="row" y «Total» destacado
        └── (resto de fragmentos)       # modificados: clases comunes, sin cambiar ids, nombres ni hx-*
tests/
├── dominio/test_estado.py              # NUEVO: regla de estado (V7)
├── test_paleta.py                      # NUEVO: contrastes y «todo con tokens» (V12)
├── test_pdf_contenido.py               # NUEVO: texto del PDF idéntico a la referencia v1.1; sin estado (V12)
└── referencias/pdf_*.txt               # NUEVO: texto de referencia del PDF, generado ANTES de tocar pdf.html
```

**Structure Decision**: se mantiene el proyecto único de la 001. Toda decisión visual vive en `static/tokens.css` (fuente única para app y PDF); `estilos.css` se organiza por componentes. La regla del estado va en `dominio/`, como las demás reglas, para probarla con pytest.

**Orden obligatorio** (para tasks.md): (1) generar las referencias de texto del PDF con la v1.1 **antes** de modificar `pdf.html`; (2) `tokens.css` y fuentes antes de `estilos.css` y `pdf.html`; (3) `estado.py` y su test antes de las plantillas que muestran el estado.

## Complexity Tracking

Sin violaciones de la constitución que justificar.
