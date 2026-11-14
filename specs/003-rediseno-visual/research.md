# Research: PresupuestosPro v1.2 — Rediseño visual profesional y accesible

**Fecha**: 2026-11-14 | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

Stack, convenciones y estructura: [specs/001-presupuestos-pro/plan.md](../001-presupuestos-pro/plan.md) y [research.md de la 001 (D1–D20)](../001-presupuestos-pro/research.md), más las decisiones R1–R11 de la [002](../002-mejoras-ui-usuarios/research.md). Aquí solo van las decisiones nuevas (V1–V12). Ninguna añade dependencias de Python ni de JavaScript.

## Hallazgos sobre el código actual (punto de partida)

- **Estilos de la app**: un único `presupuestos/static/estilos.css` (~200 líneas) con 9 variables de color en `:root`, pero con colores sueltos repetidos fuera de ellas (`#fff`, `#eaeef2`, `rgba(0,0,0,.45)`), tamaños y márgenes escritos a mano en cada regla (≈ 15 tamaños de letra y separaciones distintos) y fuente `system-ui` (distinta en cada dispositivo).
- **PDF**: `presupuestos/templates/pdf.html` con su propio `<style>` en línea (permitido: WeasyPrint no aplica la CSP), fuente «DejaVu Sans» del sistema (paquete `fonts-dejavu-core` del `Dockerfile`) y colores grises sueltos. No comparte nada con la app.
- **CSP** (`app.py`): `style-src 'self'`, `font-src` no declarado → hereda `default-src 'self'`. Las fuentes servidas desde `/static/` están permitidas; los estilos en línea (`style="…"`, `<style>`) en las páginas de la app **no**.
- **Generador del PDF** (`pdf.py`, D6): solo admite URIs `data:`; ninguna otra URL se descarga.
- **WeasyPrint 70** (comprobado en el entorno): admite variables CSS (`var()`), `font-variant-numeric: tabular-nums` y fuentes WOFF2 (brotli instalado como dependencia de WeasyPrint).
- **Estados**: no existe ninguna columna de estado. `presupuestos.emisor_congelado` se rellena en la primera descarga correcta del PDF (FR-018 de la 001) y `fecha_validez` está siempre presente: bastan para deducir Borrador, Enviado y Caducado (spec, Clarifications).
- **Pantallas**: 13 plantillas de página + 14 fragmentos (`templates/fragmentos/`). Los títulos de pantalla son `<h1>`, pero algunos bloques usan `<h2>` y otros `<p><strong>` para lo mismo; los totales son una `<table>` sin cabeceras; no hay enlace «Saltar al contenido».

---

## V1. Un único lugar para la paleta, la escala tipográfica y el espaciado — FR-202, FR-203, SC-209

- **Decisión**: nuevo archivo `presupuestos/static/tokens.css` con **todas** las decisiones de diseño como propiedades personalizadas de CSS en `:root` (colores, tipografía, tamaños, espaciado, radios, sombra, foco). `estilos.css` solo usa `var(--…)`; ningún color, tamaño ni separación escrito a mano fuera de `tokens.css`. El PDF incluye **el mismo archivo** (V10).
  - App: `base.html` enlaza `tokens.css` y después `estilos.css` (dos `<link>`, permitidos por la CSP).
  - PDF: `pdf.py` lee `tokens.css` una vez (caché en memoria) y lo pasa a la plantilla, que lo inserta en su `<style>`.
- **Motivo**: «definido en un único lugar» literal: cambiar `--color-marca` cambia la app y el PDF (SC-209). Sin preprocesadores ni herramientas de construcción (principio I).
- **Alternativas descartadas**: Sass u otro preprocesador (dependencia y paso de construcción); duplicar los valores en `pdf.html` (dos lugares, se desincronizan); un framework CSS (Tailwind, Bootstrap: dependencia, clases en todas las plantillas, aspecto genérico).

## V2. Tipografía: Inter, incluida con la aplicación — FR-201, SC-210 (Clarifications Q3)

- **Decisión**: familia **Inter** 4.x (licencia SIL Open Font License 1.1, se permite distribuirla), en **WOFF2** con cuatro archivos estáticos: Regular 400, Italic 400, SemiBold 600 y Bold 700, en `presupuestos/static/fuentes/` junto con `OFL.txt`. Se declaran con `@font-face` en `tokens.css` (`font-display: swap`) y la pila de reserva `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` (la app sigue legible si la fuente no carga: spec, Supuestos).
  - Importes con `font-variant-numeric: tabular-nums` (cifras de ancho fijo de la propia Inter: no hace falta una segunda familia).
  - En el PDF, los cuatro archivos se insertan como URIs `data:` (V10), así el generador sigue sin leer nada fuera de su contenido (D6 intacto).
- **Motivo**: diseñada para pantalla, muy legible en tamaños pequeños, cubre el español completo (tildes, «ñ», «ü», «¿», «¡», «€», «·», «—») y tiene cifras tabulares. Cuatro archivos (~100 KB cada uno en WOFF2) se cachean en el navegador tras la primera visita.
- **Alternativas descartadas**: fuentes del sistema (aspecto distinto por dispositivo y en el PDF, contrario a Q3); Source Sans 3 / IBM Plex Sans (igual de válidas; Inter tiene mejor legibilidad de cifras a 13–14 px); fuente variable de Inter (un archivo, pero ~350 KB y soporte de ejes variable más irregular en WeasyPrint); cargar desde Google Fonts (dependencia externa, prohibida por FR-218 y FR-028 de la 001).
- **Obtención**: los archivos se descargan una vez del repositorio oficial de Inter durante la implementación y se versionan con el código. No es una dependencia de ejecución.

## V3. Escala tipográfica (6 tamaños) — FR-201, FR-204

Base 16 px (se respeta el tamaño elegido en el navegador: todas las medidas en `rem`, FR-214).

| Token | Tamaño | Uso |
|---|---|---|
| `--texto-xs` | 0,8125 rem (13 px) | Títulos de grupo del menú (mayúsculas), etiquetas de estado, cabeceras de tabla |
| `--texto-sm` | 0,875 rem (14 px) | Texto secundario, ayudas, errores de campo, etiquetas de las líneas |
| `--texto-base` | 1 rem (16 px) | Texto normal, campos, botones |
| `--texto-lg` | 1,25 rem (20 px) | Títulos de sección (`h2`), «Total» en pantalla |
| `--texto-xl` | 1,5 rem (24 px) | Título de pantalla (`h1`) en móvil |
| `--texto-2xl` | 1,875 rem (30 px) | Título de pantalla (`h1`) desde 1024 px |

- Pesos: 400 normal, 600 etiquetas y títulos de sección, 700 título de pantalla y «Total».
- Interlineado: 1,5 para texto, 1,25 para títulos.
- El PDF usa la misma escala proporcional en `pt` (V10).

## V4. Escala de espaciado, radios y sombra — FR-203

- **Espaciado** (base 4 px): `--esp-1` 4 px · `--esp-2` 8 px · `--esp-3` 12 px · `--esp-4` 16 px · `--esp-5` 24 px · `--esp-6` 32 px · `--esp-7` 48 px. Reglas de uso en [contracts/sistema-visual.md](./contracts/sistema-visual.md#espaciado).
- **Radios**: `--radio-sm` 4 px (etiquetas de estado, campos), `--radio-md` 8 px (tarjetas, botones).
- **Sombra**: una sola, `--sombra` (tarjetas y menú en móvil).
- **Ancho de lectura**: `--ancho-contenido` 60 rem (960 px), como en la 002.

## V5. Paleta limitada y contrastes comprobados — FR-202, FR-212, SC-202

Contrastes calculados con la fórmula de WCAG 2.1 (luminancia relativa). Todos ≥ 4,5:1 para texto y ≥ 3:1 para bordes y foco.

| Token | Valor | Uso | Contraste |
|---|---|---|---|
| `--color-texto` | `#1a1f26` | Texto principal | 16,6:1 sobre blanco · 15,3:1 sobre `--color-fondo-2` |
| `--color-texto-suave` | `#4d5866` | Texto secundario, ayudas | 7,2:1 sobre blanco · 6,7:1 sobre `--color-fondo-2` |
| `--color-marca` | `#1f4e79` | Acción principal, enlaces, foco, acentos del PDF | 8,7:1 sobre blanco (y blanco sobre marca) |
| `--color-borde-control` | `#7b8794` | Bordes de campos y botones secundarios | 3,7:1 sobre blanco |
| `--color-borde` | `#d5dae0` | Separadores decorativos (no transmiten información) | — (decorativo) |
| `--color-fondo` | `#ffffff` | Fondo del contenido | — |
| `--color-fondo-2` | `#f4f6f8` | Fondo de la barra, menú y bloques destacados | — |
| `--color-exito` / `--color-exito-fondo` | `#1b6e3a` / `#e6f4ec` | Mensajes de éxito | 6,3:1 sobre blanco · 5,6:1 sobre su fondo |
| `--color-aviso` / `--color-aviso-fondo` | `#7a4f00` / `#fff4d6` | Avisos | 6,5:1 |
| `--color-error` / `--color-error-fondo` | `#b3261e` / `#fbe9e7` | Errores, botón de peligro, aviso de conexión | 6,5:1 sobre blanco · 5,6:1 sobre su fondo · blanco sobre error 6,5:1 |

Estados (V7): ver tabla en [contracts/estados.md](./contracts/estados.md); todos entre 5,5:1 y 7,3:1.

- **Motivo**: un azul marino sobrio como único color de marca, neutros fríos y un color por significado: «limitada» = 4 neutros + 1 marca + 3 significados + 5 estados (que reutilizan tonos de los anteriores).
- **Sin modo oscuro**: `color-scheme: light` en `:root` y `<meta name="color-scheme" content="light">`, para que los controles nativos (calendario, selectores) no se vuelvan oscuros sobre fondo claro (spec, casos límite).

## V6. Componentes comunes — FR-205 a FR-208

Se reescribe `estilos.css` organizado por componentes, en orden mobile-first (reglas base para 360 px y `@media (min-width: …)` para ampliar). Catálogo completo con clases y estados en [contracts/sistema-visual.md](./contracts/sistema-visual.md#componentes):

- **Botones**: `.boton` (principal), `.boton.secundario`, `.boton.peligro`; mismas clases para `<button>` y `<a>`. Alto mínimo 44 px. Se eliminan los estilos sueltos de `button` sin clase: todo botón lleva una variante.
- **Campos**: etiqueta encima, ayuda (`.ayuda`) y error (`.error-campo` con icono) debajo, alto 44 px, borde `--color-borde-control`, foco común (V9).
- **Mensajes**: `.mensaje.exito | .aviso | .error` con icono y texto.
- **Listas y tablas**: `.lista` (tarjetas en móvil, filas desde 760 px) y `.tabla` (para totales y usuarios); importes `.importe` con cifras tabulares a la derecha.
- **Totales**: tabla con «Total» en `--texto-lg` peso 700 y borde superior de 2 px.
- **Etiqueta de estado**: `.estado.borrador | .enviado | .caducado | .aceptado | .rechazado` (V7).

**Alternativas descartadas**: BEM estricto o CSS por pantalla (más clases y reglas, más difícil de mantener coherente); componentes con JavaScript (no hace falta ninguno).

## V7. Estado del presupuesto deducido, sin guardar nada — FR-209, FR-209a, FR-210, FR-211 (Clarifications Q1, Q2)

- **Decisión**: nuevo módulo puro `presupuestos/dominio/estado.py`:
  - `estado(emisor_congelado, fecha_validez, hoy) -> "borrador" | "enviado" | "caducado"`: `"caducado"` si `fecha_validez < hoy`; si no, `"enviado"` si `emisor_congelado` no es nulo; si no, `"borrador"`. Prioridad de Q2 en una sola función.
  - `ETIQUETAS` con las cinco etiquetas (`aceptado` y `rechazado` incluidas para FR-209a, sin función que las devuelva).
  - `hoy` llega de `fechas.hoy()` (Europe/Madrid, D18); un presupuesto con validez = hoy no está caducado.
- **Uso**: `rutas/presupuestos.py` añade `estado` a cada fila del historial y al contexto del presupuesto (`_contexto`). Una macro Jinja `etiqueta_estado(estado)` en `templates/fragmentos/_estado.html` pinta la etiqueta (texto + icono + clase). En la pantalla del presupuesto, la etiqueta va junto al número dentro de `<span id="estado-presupuesto">` y `_respuesta_cabecera.html` la devuelve fuera de banda, para que cambie al editar la fecha de validez sin recargar (US3 AS5).
- **No va al PDF**: `pdf.html` no recibe `estado` (FR-211).
- **¿Es lógica de negocio nueva?**: es una regla de presentación que lee datos existentes y no escribe nada; no cambia cálculos, rutas ni respuestas JSON (FR-215). Va en `dominio/` para probarla con pytest como las demás reglas.
- **Alternativas descartadas**: columna `estado` (prohibido por la spec); calcularlo en la plantilla con Jinja (regla sin probar, repetida en dos plantillas); consulta SQL con `CASE` (la fecha de hoy en España ya se calcula en Python, D18).
- **Limitación aceptada**: tras pulsar «Descargar PDF», la pantalla del presupuesto no se recarga (el navegador descarga un archivo); el estado pasa a «Enviado» al volver a abrirla o en el historial.

## V8. Iconos en SVG en línea, dibujados a mano — FR-210, FR-214, US1 AS6

- **Decisión**: seis iconos sencillos: `lapiz` (Borrador), `avion` (Enviado), `reloj` (Caducado), `check` (Aceptado y éxito), `aspa` (círculo con aspa: Rechazado y error) y `triangulo` (avisos y errores de campo) como macro Jinja `icono(nombre)` en `templates/fragmentos/_iconos.html`: `<svg aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24">` con trazos `stroke="currentColor"` (toman el color del texto). Siempre acompañan a un texto: nunca lo sustituyen.
- **Motivo**: sin archivos ni dependencias; la CSP no afecta al SVG en línea (no es script); heredan el color y escalan con el texto.
- **Alternativas descartadas**: librería de iconos (dependencia); fuente de iconos (accesibilidad pobre, otro archivo); caracteres Unicode (✓ ✗ ⏰: no todos están en Inter y cambian según la fuente de reserva).

## V9. Accesibilidad transversal — FR-212 a FR-214, US4

| Necesidad | Decisión |
|---|---|
| Foco visible | `:focus-visible { outline: 3px solid var(--color-marca); outline-offset: 2px; }` en todo elemento interactivo; nunca `outline: none` sin sustituto. Contraste del foco 8,7:1. |
| Saltar al contenido | Primer elemento de `<body>` con sesión: `<a class="saltar" href="#contenido">Saltar al contenido</a>`, oculto hasta recibir foco; `<main id="contenido" tabindex="-1">`. |
| Solo color, nunca | Estados con texto + icono; errores con icono + texto; sección actual del menú con borde izquierdo y negrita (002); campos obligatorios con «*» y la nota «* Obligatorio». |
| Zoom 200 % / 320 px | Medidas en `rem`, `min-width: 0` en rejillas, `overflow-wrap: anywhere` en nombres y descripciones, importes `white-space: nowrap` dentro de celdas que pueden bajar de línea completas; se comprueba a 320 px además de 360 px. |
| Reducir movimiento | `@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition: none !important; animation: none !important; } }`. |
| Encabezados | Un único `h1` por pantalla; secciones con `h2`; los bloques que hoy usan `<p><strong>` como título pasan a `h2`/`h3` según su nivel. |
| Tablas | `<th scope="col">` en cabeceras y `<th scope="row">` en las filas de totales («Base imponible», «IVA…», «Total»); `<caption class="solo-lector">` donde ayude. |
| Texto solo para lectores | Clase `.solo-lector` (patrón de recorte estándar) para textos como «Estado:» delante de la etiqueta. |
| Tamaños táctiles | 44 × 44 px mínimo en botones, enlaces de menú y casillas (se amplía el área con padding). |

- **Motivo**: cubre los criterios de WCAG 2.1 AA que el rediseño toca (1.3.1, 1.4.1, 1.4.3, 1.4.4, 1.4.10, 1.4.11, 2.1.1, 2.4.1, 2.4.7, 2.5.5 como buena práctica, 2.3.3 como buena práctica) sin añadir JavaScript.

## V10. PDF con el mismo sistema visual — FR-217, FR-211, US2 (Clarifications Q4)

- **Decisión**:
  - `pdf.py` importa WeasyPrint **solo dentro de** `generar_pdf()`, para que el resto del módulo (y los tests que lo usan) no dependan de las librerías del sistema de WeasyPrint.
  - `pdf.py` construye una vez (caché) el CSS común: contenido de `tokens.css` con las URLs de las fuentes sustituidas por URIs `data:font/woff2;base64,…`. `generar_pdf` no cambia su política: solo `data:` (D6).
  - `pdf.html` recibe ese CSS (`estilos_comunes`) y lo inserta antes de sus reglas propias, que solo usan `var(--…)`. Sus reglas en `pt`/`mm` se derivan de la escala (V3) y del espaciado (V4).
  - Color de marca solo en: título «PRESUPUESTO» con el número, cabecera de la tabla de líneas (texto o borde inferior) y la línea sobre el «Total» (Q4). Resto en `--color-texto` y `--color-texto-suave`; separadores de fila en gris (sin fondos alternos de color: mejor en blanco y negro y ahorra tinta).
  - Logo en una caja de 60 × 25 mm con `object-fit: contain`; sin logo, el bloque del emisor ocupa el ancho (sin hueco).
  - **Contenido idéntico**: mismos bloques, textos y orden del [contrato del PDF de la 001](../001-presupuestos-pro/contracts/pdf-presupuesto.md). Detalle visual en [contracts/pdf-diseno.md](./contracts/pdf-diseno.md).
- **Motivo**: una sola fuente de verdad para app y PDF sin abrir el generador a archivos locales.
- **Alternativas descartadas**: permitir `file://` al generador para cargar fuentes y CSS (abre lecturas de disco; D6 eligió solo `data:`); mantener DejaVu en el PDF (contrario a Q3).
- **Coste**: insertar las fuentes añade ~550 KB al HTML que procesa WeasyPrint; el PDF final solo incrusta los glifos usados (subconjunto), por lo que su tamaño apenas cambia. Tiempo de generación: se mide en la verificación (debe seguir por debajo de 3 s, objetivo de rendimiento de la 001; se comprueba con un presupuesto de 40 líneas).

## V11. Cambios de marcado permitidos — FR-215

- Se pueden cambiar clases, envoltorios, encabezados y atributos de accesibilidad de todas las plantillas y fragmentos.
- **No** se cambian: rutas, métodos, nombres de campos de formulario, atributos `hx-*` (destinos, disparadores, intercambios), ids que usan HTMX o `app.js` (`#totales`, `#fechas`, `#cliente-actual`, `#error-*`, `#lista-*`, `#menu-lateral`, `#aviso-conexion`…), textos existentes (salvo los nuevos de la spec) ni respuestas de error.
- `app.js` solo cambia si una clase que usa se renombra (`.boton-menu`, `.menu-fondo`, `.boton-volver`, `.form-cliente`, `.campo-verificado`, `.selector-pais`, `.pais-fijo`, `.pais-revisar`): se conservan esos nombres para no tocarlo.

## V12. Verificación y tests — SC-201 a SC-210, constitución IV

Se mantiene la política de la 001 (D20): pytest para reglas de dominio, acceso, datos y exportación; lo visual se comprueba en la app con [quickstart.md](./quickstart.md). Tests nuevos, cada uno justificado:

| Test | Por qué es automático |
|---|---|
| `tests/dominio/test_estado.py` | Regla de dominio (V7): prioridad Caducado, límite del día, nulos. |
| `tests/test_pdf_contenido.py` | Protege FR-215/SC-206 («0 diferencias de contenido»): renderiza `pdf.html` (sin generar el PDF) para dos presupuestos de ejemplo y compara el **texto** visible, normalizado, con una referencia guardada **antes** del rediseño. También comprueba que ninguna etiqueta de estado aparece en el PDF (FR-211) y que el CSS común incluye las fuentes en `data:`. |
| `tests/test_paleta.py` | Protege SC-202 y SC-209: lee `tokens.css`, comprueba que cada par de [contracts/sistema-visual.md](./contracts/sistema-visual.md#pares-de-contraste) cumple su contraste mínimo y que `estilos.css` y `pdf.html` no contienen colores hexadecimales propios (todo `var(--…)`). |

- Los 106 tests actuales deben seguir pasando sin tocar sus aserciones de reglas (SC-208); solo se ajustarían si alguno comprueba un texto o marcado que el rediseño cambie de forma permitida.
- Contraste, teclado, zoom, lector de pantalla y PDF impreso: [quickstart.md](./quickstart.md) con herramientas gratuitas del navegador.

---

No queda ningún «NEEDS CLARIFICATION».
