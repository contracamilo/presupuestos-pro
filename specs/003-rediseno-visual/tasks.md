---

description: "Lista de tareas de PresupuestosPro v1.2 — Rediseño visual profesional y accesible"
---

# Tasks: PresupuestosPro v1.2 — Rediseño visual profesional y accesible

**Input**: documentos de diseño de `/specs/003-rediseno-visual/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md) (V1–V12), [data-model.md](./data-model.md), [contracts/](./contracts/) ([sistema-visual.md](./contracts/sistema-visual.md), [estados.md](./contracts/estados.md), [pdf-diseno.md](./contracts/pdf-diseno.md)), [quickstart.md](./quickstart.md)

**Tests**: research.md V12 pide tres tests nuevos y los justifica: `tests/dominio/test_estado.py` (regla de dominio), `tests/test_pdf_contenido.py` (contenido del PDF idéntico, FR-215/SC-206) y `tests/test_paleta.py` (contrastes y «todo con tokens», SC-202/SC-209). Lo demás se verifica en la app con [quickstart.md](./quickstart.md) (constitución, principio IV).

**Organization**: tareas agrupadas por historia de usuario; cada historia se puede implementar, verificar y entregar por separado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede hacer en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: historia de usuario de la spec (US1–US4)

## Path Conventions

Proyecto Python único de la 001: `presupuestos/` (aplicación), `tests/`. **No se añade ninguna dependencia.** Restricciones que aplican a **todas** las tareas:

- **No cambian** (FR-215, research V11): rutas, métodos, respuestas, nombres de campos de formulario, atributos `hx-*`, ids que usan HTMX o `app.js` (`#totales`, `#fechas`, `#cabecera`, `#lineas`, `#catalogo`, `#cliente-actual`, `#ficha-cliente`, `#nuevo-cliente`, `#resultados-cliente`, `#lista-presupuestos`, `#lista-clientes`, `#error-*`, `#linea-*`, `#servicio-*`, `#menu-lateral`, `#aviso-conexion`), textos visibles existentes ni datos.
- **Clases que usa `app.js`** (no renombrar): `boton-menu`, `menu-fondo`, `menu-lateral`, `menu-abierto`, `boton-volver`, `form-cliente`, `campo-verificado`, `selector-pais`, `pais-fijo`, `pais-revisar`, `con-menu`.
- **Clases que generan las rutas en Python** (se mantienen y se estilan como mensaje de error, sin tocar el Python): `error` (`app.py::_error`, `rutas/presupuestos.py::_error`) y `errores` (`rutas/clientes.py::_errores_html`).
- **CSP**: `style-src 'self'` prohíbe atributos `style="…"` y `<style>` en las plantillas de la app (sí se permiten en `pdf.html`, que no pasa por el navegador). Nada de JavaScript en línea.
- **Valores visuales**: ningún color, tamaño de letra ni separación escritos a mano fuera de `presupuestos/static/tokens.css` ([sistema-visual.md, «Regla de oro»](./contracts/sistema-visual.md#regla-de-oro)).
- Textos nuevos en español de España: solo los de [sistema-visual.md, «Textos nuevos»](./contracts/sistema-visual.md#textos-nuevos-fr-215).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: fijar el punto de partida y la referencia del PDF **antes** de tocar nada visual.

- [X] T001 Ejecutar `pytest` desde la raíz del repositorio y confirmar que pasan los 106 tests de la 002 (anotar el resultado; si alguno falla, parar y avisar)
- [X] T002 Primero, en `presupuestos/pdf.py`, mover `from weasyprint import HTML, URLFetcher` **dentro** de `generar_pdf()` (mismo comportamiento; así importar el módulo no exige las librerías del sistema de WeasyPrint y los tests corren igual en macOS sin `DYLD_FALLBACK_LIBRARY_PATH` que en Docker; comentario en español explicando el motivo). Después, crear `tests/test_pdf_contenido.py` y las referencias `tests/referencias/pdf_a.txt` y `tests/referencias/pdf_b.txt` **con el `pdf.html` actual (v1.1), antes de modificarlo** (plan, «Orden obligatorio»; research V12). El test usa los fixtures de `tests/conftest.py` (`titular`, `conn`) y: (a) inserta con SQL el perfil completo (nombre, NIF, dirección, email, teléfono), un logo PNG mínimo en `logos` y `perfil.logo_id`, y `ajustes.retencion_activa = 1`; (b) crea el **presupuesto A**: cliente empresa en `peninsula` con NIF, 3 líneas (`POST /presupuestos/{id}/lineas`), notas de dos líneas; y el **presupuesto B**: sin logo (`perfil.logo_id = NULL` antes de descargarlo), cliente empresa `ue` con `nif_iva_verificado = 1` (mención de inversión del sujeto pasivo), 40 líneas, una descripción de 300 caracteres y precios que den un total ≥ 1.000.000,00 €; (c) captura el HTML que se manda al generador con `monkeypatch.setattr("presupuestos.pdf.generar_pdf", lambda html: html.encode())` y `GET /presupuestos/{id}/pdf` (gracias al cambio anterior, el test no carga WeasyPrint); (d) extrae el **texto visible** (quita `<style>…</style>`, `<title>…</title>` y todas las etiquetas con `html.parser` de la biblioteca estándar, desescapa entidades y colapsa espacios) y lo compara con la referencia. Si existe la variable de entorno `REGENERAR_REFERENCIAS=1`, escribe la referencia en lugar de compararla. Generar ahora las dos referencias con `REGENERAR_REFERENCIAS=1 pytest tests/test_pdf_contenido.py`, revisar a ojo que contienen los 8 bloques del contrato del PDF de la 001 y volver a ejecutar sin la variable: debe pasar
- [X] T003 [P] Añadir la tipografía Inter (research V2): descargar una vez el archivo oficial de la versión 4.1 (`https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip`) en el directorio temporal, extraer de `web/` los archivos `Inter-Regular.woff2`, `Inter-Italic.woff2`, `Inter-SemiBold.woff2` e `Inter-Bold.woff2` a `presupuestos/static/fuentes/` y su `LICENSE.txt` como `presupuestos/static/fuentes/OFL.txt`. Comprobar con `fontTools` (ya instalado con WeasyPrint) que cada archivo contiene los glifos de `á é í ó ú Á É Í Ó Ú ñ Ñ ü Ü ¿ ¡ € · — « » −` y la característica OpenType `tnum`; anotar el tamaño de cada archivo. Comprobar que `pyproject.toml` incluye `static/*` en `package-data` y, si `static/fuentes/*` no queda incluido por ese patrón, añadir `"static/fuentes/*"` a la lista

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: el archivo único de tokens y la capa base de estilos de la que beben todas las historias.

**⚠️ CRITICAL**: ninguna historia puede empezar hasta terminar esta fase.

- [X] T004 Crear `presupuestos/static/tokens.css` con **todos** los tokens de [contracts/sistema-visual.md](./contracts/sistema-visual.md#tokens) en `:root` (colores, incluidos `--color-marca-hover` y los diez `--estado-<valor>-texto` / `--estado-<valor>-fondo` de [contracts/estados.md](./contracts/estados.md#etiquetas); tipografía; tamaños `--texto-xs` a `--texto-2xl` en `rem`; pesos; interlineados; `--esp-1` a `--esp-7` en `rem`; radios; `--sombra`; `--ancho-contenido`; `--ancho-menu`; `--alto-control`), más `color-scheme: light;` en `:root` y cuatro `@font-face` de la familia `"Inter"` (400 normal, 400 italic, 600, 700) con `src: url("/static/fuentes/Inter-….woff2") format("woff2")` y `font-display: swap`. Comentario de cabecera en español: «Único lugar con colores, tamaños y separaciones de la app y del PDF (FR-202, FR-203)»
- [X] T005 [P] Crear `tests/test_paleta.py` (research V12): (a) lee `presupuestos/static/tokens.css`, extrae los colores `--nombre: #rrggbb` con una expresión regular y comprueba con la fórmula de contraste de WCAG 2.1 cada par de [sistema-visual.md, «Pares de contraste»](./contracts/sistema-visual.md#pares-de-contraste) con su mínimo (4,5 o 3); (b) comprueba que `presupuestos/static/estilos.css` y el bloque `<style>` de `presupuestos/templates/pdf.html` no contienen colores literales (`#` seguido de 3 o 6 cifras hexadecimales, `rgb(`, `rgba(`, `hsl(`), salvo dentro de comentarios; (c) comprueba que ninguna plantilla de `presupuestos/templates/` salvo `pdf.html` contiene `style="` ni `<style`. La parte (b) fallará hasta T007 y T026: es esperado
- [X] T006 En `presupuestos/templates/base.html`: añadir `<meta name="color-scheme" content="light">` y `<link rel="stylesheet" href="/static/tokens.css">` **antes** del enlace a `estilos.css`; mantener `lang="es"` (FR-214b) y el resto sin cambios
- [X] T007 Reescribir la **capa base** de `presupuestos/static/estilos.css` (los componentes llegan en US1), solo con `var(--…)`: reinicio (`box-sizing`, márgenes), `body` con `--fuente`, `--texto-base`, `--interlineado`, `--color-texto`, `--color-fondo` y `overflow-x: hidden`; jerarquía `h1`/`h2`/`h3` según [sistema-visual.md, «Jerarquía»](./contracts/sistema-visual.md#jerarquía-fr-204) (`h1` en `--texto-xl`, y `--texto-2xl` desde 1024 px); enlaces en `--color-marca`; `.suave` y nueva `.ayuda` (`--texto-sm`, `--color-texto-suave`); `.solo-lector` (patrón de recorte: `position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap`); `:focus-visible { outline: 3px solid var(--color-marca); outline-offset: 2px; }` y ninguna regla `outline: none`; `@media (prefers-reduced-motion: reduce)` que anula transiciones y animaciones; `main` con ancho `--ancho-contenido` y márgenes laterales `--esp-4` (`--esp-6` desde 1024 px); barra superior, menú lateral, `.grupo-menu`, `.menu-fondo` (`--color-superposicion`) y enlace `[aria-current="page"]` (fondo `--color-marca-claro`, borde izquierdo de marca y peso fuerte) con el **mismo comportamiento** de la 002 (punto de corte 1024 px, clases y transición sin cambios). Eliminar todas las variables y colores antiguos del principio del archivo
- [X] T008 [P] Crear `presupuestos/templates/fragmentos/_iconos.html` con la macro `icono(nombre)` que devuelve `<svg class="icono" aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">…</svg>` para seis nombres dibujados con formas simples (research V8): `lapiz` (Borrador), `avion` (Enviado, avión de papel), `reloj` (Caducado), `check` (Aceptado y mensajes de éxito), `aspa` (círculo con aspa: Rechazado y mensajes de error), `triangulo` (triángulo con «!»: avisos y errores de campo). Añadir a `estilos.css` la regla `.icono { flex: none; vertical-align: -0.125em; }`

**Checkpoint**: `pytest` en verde salvo la parte (b) de `test_paleta.py` si aún queda algún color en `pdf.html`; las pantallas se ven con Inter y la nueva paleta (aún sin componentes).

---

## Phase 3: User Story 1 - Una app con aspecto profesional y coherente en todas las pantallas (Priority: P1) 🎯 MVP

**Goal**: componentes comunes (botones, campos, mensajes, listas, totales) aplicados a todas las pantallas (FR-201 a FR-208, FR-216; research V6; [contracts/sistema-visual.md](./contracts/sistema-visual.md#componentes)).

**Independent Test**: quickstart A1–A10.

### Implementation for User Story 1

- [X] T009 [US1] Componentes en `presupuestos/static/estilos.css` según [sistema-visual.md, «Componentes»](./contracts/sistema-visual.md#componentes), «Espaciado» y «Puntos de corte», solo con tokens: **botones** `.boton` (principal), `.boton.secundario`, `.boton.peligro` (válidos en `<button>` y `<a>`), estado al pasar el ratón (`--color-marca-hover`; secundario y peligro con fondo `--color-fondo-2`), desactivado según [sistema-visual.md, «Estados interactivos»](./contracts/sistema-visual.md#estados-interactivos-todos-los-controles) (sin opacidad: fondo `--color-fondo-2`, texto `--color-texto-suave`, borde `--color-borde-control`, cursor no permitido), alto mínimo `--alto-control`; la regla antigua que estilaba todo `button` sin clase desaparece (`.boton-menu` conserva su aspecto propio de 44 × 44 px); `.boton-volver` como variante secundaria; **campos** (`input` de texto, email, password, search, date, `select`, `textarea`) con alto `--alto-control` (salvo `textarea`), borde 1 px `--color-borde-control`, radio `--radio-sm`; `label` encima (`--texto-sm`, peso medio), `label.casilla` en línea; `.error-campo` (`--texto-sm`, `--color-error`, `display:flex; gap: var(--esp-1)` para el icono) y `[aria-invalid="true"]` con borde 2 px `--color-error`; **mensajes** `.mensaje` con variantes `.exito`, `.aviso`, `.error` (fondo `--color-*-fondo`, texto `--color-*`, filete izquierdo de 4 px, icono y texto en `flex`), y las clases que generan las rutas `.error` y `.errores` con el mismo aspecto que `.mensaje.error`; **listas** `.lista > li` (tarjeta con borde `--color-borde`, radio `--radio-md`, relleno `--esp-3`, `--esp-4` desde 760 px) y `.fila`; **líneas** `.linea` (rejilla de la 002 conservando clases `.descripcion`, `.importe-linea`, `.botones`); **tabla** `.tabla` con `th` en estilo «etiqueta de grupo»; **importes** `.importe` y `.importe-linea` con `font-variant-numeric: tabular-nums`, a la derecha y sin cortes; **totales** `.totales` (filas `th[scope=row]` a la izquierda, importes a la derecha, fila `.total` en `--texto-lg` peso fuerte con borde superior de 2 px `--color-texto` y `--esp-2` de aire); utilidades existentes `.acciones`, `.rejilla` (dos columnas desde 640 px, `min-width: 0` en sus hijos), `.plegable`, `.resultados`, `.mencion`, `.entrar`, `.alta-usuario`, `.tipo-estado`, `.logo-previa` (caja máx. 15 rem × 6 rem con `object-fit: contain`); **separación** entre campos `--esp-4`, entre secciones `--esp-6`, entre botones `--esp-2`. Eliminar las reglas antiguas que este bloque sustituye
- [X] T010 [P] [US1] Crear `presupuestos/templates/fragmentos/_mensajes.html` con la macro `mensaje(tipo, texto, rol=None)` (`tipo` ∈ `exito`, `aviso`, `error`) que pinta `<p class="mensaje {{ tipo }}" role="…">{{ icono(…) }}<span class="solo-lector">Hecho: | Aviso: | Error: </span>{{ texto }}</p>` (`role="status"` para éxito y aviso, `role="alert"` para error, salvo que se indique `rol`), importando `icono` de `_iconos.html` (iconos `check`, `triangulo`, `aspa`)
- [X] T011 [P] [US1] Historial: en `presupuestos/templates/historial.html` y `presupuestos/templates/fragmentos/_historial_lista.html`, clase `boton` en «Nuevo presupuesto»; importe del elemento con clase `importe`; mensajes vacíos con `.suave`. Sin tocar `hx-*`, ids ni textos
- [X] T012 [P] [US1] Pantalla del presupuesto: en `presupuestos/templates/presupuesto.html`, `fragmentos/_cabecera.html`, `_fechas.html`, `_selector_cliente.html`, `_cliente_actual.html`, `_resultados_cliente.html`, `_lineas.html`, `_respuesta_lineas.html` y `_respuesta_cabecera.html`: clase `boton` (principal) en «Descargar PDF», «Añadir línea» y «Añadir desde el catálogo»; `boton secundario` en ↑ y ↓; `boton peligro` en «Eliminar» y «Borrar presupuesto»; los botones de `_resultados_cliente.html` con `boton secundario`; el bloque de requisitos para descargar (`#requisitos`) con el aspecto de `.mensaje.error` (manteniendo su `id`, su `role="alert"` y su lista); el aviso de cliente anonimizado de `_cliente_actual.html` como `mensaje('error', …)`. Sin tocar `hx-*`, ids, nombres de campo ni textos
- [X] T013 [P] [US1] Totales (FR-208): en `presupuestos/templates/fragmentos/_totales.html`, cada fila con `<th scope="row">` para el concepto y `<td class="importe">` para el importe; fila del total con clase `total`; aviso «Totales provisionales…» como `mensaje('aviso', …)`; añadir `<caption class="solo-lector">Totales del presupuesto</caption>`. Mismo `id="totales"`, mismo `hx-swap-oob` y mismos textos
- [X] T014 [P] [US1] Clientes: en `presupuestos/templates/clientes.html`, `cliente.html`, `fragmentos/_clientes_lista.html`, `_cliente_form.html` y `_ficha_cliente.html`: `boton` en «Guardar cliente»; `boton secundario` en «Archivar»; `boton peligro` en «Anonimizar cliente»; enlace «← Volver a clientes» con clase `boton-volver`; avisos de cliente archivado o eliminado con `mensaje('aviso', …)`; «Cambios guardados.» con `mensaje('exito', …)`. Mantener las clases de `app.js` (`form-cliente`, `campo-verificado`, `selector-pais`, `pais-revisar`)
- [X] T015 [P] [US1] Catálogo: en `presupuestos/templates/catalogo.html` y `fragmentos/_catalogo_lista.html`: `boton` en «Guardar» y «Añadir al catálogo»; `boton peligro` en «Archivar»
- [X] T016 [P] [US1] Perfil y ajustes: en `presupuestos/templates/perfil.html` y `ajustes.html`: `boton` en «Guardar perfil», «Subir logo»/«Cambiar logo» y «Guardar ajustes»; `boton peligro` en «Quitar logo»; mensajes `guardado`, `logo_guardado`, `logo_quitado` con `mensaje('exito', …)`; `error`, `error_logo` y la lista `errores` de ajustes con el aspecto de error (`mensaje('error', …)` o `<ul class="errores" role="alert">`); textos de ayuda (`.suave` bajo campos) pasan a `.ayuda`
- [X] T017 [P] [US1] Cuentas: en `presupuestos/templates/usuarios.html`, `mi_cuenta.html`, `entrar.html` y `crear_titular.html`: `boton` en «Dar de alta», «Cambiar contraseña», «Entrar» y «Crear cuenta»; `boton secundario` en «Restablecer contraseña»; `boton peligro` en «Dar de baja»; `summary` de «Añadir usuario» con `boton`; ayudas «Mínimo 10 caracteres» con `.ayuda`; cada `.error-campo` precedido de `icono('triangulo')`; mensajes de éxito y avisos con `mensaje(…)`. Mantener ids `error-*`/`ayuda-*` y los `aria-describedby`
- [X] T018 [P] [US1] Página de error: en `presupuestos/templates/error.html`, el enlace «Volver al historial» con clase `boton secundario`; el mensaje con `.suave` o `mensaje('error', …)` según contexto, sin cambiar textos
- [X] T019 [US1] Revisar con un navegador a 360 px, 800 px y 1280 px las 13 pantallas (quickstart A1–A8) y corregir en `presupuestos/static/estilos.css` cualquier desbordamiento horizontal, salto de jerarquía o diferencia de aspecto entre pantallas; comprobar que no queda ningún `<button>` sin variante (`grep -n "<button" presupuestos/templates -r` y revisar que todos llevan `boton`, `boton-menu` o son el `summary`)

**Checkpoint**: quickstart A1–A10 en verde; la app funciona igual que en la 002.

---

## Phase 4: User Story 2 - Un PDF que el cliente perciba como profesional (Priority: P1)

**Goal**: mismo sistema visual en el PDF, contenido idéntico (FR-201, FR-208, FR-211, FR-214b, FR-217; research V10; [contracts/pdf-diseno.md](./contracts/pdf-diseno.md)).

**Independent Test**: `pytest tests/test_pdf_contenido.py` y quickstart B1–B12.

### Implementation for User Story 2

- [X] T020 [US2] En `presupuestos/pdf.py`, añadir `estilos_comunes() -> str` con caché (`functools.lru_cache`), sin importar WeasyPrint (el import sigue dentro de `generar_pdf`, T002): lee `presupuestos/static/tokens.css` y sustituye cada `url("/static/fuentes/<archivo>.woff2")` por `url("data:font/woff2;base64,<contenido>")` leyendo el archivo de `presupuestos/static/fuentes/`. `generar_pdf` y su `URLFetcher(allowed_protocols={"data"}, …)` **no cambian** (D6 de la 001). Comentario en español explicando por qué se insertan las fuentes en lugar de abrir el generador a archivos locales
- [X] T021 [US2] En `presupuestos/rutas/presupuestos.py::descargar_pdf`, pasar `estilos_comunes=estilos_comunes()` al `render` de `pdf.html` (importado de `presupuestos.pdf` dentro de la función, como ya se hace con `generar_pdf`, para no cargar WeasyPrint al arrancar). No pasar `estado` a la plantilla (FR-211)
- [X] T022 [US2] Rehacer el `<style>` de `presupuestos/templates/pdf.html` según [contracts/pdf-diseno.md](./contracts/pdf-diseno.md): primero `{{ estilos_comunes|safe }}` y después reglas propias que solo usan `var(--…)` (más `mm`/`pt` para medidas de página, que no son colores ni escalas de la app): `@page` A4 con márgenes 16 mm × 18 mm; `body` con `var(--fuente)` a 9,5 pt; cabecera en dos columnas con caja del logo máx. 60 × 25 mm y `object-fit: contain`, y sin logo el emisor ocupa la cabecera (clase `sin-logo` en el contenedor cuando `logo_uri` está vacío, en lugar de la celda vacía actual); título «PRESUPUESTO {{ p.numero }}» en 18 pt peso fuerte y `--color-marca`; bloque del cliente con etiqueta en mayúsculas `--color-texto-suave` y filete izquierdo gris de 1 pt (`--color-borde-control`) sin fondo de color; tabla de líneas con `<th scope="col">`, cabecera en mayúsculas `--color-marca` y filete inferior de marca, `thead { display: table-header-group }`, filas con separador `--color-borde`, `tr { break-inside: avoid }`, columnas numéricas a la derecha con `font-variant-numeric: tabular-nums`; desglose a la derecha con `<th scope="row">`, «Total» en 13 pt peso fuerte con filete superior de 1,5 pt de `--color-marca`, `break-inside: avoid`; mención en cursiva `--color-texto-suave`; notas con título en peso medio. **El color de marca solo en esos tres sitios** (Q4). Mantener `<html lang="es">` y **exactamente** los mismos textos, bloques y orden
- [X] T023 [US2] Ampliar `tests/test_pdf_contenido.py`: además de comparar con las referencias de T002 (que deben seguir pasando **sin regenerarlas**), comprobar que el HTML capturado contiene `data:font/woff2;base64,` y `font-family` con `Inter`, que no contiene `/static/` ni `http` y que no contiene ninguna de las palabras «Borrador», «Enviado», «Caducado», «Aceptado», «Rechazado» (FR-211). Ejecutar `pytest tests/test_pdf_contenido.py tests/test_paleta.py`
- [X] T024 [US2] Descargar desde la app (con `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` en macOS) los presupuestos de quickstart P1 y P4, abrirlos y recorrer quickstart B2–B12: jerarquía, acentos de color, tabla, paginación, logo ancho y sin logo, impresión en escala de grises, fuente Inter en las propiedades del documento y tiempo de descarga de P4 < 3 s; corregir en `presupuestos/templates/pdf.html` lo que falle (sin tocar textos)

**Checkpoint**: tests del PDF en verde; quickstart B en verde.

---

## Phase 5: User Story 3 - Ver de un vistazo el estado de cada presupuesto (Priority: P2)

**Goal**: etiquetas Borrador / Enviado / Caducado deducidas sin guardar nada; Aceptado y Rechazado solo diseñadas (FR-209, FR-209a, FR-210, FR-211; research V7; [data-model.md](./data-model.md#estado-del-presupuesto--dato-deducido-no-guardado-fr-209-v7); [contracts/estados.md](./contracts/estados.md)).

**Independent Test**: quickstart C1–C8.

### Tests for User Story 3

- [X] T025 [P] [US3] Crear `tests/dominio/test_estado.py` con la tabla de [data-model.md](./data-model.md#regla-en-este-orden-el-primero-que-se-cumple-gana--clarifications-q2): `estado(None, "2026-12-01", "2026-11-14") == "borrador"`; `estado('{"nombre": "X"}', "2026-12-01", "2026-11-14") == "enviado"`; `estado(None, "2026-11-13", "2026-11-14") == "caducado"`; `estado('{…}', "2026-11-13", "2026-11-14") == "caducado"` (Caducado gana); validez = hoy → no caducado (`estado(None, "2026-11-14", "2026-11-14") == "borrador"`); `ETIQUETAS == {"borrador": "Borrador", "enviado": "Enviado", "caducado": "Caducado", "aceptado": "Aceptado", "rechazado": "Rechazado"}`; `MOSTRABLES == ("borrador", "enviado", "caducado")`

### Implementation for User Story 3

- [X] T026 [P] [US3] Crear `presupuestos/dominio/estado.py` (módulo puro, sin web ni BD): `ETIQUETAS` (las cinco, en este orden), `MOSTRABLES = ("borrador", "enviado", "caducado")` y `estado(emisor_congelado: str | None, fecha_validez: str, hoy: str) -> str` con la regla «`"caducado"` si `fecha_validez < hoy`; si no, `"enviado"` si `emisor_congelado` no es `None` ni vacío; si no, `"borrador"`» (fechas en `AAAA-MM-DD`, comparables como texto). Docstring en español que cite FR-209 y la prioridad de la sesión de aclaraciones. Aceptado y Rechazado no se devuelven nunca (FR-209a)
- [X] T027 [US3] En `presupuestos/rutas/presupuestos.py`: en `historial`, añadir `p["estado"] = estado.estado(p["emisor_congelado"], p["fecha_validez"], fechas.hoy())` a cada fila (calcular `hoy` una vez fuera del bucle); en `_contexto`, añadir `"estado": estado.estado(datos["presupuesto"]["emisor_congelado"], datos["presupuesto"]["fecha_validez"], fechas.hoy())`. No cambiar nada más (consultas, respuestas, PDF)
- [X] T028 [P] [US3] Crear `presupuestos/templates/fragmentos/_estado.html` con la macro `etiqueta_estado(valor)` según [contracts/estados.md, «Marcado»](./contracts/estados.md#marcado): `<span class="estado {{ valor }}"><span class="solo-lector">Estado: </span>{{ icono(…) }}{{ ETIQUETAS[valor] }}</span>` con el icono de cada estado (`lapiz`, `avion`, `reloj`, `check`, `aspa`); registrar `ETIQUETAS` de `dominio/estado.py` como global de Jinja `etiquetas_estado` en `presupuestos/rutas/__init__.py` y usarla en la macro
- [X] T029 [US3] Estilos de las etiquetas en `presupuestos/static/estilos.css`: `.estado` (`inline-flex`, `gap: var(--esp-1)`, `--texto-xs`, peso medio, relleno `--esp-1` × `--esp-2`, radio `--radio-sm`, borde 1 px del color del texto, alto mínimo 1,5 rem, `white-space: nowrap`) y las cinco variantes con `--estado-<valor>-texto` y `--estado-<valor>-fondo`; `.estado.borrador` con borde **discontinuo**; `.estado.caducado` con texto en **cursiva** (FR-210)
- [X] T030 [US3] Mostrar la etiqueta: en `presupuestos/templates/fragmentos/_historial_lista.html`, `etiqueta_estado(p.estado)` junto al número de cada presupuesto; en `presupuestos/templates/presupuesto.html`, `<span id="estado-presupuesto">{{ etiqueta_estado(estado) }}</span>` junto al número en el `h1` (o justo debajo en móvil si no cabe); en `presupuestos/templates/fragmentos/_respuesta_cabecera.html`, añadir `<span id="estado-presupuesto" hx-swap-oob="true">{{ etiqueta_estado(estado) }}</span>` para que cambie al editar la fecha de validez sin recargar (US3 AS5). Comprobar que `presupuestos/rutas/clientes.py` (que reutiliza `_contexto` al dar de alta un cliente desde el presupuesto) sigue funcionando: `estado` llega en el contexto
- [X] T031 [US3] Recorrer quickstart C1–C7 en el navegador (incluida la simulación de escala de grises) y corregir lo que falle

**Checkpoint**: `pytest tests/dominio` en verde; quickstart C en verde; el PDF sigue sin estado (T023).

---

## Phase 6: User Story 4 - Usar la app con teclado, lector de pantalla o con dificultades de visión (Priority: P2)

**Goal**: WCAG 2.1 AA en lo que el rediseño toca (FR-212 a FR-214b; research V9).

**Independent Test**: quickstart D1–D10.

### Implementation for User Story 4

- [X] T032 [US4] «Saltar al contenido» (FR-213): en `presupuestos/templates/base.html`, como primer hijo de `<body>` cuando hay `usuario`, `<a class="saltar" href="#contenido">Saltar al contenido</a>`; `<main id="contenido" tabindex="-1">`. En `presupuestos/static/estilos.css`, `.saltar` fuera de la vista hasta `:focus` (entonces arriba a la izquierda, por encima del menú, con aspecto de botón principal) y `main:focus { outline: none; }` **solo** para `main` (no es un control). Comprobar que `app.js` no depende del marcado de `<main>`
- [X] T033 [P] [US4] Encabezados (FR-214): revisar todas las plantillas de `presupuestos/templates/` y `fragmentos/` para que haya **un único `h1`** por pantalla, secciones con `h2` y subsecciones con `h3` sin saltos de nivel; convertir en encabezado los títulos que hoy son `<p><strong>` (p. ej. «No se puede descargar el PDF:» en `presupuesto.html`) sin cambiar su texto; anotar en el informe final qué plantillas cambian
- [X] T034 [US4] Área táctil y anchura mínima (FR-214, FR-214a) en `presupuestos/static/estilos.css`: alto y ancho mínimos `--alto-control` en `.boton`, enlaces del menú, `summary`, `label.casilla` (el área incluye el texto) y botones ↑ ↓ de las líneas; `overflow-wrap: anywhere` en nombres de cliente, descripciones de línea y emisor; en rejillas y filas `min-width: 0`; probar a 320 px y con zoom al 200 % en 1280 px y con letra del navegador a 20 px (quickstart D5, D6, D10), y corregir lo que se corte o desborde
- [X] T035 [US4] Recorrido de accesibilidad (quickstart D1–D4, D7–D9): solo teclado por el flujo principal, contraste de cada componente con el comprobador del navegador (los valores deben coincidir con `test_paleta.py`), lector de pantalla en historial y presupuesto (un `h1`, encabezados en orden, «Estado: …» leído, cabeceras de totales anunciadas) y «Reducir movimiento». Corregir lo que falle en las plantillas o en `estilos.css`

**Checkpoint**: quickstart D1–D10 en verde.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T036 Limpieza de `presupuestos/static/estilos.css`: eliminar reglas y clases que ya no usa ninguna plantilla (`.ok`, estilos antiguos de `button` sin clase, etc.; comprobar cada una con `grep -rn` en `presupuestos/templates` y en `presupuestos/rutas` antes de borrarla) y ordenar el archivo por secciones comentadas (base · disposición · menú · componentes · estados · utilidades · accesibilidad)
- [X] T037 Ejecutar `pytest` completo y confirmar que pasan los 106 tests anteriores y los nuevos (`test_estado`, `test_paleta`, `test_pdf_contenido`) (SC-208)
- [ ] T038 Recorrer [quickstart.md](./quickstart.md) completo (A–E), incluidas las pruebas con 5 personas C8 (SC-205) y B13 (SC-206) y la impresión de pantallas E7, incluidas la regresión E5 con las guías de la 001 y la 002 y los pasos técnicos E1–E4 y E6, en un navegador a 320, 360, 800 y 1280 px; anotar cualquier fallo y corregirlo antes de dar la entrega por terminada (constitución, «Verificación de cada entrega»)
- [X] T039 Revisar la entrega contra los principios I–V de `.specify/memory/constitution.md` y FR-215/FR-218: ninguna dependencia nueva en `pyproject.toml`; ninguna petición a otro dominio (inspector → Red); ningún `style="` ni JS en línea en las plantillas de la app; ninguna ruta, campo de formulario, `hx-*`, id usado por HTMX/`app.js` ni texto existente cambiado (comparación con la copia previa de `copias/antes-de-003/`, revisando solo plantillas); `PRAGMA user_version` sigue en 2; textos nuevos solo los de [sistema-visual.md](./contracts/sistema-visual.md#textos-nuevos-fr-215)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 primero. **T002 debe terminar antes de cualquier cambio en `pdf.html`** (T022). T003 en paralelo con T002.
- **Foundational (Phase 2)**: depende de T003 (las fuentes que declara `tokens.css`). Bloquea todas las historias.
- **US1 (Phase 3)** y **US2 (Phase 4)**: dependen de la fase 2; pueden ir en paralelo (archivos distintos salvo `estilos.css`, que solo toca US1).
- **US3 (Phase 5)**: depende de la fase 2; T029 (estilos) después de T009 si se hace tras US1 (mismo archivo). La lógica (T025–T028) es independiente de US1 y US2.
- **US4 (Phase 6)**: conviene después de US1 (revisa el resultado de los componentes); T032 y T034 tocan `estilos.css`.
- **Polish (Phase 7)**: después de todas las historias que se entreguen.

### Puntos de contacto (archivos compartidos, en serie)

- `presupuestos/static/estilos.css`: T007 → T008 (regla `.icono`) → T009 → T019 → T029 → T032 → T034 → T036.
- `presupuestos/templates/presupuesto.html`: T012 → T030 → T033.
- `presupuestos/templates/fragmentos/_historial_lista.html`: T011 → T030.
- `presupuestos/templates/fragmentos/_respuesta_cabecera.html`: T012 → T030.
- `presupuestos/templates/base.html`: T006 → T032.
- `presupuestos/rutas/presupuestos.py`: T021 y T027 (bloques distintos; en serie).
- `tests/test_pdf_contenido.py`: T002 → T023.

### Within Each User Story

- US2: T020 → T021 → T022 → T023 → T024.
- US3: T025 y T026 en paralelo (test primero, debe fallar) → T027 → T028 → T029 → T030 → T031.
- US1: T009 y T010 antes de las plantillas (T011–T018), que van en paralelo entre sí → T019.

### Parallel Opportunities

- Setup: T002 y T003.
- Foundational: T005 y T008 en paralelo con T004/T006 (archivos distintos).
- US1: T011, T012, T013, T014, T015, T016, T017 y T018 a la vez (grupos de plantillas distintos), tras T009–T010.
- US3: T025, T026 y T028.
- Historias US2 y US3 (lógica) en paralelo con US1.

---

## Parallel Example: User Story 1

```bash
# Tras T009 (componentes) y T010 (macro de mensajes), cada grupo de plantillas por separado:
Task: "T011 historial.html, _historial_lista.html"
Task: "T012 presupuesto.html y fragmentos del presupuesto"
Task: "T013 _totales.html"
Task: "T014 clientes.html, cliente.html, _cliente_form.html, _ficha_cliente.html, _clientes_lista.html"
Task: "T015 catalogo.html, _catalogo_lista.html"
Task: "T016 perfil.html, ajustes.html"
Task: "T017 usuarios.html, mi_cuenta.html, entrar.html, crear_titular.html"
Task: "T018 error.html"
```

## Parallel Example: User Story 3

```bash
Task: "T025 tests/dominio/test_estado.py"
Task: "T026 presupuestos/dominio/estado.py"
Task: "T028 fragmentos/_estado.html"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1 (T001–T003): punto de partida, referencia del PDF y fuentes.
2. Phase 2 (T004–T008): tokens y capa base.
3. Phase 3 (US1): componentes en todas las pantallas.
4. **Parar y verificar**: quickstart A y una pasada rápida de la 002.
5. Entregable: la app con el nuevo aspecto; el PDF todavía como en v1.1 (sigue siendo correcto).

### Incremental Delivery

1. US1 → app coherente y profesional.
2. US2 → PDF con la misma imagen (contenido protegido por T002/T023).
3. US3 → etiquetas de estado.
4. US4 → pasada de accesibilidad (teclado, lector, zoom, área táctil).
5. Phase 7 → verificación completa.

Cada historia se verifica con su bloque de quickstart antes de pasar a la siguiente.

---

## Notes

- [P] = archivos distintos, sin dependencias pendientes.
- Cada tarea cita el requisito o la decisión que la justifica; nada fuera de la spec (principio III): sin modo oscuro, sin filtros por estado, sin marcar Aceptado/Rechazado.
- `app.js` no se toca: si una tarea parece exigirlo, revisar antes si basta con conservar la clase que usa.
- El proyecto no es un repositorio git: antes de empezar, guardar una copia de `presupuestos/templates/` y `presupuestos/static/` (p. ej. en `copias/antes-de-003/`) para la comparación de T039.
- El checklist `checklists/diseno-accesibilidad.md` tiene puntos sin marcar: `/speckit-implement` preguntará antes de empezar; revisarlo o decidir continuar.
