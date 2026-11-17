---

description: "Lista de tareas de PresupuestosPro v1.3 — Exportar en un .zip"
---

# Tasks: PresupuestosPro v1.3 — Exportar en un .zip

**Input**: documentos de diseño de `/specs/004-exportar-zip/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md) (E1–E11), [data-model.md](./data-model.md), [contracts/](./contracts/) ([rutas-http.md](./contracts/rutas-http.md), [archivo-exportacion.md](./contracts/archivo-exportacion.md)), [quickstart.md](./quickstart.md)

**Tests**: research.md E11 los pide y los justifica (se capturan sin WeasyPrint, como `tests/test_pdf_contenido.py`): `tests/dominio/test_formato_fechas_nombre.py` (nombres), `tests/test_exportar_zip.py` (nuevo) y ajustes en `tests/test_exportar_copia.py` y `tests/test_acceso.py`. La ventana, el estado «Preparando…» y la descarga real se verifican en la app con [quickstart.md](./quickstart.md) (constitución, principio IV).

**Organization**: tareas agrupadas por historia de usuario; cada historia se puede implementar, verificar y entregar por separado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede hacer en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: historia de la spec (US1, US1b, US2, US3)

## Path Conventions

Proyecto Python único de la 001: `presupuestos/` (aplicación), `tests/`. **No se añade ninguna dependencia.** Restricciones que aplican a **todas** las tareas:

- **No cambian**: esquema de datos (`user_version` sigue en 2), cálculos, estados, contenido del PDF, numeración, cuentas, la orden `python -m presupuestos copia`, y el nombre de la descarga individual de PDF (`nombre_pdf`, FR-022 de la 001).
- **CSP**: `style-src 'self'` y `script-src 'self'`: nada de `style="…"`, `<style>` ni JavaScript en línea en las plantillas de la app. El JS va en `presupuestos/static/app.js`.
- **Valores visuales**: ningún color, tamaño ni separación escritos a mano en `estilos.css`: solo `var(--…)` de `presupuestos/static/tokens.css` (003).
- **No renombrar** ids ni clases que usa `app.js` (`#menu-lateral`, `#aviso-conexion`, `#lista-presupuestos`, `boton-menu`, `menu-fondo`, etc.).
- Textos nuevos en español de España, exactamente los de [contracts/rutas-http.md](./contracts/rutas-http.md).
- En los tests, el PDF se captura con `monkeypatch.setattr("presupuestos.pdf.generar_pdf", lambda html: html.encode())` (como `tests/test_pdf_contenido.py`). La ruta de exportación debe importar `generar_pdf` **dentro** de la función, como hace `descargar_pdf`, para que ese parche funcione.

---

## Phase 1: Setup

**Purpose**: fijar el punto de partida.

- [X] T001 Ejecutar `.venv/bin/pytest` desde la raíz y confirmar que pasan todos los tests actuales (anotar el número; si alguno falla, parar y avisar)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: piezas que necesitan todas las historias. Ninguna historia puede empezar antes.

**⚠️ CRITICAL**: no empezar las fases 3+ hasta terminar esta.

- [X] T002 [P] En `presupuestos/dominio/nombre_archivo.py` añadir `limpiar_nombre(texto: str) -> str` y `nombre_pdf_zip(numero: str, nombre_cliente: str) -> str` (research E8, FR-307, FR-308), **sin tocar `nombre_pdf`**. `limpiar_nombre`: sustituye por un espacio cada uno de `/ \ : * ? " < > |` y los caracteres de control, colapsa espacios repetidos, quita espacios y puntos de los extremos, **conserva tildes y «ñ»**, y recorta a **80 caracteres** como máximo (volviendo a quitar espacios y puntos finales). `nombre_pdf_zip` devuelve `f"{numero} - {limpio}.pdf"` y, si `limpio` queda vacío, usa `«Sin cliente»`. Añadir tests en `tests/dominio/test_formato_fechas_nombre.py`: `«Diseño/Web S.L.»` → `PRE-2026-001 - Diseño Web S.L.pdf`; `«Estudio García»` conserva la tilde; `«A:B*C?»`; nombre vacío o solo `///` → `Sin cliente`; nombre de 150 caracteres → cliente de ≤ 80; y que `nombre_pdf` sigue devolviendo lo de siempre (`PRE-2026-001_Estudio-Garcia.pdf`)
- [X] T003 En `presupuestos/rutas/presupuestos.py` extraer de `descargar_pdf` una función `html_pdf(conn, datos) -> str` (research E7) con **exactamente** lo que hoy hay entre «emisor efectivo» y el `render` de `pdf.html`: lectura del logo como URI `data:`, `estilos_comunes()`, y `plantillas.get_template("pdf.html").render(...)`; `descargar_pdf` conserva su orden (comprobar requisitos → fijar emisor → `html_pdf` → `generar_pdf` → `Response` con `nombre_pdf`). Comportamiento idéntico: ejecutar `tests/test_pdf_contenido.py` y todo `pytest`, que deben seguir en verde sin cambiar las referencias de `tests/referencias/`
- [X] T004 [P] En `presupuestos/rutas/exportar.py` convertir `datos_exportacion(conn)` en `datos_exportacion(conn, ids: list[int] | None = None) -> dict` (research E9, contracts/archivo-exportacion.md): añadir la clave `"alcance"` (`"completo"` si `ids is None`, `"seleccion"` si no), con `version` en 2. Con `ids`: `presupuestos` solo los de `ids` (con `lineas` y `emisor_congelado`), `clientes` solo los referenciados por ellos, `logos` solo los `logo_id` de sus `emisor_congelado`, `servicios` y `contadores` como `[]`, `perfil` y `ajustes` como `None`. Sin `ids` el resultado es el de hoy más `alcance`. Nunca incluir `usuarios`, `sesiones` ni `intentos_acceso`. Tests en `tests/test_exportar_zip.py` (archivo nuevo, con los fixtures `conn`, `titular` de `tests/conftest.py`): `datos_exportacion(conn)` conserva las 7 claves de `datos` y añade `alcance: "completo"`; con `ids=[x]` solo aparece ese presupuesto, su cliente y el logo de su emisor fijado, y `servicios == []`, `contadores == []`, `perfil is None`, `ajustes is None`
- [X] T005 En `presupuestos/rutas/exportar.py` añadir `presupuestos_exportables(conn) -> list[dict]` (research E6, spec «Presupuesto exportable»): devuelve, en el orden del historial (`fecha_emision DESC, numero DESC`), los presupuestos con `emisor_congelado IS NOT NULL` **y** `requisitos_descarga(perfil_efectivo, cliente, lineas) == []` (usar `db.cargar_presupuesto`), cada uno con `id`, `numero`, `cliente_nombre`, `estado` (con `estado.estado(...)`) y `fecha_emision`. Añadir también `resumen_exportacion(conn) -> dict` con `total` (todos los presupuestos), `exportables` (cuántos) y `solo_datos` (`total - exportables`). Tests en `tests/test_exportar_zip.py` con un escenario de 4 presupuestos: descargado válido, borrador, descargado con cliente anonimizado después, descargado válido caducado: la lista contiene solo el 1.º y el 4.º, y el resumen es `total=4, exportables=2, solo_datos=2`

**Checkpoint**: nombres, PDF reutilizable, archivo de datos y lista de exportables listos y probados.

---

## Phase 3: User Story 1 - Llevarme todos mis presupuestos de una vez (Priority: P1) 🎯 MVP

**Goal**: botón «Exportar…» → ventana con «Todo» → un único .zip con los PDF exportables y el archivo de datos.

**Independent Test**: [quickstart.md §A](./quickstart.md#a-exportar-todo-us1-sc-301-sc-302): con 3 presupuestos descargados, descargar el zip y comprobar nombres, contenido y que cada PDF coincide con su descarga individual.

### Tests for User Story 1

- [X] T006 [P] [US1] En `tests/test_exportar_zip.py` añadir tests de `POST /exportar` con `modo=todo` (PDF capturado con `monkeypatch`, escenario de 3 presupuestos descargados + 1 borrador): (a) 200, `Content-Type: application/zip`, `Content-Disposition` con `presupuestospro-copia-AAAA-MM-DD.zip` (fecha de `fechas.hoy()`); (b) el zip abre con `zipfile`, contiene exactamente 3 PDF `«PRE-… - cliente.pdf»` y un `presupuestospro-copia-AAAA-MM-DD.json`, y nada más; (c) el JSON tiene `alcance: "completo"` y los 4 presupuestos; (d) el cliente `«Diseño/Web S.L.»` da `Diseño Web S.L.` en el nombre; (e) sin sesión → 303 a `/entrar`; (f) una cuenta de asistente también puede exportar; (g) sin presupuestos → 422 con `{"error": "No hay presupuestos que exportar."}` y sin zip; (h) `modo` ausente o no válido → 422 `{"error": "Elige qué exportar."}`; (i) el HTML capturado de cada PDF del zip es **igual** al capturado en la descarga individual `GET /presupuestos/{id}/pdf` del mismo presupuesto (FR-304)

### Implementation for User Story 1

- [X] T007 [US1] En `presupuestos/rutas/exportar.py` sustituir `GET /exportar` por `POST /exportar` (research E3, E4, E5, contracts/rutas-http.md): leer `modo` e `ids` del formulario (`await request.form()`); en este paso solo `modo == "todo"` (la selección llega en US1b: de momento `seleccion` → 422 «Elige qué exportar.»). Con una transacción de lectura (`conn.execute("BEGIN")` … `conn.execute("ROLLBACK")` en `finally`) leer **todo** dentro de ella: `datos_exportacion(conn)`, `presupuestos_exportables(conn)` y, para cada uno, `db.cargar_presupuesto` + `html_pdf(conn, datos)` de la T003; después, **fuera de la transacción**, importar `generar_pdf` dentro de la función y generar los PDF. Armar el zip con `zipfile.ZipFile(BytesIO(), "w", ZIP_DEFLATED)`: primero el JSON (`json.dumps(..., ensure_ascii=False, indent=2)`), luego los PDF por número, con nombres de `nombre_pdf_zip` (T002). Sin presupuestos (`total == 0`) → 422 JSON. Cualquier excepción → 500 `{"error": "No se ha podido preparar la copia. Inténtalo de nuevo."}`. Respuesta 200 `application/zip` con `Content-Disposition: attachment; filename="presupuestospro-copia-{fechas.hoy()}.zip"`. **No escribir nada en la base de datos** (FR-305). Mantener `router = APIRouter(dependencies=[Depends(usuario_actual)])`. En esta misma tarea, para que la suite no quede en rojo, retirar los tests que usan `GET /exportar`: `test_exportacion_completa_y_sin_cuentas` de `tests/test_exportar_copia.py` (dejar `test_orden_copia`) y quitar `"/exportar"` de la lista de rutas GET protegidas de `tests/test_acceso.py` (línea ~162); su cobertura se rehace en la T012
- [X] T008 [US1] En `presupuestos/rutas/presupuestos.py::historial` pasar al contexto de la página completa (no al fragmento de búsqueda) `exportables=presupuestos_exportables(conn)` y `resumen=resumen_exportacion(conn)` (importándolos de `presupuestos.rutas.exportar`; si hay importación circular, mover ambas funciones a `presupuestos/db.py`)
- [X] T009 [US1] Crear `presupuestos/templates/fragmentos/_exportar_ventana.html` con un `<dialog id="ventana-exportar" aria-labelledby="exportar-titulo">` (research E1, contracts/rutas-http.md): título `<h2 id="exportar-titulo">Exportar</h2>`; si `resumen.total == 0` solo el aviso «No hay presupuestos que exportar» y un botón «Cerrar» (`<form method="dialog">`); si no, un `<form id="form-exportar" method="post" action="/exportar" data-exportables="{{ resumen.exportables }}">` con un `<fieldset>` y `<legend>`, un `<input type="radio" name="modo" value="todo" id="modo-todo" checked>` con su `<label>` «Todo», un botón «Cancelar» (`<form method="dialog">` aparte, clase `boton secundario`) y un botón `type="submit"` «Descargar .zip» (clase `boton`). Mensaje de error vacío: `<p id="exportar-error" class="error" role="alert" hidden></p>`. Incluirlo en `presupuestos/templates/historial.html` **fuera** de `#lista-presupuestos`, y añadir en la barra `acciones` un botón `type="button"` «Exportar…» (clase `boton secundario`, `id="abrir-exportar"`, `aria-haspopup="dialog"`) junto a «Nuevo presupuesto»
- [X] T010 [US1] En `presupuestos/static/app.js` añadir (IIFE existente, sin romper el resto) la lógica de la ventana: clic en `#abrir-exportar` → `document.getElementById("ventana-exportar").showModal()`; clic sobre el propio `<dialog>` (cuando `e.target` es el `dialog` y no un hijo) → `close()`; y el envío de `#form-exportar`: `preventDefault()`, `fetch("/exportar", {method: "POST", body: new FormData(form)})`, si `r.ok` leer `blob()`, crear un enlace `<a download>` con `URL.createObjectURL(blob)` y el nombre de `Content-Disposition` (`filename="…"`), pulsarlo, revocar la URL y cerrar la ventana; si no `ok`, leer el JSON y mostrar `error` en `#exportar-error` (quitando `hidden`). Delegar eventos en `document` como el resto del archivo para que siga funcionando tras HTMX
- [X] T011 [P] [US1] En `presupuestos/static/estilos.css` añadir estilos de `dialog#ventana-exportar` con variables de `tokens.css` (fondo, borde, radio, sombra, espaciado), `::backdrop` semitransparente con un token existente, ancho máximo con `max-width: min(32rem, calc(100vw - var(--espacio-…)*2))`, lista de selección con `max-height` y `overflow-y: auto`, objetivos táctiles de 44 × 44 px (como el resto de controles) y foco visible heredado; sin desplazamiento horizontal a 320 px. Ningún valor suelto: si falta un token, reutilizar el más cercano ya definido (no añadir tokens nuevos salvo necesidad probada y entonces en `tokens.css`)
- [X] T012 [US1] Retirar la exportación suelta (FR-314, research E10): quitar el `<li>` «Exportar» de `presupuestos/templates/base.html`; `test_exportacion_completa_y_sin_cuentas` ya se retiró en la T007 y su cobertura pasa a `tests/test_exportar_zip.py` (en esta tarea): añadir allí un test que descomprime el zip y comprueba que el JSON **no** contiene `hash_contrasena`, `usuarios`, ni el email de ninguna cuenta, y que `logos[0].datos_base64` y `tipo_documento` de los clientes siguen presentes); en `tests/test_acceso.py` añadir una comprobación `POST /exportar` sin sesión → 303 a `/entrar`, y añadir que `GET /exportar` con sesión devuelve 405 («Esta acción no está permitida»)
- [X] T013 [US1] Alinear la documentación del diseño con el comportamiento real de la T012: `GET /exportar` ya no existe como ruta, pero como `/exportar` sí existe para `POST`, FastAPI responde **405**, no 404. Comprobar que `specs/004-exportar-zip/contracts/rutas-http.md` (tabla «Cambios en rutas»), `research.md` (E3) y `quickstart.md` (paso D6) dicen 405 (ya corregidos en la pasada de `/speckit-analyze`; solo verificar contra el comportamiento real) y, si no, corregirlos: paso D6 (con sesión, abrir `/exportar` en la barra de direcciones muestra «Esta acción no está permitida»)

**Checkpoint**: US1 funciona y se puede entregar: quickstart §A.

---

## Phase 4: User Story 1b - Elegir qué presupuestos exportar (Priority: P1)

**Goal**: la opción «Seleccionar qué exportar» con casillas, «Marcar todos» y exportación parcial.

**Independent Test**: [quickstart.md §B](./quickstart.md#b-seleccionar-qué-exportar-us1b-sc-309): marcar 2 de 3 exportables y comprobar `presupuestospro-seleccion-…zip` con 2 PDF y un JSON parcial.

### Tests for User Story 1b

- [X] T014 [P] [US1b] En `tests/test_exportar_zip.py` añadir tests de `modo=seleccion` (escenario de 3 exportables + 1 borrador + 1 con cliente anonimizado): (a) con 2 ids válidos → 200 y nombre `presupuestospro-seleccion-AAAA-MM-DD.zip`; el zip tiene 2 PDF y un `presupuestospro-seleccion-AAAA-MM-DD.json` con `alcance: "seleccion"` y solo esos 2 presupuestos, sus clientes y sus logos; `servicios == []`, `contadores == []`, `perfil`/`ajustes` `None`; (b) sin `ids` → 422 `{"error": "Marca al menos un presupuesto."}`; (c) un id de un borrador, o del presupuesto con cliente anonimizado, o inexistente → **409** `{"error": "La lista ha cambiado. Cierra la ventana y vuelve a abrirla."}` **sin** zip (FR-313a); (d) un presupuesto descargado **después** de renderizar la lista y no marcado no aparece en el zip; (e) `modo=todo` con `ids` presentes los ignora y devuelve la copia completa

### Implementation for User Story 1b

- [X] T015 [US1b] En `presupuestos/rutas/exportar.py::exportar` (POST) implementar `modo == "seleccion"`: convertir `ids` a enteros (valor no numérico → 422 «Marca al menos un presupuesto.»); `ids` vacío → 422 «Marca al menos un presupuesto.»; dentro de la misma transacción de lectura comparar con `presupuestos_exportables(conn)`: si algún id no está en ella → 409 «La lista ha cambiado. Cierra la ventana y vuelve a abrirla.» (sin generar nada); si todo es válido, generar un PDF por id (en el orden por número) y `datos_exportacion(conn, ids)`. Nombres: zip `presupuestospro-seleccion-{fechas.hoy()}.zip` y JSON `presupuestospro-seleccion-{fechas.hoy()}.json`
- [ ] T016 [US1b] Ampliar `presupuestos/templates/fragmentos/_exportar_ventana.html` (contracts/rutas-http.md, «Ventana»): segundo radio `name="modo" value="seleccion" id="modo-seleccion"` con label «Seleccionar qué exportar», **desactivado** (con `<p class="suave">Aún no hay presupuestos descargados</p>`) si `resumen.exportables == 0`; un `<fieldset id="seleccion" hidden>` con `<legend>` «Presupuestos que se exportarán», un `<label><input type="checkbox" id="marcar-todos"> Marcar todos</label>`, `<p id="recuento-marcados" aria-live="polite">0 marcados</p>`, y una `<ul class="lista">` con, para cada exportable, `<li><label><input type="checkbox" name="ids" value="{{ p.id }}"> <strong>{{ p.numero }}</strong> {{ etiqueta_estado(p.estado) }} · {{ p.cliente_nombre }}</label></li>` (importar `etiqueta_estado` de `fragmentos/_estado.html`); y el aviso de copia parcial (FR-306b) en `<p id="aviso-parcial" class="aviso" hidden>` con el texto «Esta copia solo incluye los presupuestos marcados; no sirve como copia de seguridad completa.»; y `<p id="ayuda-marcar" class="suave" hidden>Marca al menos un presupuesto.</p>`
- [ ] T017 [US1b] En `presupuestos/static/app.js` ampliar la ventana: al cambiar el radio `modo` mostrar/ocultar `#seleccion`, `#aviso-parcial` y `#ayuda-marcar` (con `hidden`); «Marcar todos» (`#marcar-todos`) marca o desmarca todas las casillas `name="ids"`; al cambiar cualquier casilla actualizar `#recuento-marcados` («N marcados»), el estado de `#marcar-todos` (marcado solo si todas lo están) y desactivar «Descargar .zip» cuando `modo == seleccion` y no hay ninguna marcada (mostrando `#ayuda-marcar`); al volver a «Todo» la selección se **ignora** (no se envían `ids`: desactivar las casillas con `disabled` mientras `modo == todo`, o excluirlas del `FormData`); al cerrar la ventana restablecer «Todo», sin casillas marcadas y sin mensajes
- [ ] T018 [P] [US1b] En `presupuestos/static/estilos.css` estilos de `#seleccion` (lista con scroll interno, filas de 44 px mínimo, `.aviso` con tokens) coherentes con la 003; sin colores ni tamaños sueltos

**Checkpoint**: US1 y US1b funcionan por separado: quickstart §A y §B.

---

## Phase 5: User Story 2 - Que exportar no cambie nada y diga qué incluye (Priority: P1)

**Goal**: garantizar solo lectura y mostrar de antemano qué llevará el zip.

**Independent Test**: [quickstart.md §C](./quickstart.md#c-el-archivo-de-datos-y-la-solo-lectura-us2-sc-302-sc-304): con 2 presupuestos descargados y 1 borrador, exportar y comprobar que todo sigue igual.

### Tests for User Story 2

- [ ] T019 [P] [US2] En `tests/test_exportar_zip.py` añadir tests de solo lectura (FR-305, SC-304): con un borrador, exportar `todo` y comprobar en la base de datos que `emisor_congelado IS NULL` y que su estado (`estado.estado(...)`) sigue siendo `borrador`; que `SELECT * FROM presupuestos` y `contadores` son idénticos antes y después (comparar filas completas); que el siguiente `POST /presupuestos` recibe el número consecutivo esperado; y que `conn.total_changes` no aumenta durante la exportación (usar una conexión propia solo para medir si hace falta). Añadir un test de coherencia (FR-312): parchear `html_pdf` para que, al generar el PDF del primer presupuesto, otra conexión inserte un presupuesto nuevo y descargue un borrador; el zip debe contener solo lo que existía al empezar (el JSON no incluye el presupuesto nuevo y no contiene el PDF del borrador)

### Implementation for User Story 2

- [ ] T020 [US2] En `presupuestos/templates/fragmentos/_exportar_ventana.html` mostrar, bajo el radio «Todo», el texto de recuento (FR-310): `Se incluirán {{ resumen.exportables }} PDF y el archivo de datos.` y, si `resumen.solo_datos > 0`, `Los {{ resumen.solo_datos }} presupuestos sin PDF solo irán en el archivo de datos.` (con singular correcto si es 1: «El presupuesto sin PDF solo irá…»); si `resumen.exportables == 0` y `resumen.total > 0`: `No hay ningún presupuesto con PDF; la copia llevará solo el archivo de datos.`. Poner el contenedor con `id="recuento-todo"` y `aria-live="polite"`
- [ ] T021 [US2] En `presupuestos/static/app.js` actualizar el texto del botón «Descargar .zip» (FR-310a): `Descargar .zip (N archivos)` con `N = PDF + 1` y «(1 archivo)» en singular; con «Todo» `N = resumen.exportables + 1` (leer `resumen.exportables` de un `data-exportables` en `#form-exportar`, añadirlo en la T009), con «Seleccionar» `N = marcados + 1`; recalcular al cambiar de opción, al marcar/desmarcar y con «Marcar todos»
- [ ] T022 [US2] Comprobar y, si hace falta, corregir que ninguna ruta de la exportación escribe: `grep` en `presupuestos/rutas/exportar.py` no debe encontrar `INSERT`, `UPDATE`, `DELETE` ni `transaccion_exclusiva`; la transacción debe ser `BEGIN` + `ROLLBACK`

**Checkpoint**: la ventana informa y la exportación es de solo lectura: quickstart §C.

---

## Phase 6: User Story 3 - Saber que está trabajando cuando son muchos (Priority: P2)

**Goal**: estado «Preparando la copia…», sin segunda exportación y errores claros.

**Independent Test**: [quickstart.md §E](./quickstart.md#e-muchos-presupuestos-y-espera-us3-sc-307): con 50 presupuestos, el botón muestra «Preparando la copia…» y está desactivado hasta empezar la descarga.

### Tests for User Story 3

- [ ] T023 [P] [US3] En `tests/test_exportar_zip.py` añadir: (a) si `generar_pdf` (parcheado) lanza una excepción, `POST /exportar` devuelve 500 con `{"error": "No se ha podido preparar la copia. Inténtalo de nuevo."}`, **no** devuelve ningún zip y la base de datos queda sin cambios (FR-313); (b) con 50 presupuestos descargados creados por SQL y el PDF parcheado, el zip contiene 50 PDF + 1 JSON con nombres sin repetir; (c) con 200, igual (volumen soportado, spec «Assumptions»)

### Implementation for User Story 3

- [ ] T024 [US3] En `presupuestos/static/app.js`, en el envío de `#form-exportar`: antes del `fetch`, desactivar «Descargar .zip», «Cancelar», los radios y las casillas, poner `aria-busy="true"` en el formulario y cambiar el texto del botón a «Preparando la copia…» (guardando el anterior); ignorar un segundo envío mientras haya uno en curso (variable de estado); al terminar bien, cerrar la ventana y **restaurar** botón y controles; al fallar (respuesta no `ok` o `fetch` rechazado), restaurar y mostrar el mensaje en `#exportar-error` (si no hay JSON, «No se ha podido preparar la copia. Inténtalo de nuevo.»), dejando la ventana abierta; Esc y clic fuera **no** cierran la ventana mientras se prepara (`cancel` con `preventDefault()`)
- [ ] T025 [US3] Medir y anotar en [research.md](./research.md) (E7, «Nota de rendimiento») el tiempo real de una exportación de 50 presupuestos con el PDF real (WeasyPrint instalado), siguiendo [quickstart.md §E1](./quickstart.md#e-muchos-presupuestos-y-espera-us3-sc-307); la spec no fija un tiempo máximo: si supera 120 s (umbral orientativo de esta tarea, no un requisito), avisar al usuario antes de seguir (decisión de producto, no de código)

**Checkpoint**: las tres historias funcionan: quickstart §E.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T026 [P] Actualizar `README.md`: en «Operations» sustituir «Full data export as JSON» por la exportación en .zip (ventana «Todo» / «Seleccionar», PDF + archivo de datos) y mantener las copias de seguridad por línea de comandos; actualizar la tabla de specs con la 004
- [ ] T027 [P] Actualizar `specs/README.md`: añadir la fila de la 004 (estado «Implementada» solo al terminar, con T-numeros pendientes) y el nuevo recuento de tareas; y en `specs/001-presupuestos-pro/contracts/archivo-exportacion.md` y `rutas-http.md` (línea de `GET /exportar`) añadir una nota «Sustituido por la spec 004» enlazando a los contratos de la 004
- [ ] T028 [P] Revisar `docs/administracion.md` y la propia app (`grep -ri "exportar" presupuestos/templates docs README.md`): cualquier referencia a la descarga del archivo de datos debe apuntar al botón «Exportar…» del historial
- [ ] T029 Ejecutar `.venv/bin/pytest` completo (todo en verde) y `.venv/bin/pytest tests/test_exportar_zip.py -v`
- [ ] T030 Recorrer [quickstart.md](./quickstart.md) completo (A–H, incluida la prueba con 3 personas de SC-308) en la app, con WeasyPrint real, a 320, 360, 800 y 1280 px, solo teclado y lector de pantalla (§F); anotar cualquier fallo y corregirlo antes de dar la entrega por terminada (constitución, «Verificación de cada entrega»). Marcar en `checklists/exportacion.md` los ítems que el revisor considere satisfechos (solo el revisor las marca)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias.
- **Foundational (Phase 2)**: depende de la T001; **bloquea** las demás fases. T002 y T004 son independientes entre sí ([P]); T003 va antes de la T007; T005 usa `db.cargar_presupuesto` y puede ir tras T003.
- **US1 (Phase 3)**: depende de la fase 2. Es el MVP.
- **US1b (Phase 4)**: depende de la T007 (misma ruta), T009 (misma plantilla) y T010 (mismo JS).
- **US2 (Phase 5)**: depende de US1 (plantilla y JS); sus tests (T019) pueden escribirse tras la T007.
- **US3 (Phase 6)**: depende de US1 (JS) y se solapa con T010/T017/T021 en `app.js`: hacerlas en orden.
- **Polish (Phase 7)**: al final.

### User Story Dependencies

- **US1**: independiente tras la fase 2.
- **US1b**: usa la ventana y la ruta de US1, pero se prueba por separado con tests de ruta.
- **US2**: los tests de solo lectura no necesitan la interfaz; los textos usan la plantilla de US1.
- **US3**: el estado de espera es JS sobre el envío de US1.

### Within Each User Story

- Tests antes de la implementación (deben fallar primero).
- Ruta (`exportar.py`) → contexto del historial → plantilla → JS → CSS.
- Los cambios en `app.js` y en `_exportar_ventana.html` de varias historias van **en serie** (mismos archivos): T009 → T016 → T020; T010 → T017 → T021 → T024.

### Parallel Opportunities

- Fase 2: T002 ‖ T004.
- Tests de cada historia (T006, T014, T019, T023) en paralelo con otras tareas que toquen archivos distintos (T006 y T011, T014 y T018).
- Polish: T026 ‖ T027 ‖ T028.

---

## Parallel Example: Phase 2 y User Story 1

```text
# Fase 2, a la vez (archivos distintos):
T002  presupuestos/dominio/nombre_archivo.py + tests/dominio/test_formato_fechas_nombre.py
T004  presupuestos/rutas/exportar.py (datos_exportacion) + tests/test_exportar_zip.py

# US1, a la vez tras T003–T005:
T006  tests/test_exportar_zip.py (tests de POST /exportar)
T011  presupuestos/static/estilos.css (estilos del dialog)
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Fase 1 y fase 2 (T001–T005).
2. Fase 3 (T006–T013) y **parar**: comprobar quickstart §A con la app real.
3. Con eso el autónomo ya puede llevarse todo en un .zip.

### Incremental Delivery

1. Fases 1–2 → base lista.
2. + US1 → exportar «Todo» (MVP).
3. + US1b → selección parcial.
4. + US2 → recuentos y garantías de solo lectura.
5. + US3 → espera y errores.
6. Polish → documentación y verificación final.

### Notes

- Esta spec no cambia el esquema; si alguna tarea parece necesitar una columna nueva, parar: es una señal de que se sale de la spec (constitución, principio III).
- Hacer un commit al terminar cada fase o historia.
- Las ideas fuera de alcance (filtros, PDF de borradores, importar) van a `specs/propuestas.md`, no se implementan.
