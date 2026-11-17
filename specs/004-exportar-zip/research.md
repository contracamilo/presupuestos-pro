# Research: PresupuestosPro v1.3 — Exportar en un .zip

**Fecha**: 2026-11-17 | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

Stack y convenciones: [001](../001-presupuestos-pro/plan.md), [002](../002-mejoras-ui-usuarios/plan.md), [003](../003-rediseno-visual/plan.md). Aquí solo las decisiones nuevas (E1–E11). Ninguna añade dependencias.

## Hallazgos sobre el código actual

- **Exportación actual** (`rutas/exportar.py`): `GET /exportar` devuelve un JSON con `datos_exportacion(conn)`; el menú lateral enlaza a ella (`base.html`). Tests: `tests/test_exportar_copia.py` y `tests/test_acceso.py`.
- **PDF** (`rutas/presupuestos.py::descargar_pdf`): comprueba `requisitos_descarga`, **fija el emisor** en la primera descarga (`emisor_congelado`), construye el contexto (emisor efectivo, logo como `data:`, cálculo) y llama a `generar_pdf`. Todo está inline en la ruta.
- **«Descargado»** no es un campo propio: es `emisor_congelado IS NOT NULL`. La etiqueta «Caducado» tiene prioridad sobre «Enviado», así que **no sirve** para saber si un presupuesto se descargó.
- **`requisitos_descarga`** rechaza, entre otros, un cliente anonimizado (`«El cliente … fue eliminado»`). Un presupuesto ya descargado puede, por tanto, dejar de poder generar su PDF.
- **Nombre de la descarga individual** (`dominio/nombre_archivo.py::nombre_pdf`, FR-022): `PRE-2026-001_Estudio-Garcia.pdf` (sin tildes, guiones). La spec 004 pide otro formato dentro del zip.
- **Conexión** (`db.conectar`): `isolation_level=None` (autocommit), WAL, `busy_timeout=5000`. Las transacciones se abren a mano.
- **CSP**: `default-src 'self'; script-src 'self'; style-src 'self'` (sin scripts ni estilos en línea). `fetch` al mismo origen y `<a download>` con `blob:` están permitidos.
- **Historial** (`GET /`): ya calcula el total y el estado de cada presupuesto; el fragmento `#lista-presupuestos` se sustituye al buscar (HTMX).

## E1. Ventana: `<dialog>` nativo — FR-301, FR-301a–c, SC-310

- **Decisión**: un `<dialog id="ventana-exportar">` renderizado en `historial.html` (fuera de `#lista-presupuestos`, para que la búsqueda no lo toque). `app.js` lo abre con `showModal()`. Cierra con «Cancelar» (`<form method="dialog">`), con Esc (nativo) y con un clic sobre el fondo.
- **Motivo**: `showModal()` ya atrapa el foco, bloquea el resto de la página, cierra con Esc y devuelve el foco al botón: accesibilidad que de otro modo habría que programar (FR-301c). Sin biblioteca.
- **Alternativas descartadas**: biblioteca de modales (dependencia); un `div` con `role="dialog"` (hay que programar foco y Esc); una página aparte `/exportar` (no es «ventana previa» y rompe el contexto de la lista).

## E2. Descarga con `fetch` + `Blob` — FR-311, FR-313

- **Decisión**: el formulario de la ventana lo intercepta `app.js`: desactiva «Descargar .zip», cambia su texto a «Preparando la copia…», hace `fetch(POST /exportar)`, y con la respuesta crea un `Blob`, un enlace `<a download>` temporal y lo pulsa; al terminar cierra la ventana y restaura el botón. Si la respuesta no es 200 muestra el mensaje JSON `{"error": …}` en un `role="alert"` dentro de la ventana, sin cerrarla.
- **Motivo**: un formulario normal no avisa de cuándo termina la preparación ni permite mostrar un error sin salir de la página. Con `fetch` ambas cosas son directas y la CSP no cambia.
- **Alternativas descartadas**: envío normal del formulario + cookie «descarga terminada» consultada por JS (más piezas y el error de servidor navega fuera de la página); descarga por `GET` con enlace (la selección no cabe de forma fiable en la URL con 200 presupuestos); `htmx` (no maneja descargas binarias).
- **Límite asumido**: el zip pasa por la memoria del navegador (Blob). Con cientos de presupuestos son decenas de MB; la spec documenta como volumen soportado y probado hasta 200 presupuestos y no impone tope técnico (clarificación CHK021); el quickstart E2 lo comprueba.

## E3. Ruta `POST /exportar` — FR-302, FR-305, FR-309

- **Decisión**: `POST /exportar` con campos de formulario `modo` (`todo` | `seleccion`) y `ids` (repetido). Es de **solo lectura**, pero se usa `POST` por el cuerpo; hereda la comprobación de origen de las escrituras (que no estorba). `GET /exportar` desaparece (responde 405 al existir la ruta para `POST`). Sin sesión → mismo comportamiento que el resto (redirige a iniciar sesión).
- **Respuestas**: 200 `application/zip` con `Content-Disposition: attachment; filename="…"`; errores `{"error": "…"}` en JSON con 409 (la lista cambió) o 422 (selección vacía, `modo` no válido). Sin presupuestos: 422 `No hay presupuestos que exportar.` (la interfaz ya lo evita, FR-309).
- **Alternativas descartadas**: mantener `GET /exportar` para el JSON (lo prohíbe FR-314); `GET /exportar.zip?ids=…` (URL larga, sin cuerpo).

## E4. Lectura coherente — FR-312

- **Decisión**: abrir una transacción de lectura (`BEGIN`, diferida) y leer **todo** dentro de ella: lista de presupuestos, `cargar_presupuesto` de cada uno, logos y el archivo de datos. En WAL todas las lecturas ven el mismo instante. Se cierra con `ROLLBACK` (no escribe nada) y **después** se generan los PDF a partir de los datos y HTML ya leídos.
- **Motivo**: generar un PDF puede tardar; no se mantiene una transacción abierta mientras tanto (en WAL no bloquearía a quien escribe, pero una instantánea larga retrasa la limpieza del WAL). El HTML de cada PDF se construye dentro de la transacción; la renderización con WeasyPrint, fuera.
- **Alternativas descartadas**: sin transacción (la copia podría mezclar instantes); bloqueo exclusivo (impediría trabajar mientras se exporta).

## E5. Zip con `zipfile` en memoria — FR-302, FR-303, FR-308

- **Decisión**: `zipfile.ZipFile(BytesIO, "w", ZIP_DEFLATED)`; una entrada por PDF y una para el archivo de datos; sin carpetas (los PDF y el archivo de datos en la raíz). Orden: archivo de datos primero y los PDF por número. Los nombres con tildes y «ñ» van en UTF-8 (`zipfile` activa la bandera sola).
- **Motivo**: sin ficheros temporales ni dependencias. El volumen (cientos de PDF de ~50–150 KB) cabe en memoria.
- **Alternativas descartadas**: fichero temporal en disco (limpieza y permisos); streaming del zip (complejidad sin necesidad con este volumen); `ZIP_STORED` para los PDF (ahorra CPU pero el JSON sí comprime; no merece distinguir).

## E6. Qué presupuestos «son exportables» — FR-303, FR-301b, FR-304

- **Decisión**: un presupuesto es **exportable (con PDF)** si `emisor_congelado IS NOT NULL` **y** `requisitos_descarga(perfil_efectivo, cliente, líneas)` devuelve lista vacía, es decir, si la descarga individual funcionaría hoy sin fijar nada nuevo. Esta es la lista de la ventana de selección y la base del recuento de PDF con «Todo». Los demás (borradores, o descargados con cliente anonimizado u otro requisito roto) solo van en el archivo de datos con «Todo».
- **Motivo**: la spec exige «el mismo PDF que genera la app» (FR-304); si la app no puede generarlo, la exportación tampoco. Evita PDF distintos, errores a mitad del zip y cualquier escritura (FR-305).
- **Hallazgo**: obligó a añadir a la spec el caso límite «cliente anonimizado después de descargar».
- **Alternativas descartadas**: generar igualmente saltándose los requisitos (PDF que la app no genera: contradice FR-304); fallar toda la exportación (un solo cliente borrado impediría exportar); fijar el emisor de los borradores (rompe FR-305).

## E7. Reutilizar la generación del PDF — FR-304

- **Decisión**: extraer de `descargar_pdf` una función `html_pdf(conn, datos) -> str` (contexto + plantilla `pdf.html`, incluida la lectura del logo) que usan la descarga individual y el zip; después, `generar_pdf(html)` igual que hoy. La descarga individual conserva su orden: comprobar requisitos → fijar emisor → `html_pdf` → `generar_pdf`.
- **Motivo**: garantizar por construcción que ambos PDF son el mismo documento, con importes idénticos al céntimo (SC-303).
- **Nota de rendimiento**: la ruta es síncrona (`def`), así que FastAPI la ejecuta en su grupo de hilos y no bloquea a los demás usuarios. 50 presupuestos son 50 renderizados secuenciales; se mide en el quickstart. Sin paralelismo ni caché (principio I).
- **Medición (T025, 2026-11-17)**: 50 presupuestos descargados de 6 líneas cada uno, WeasyPrint 70 real en macOS (`DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`), petición `POST /exportar` con `modo=todo` por `TestClient` (sin navegador): **23,7 s**, 50 PDF + 1 JSON, zip de 0,8 MB. Muy por debajo del umbral orientativo de 120 s; con la ventana en «Preparando la copia…» es aceptable. Medido sobre una base de datos sintética; el recorrido en el navegador (quickstart §E1) se hace en la T030.

## E8. Nombres de archivo — FR-307, FR-308

- **Decisión**: `nombre_pdf_zip(numero, cliente)` → `«{numero} - {cliente limpio}.pdf»`. `limpiar_nombre` sustituye por un espacio `/ \ : * ? " < > |` y caracteres de control, colapsa espacios, quita puntos y espacios en los extremos, conserva tildes y «ñ» y recorta el cliente a 80 caracteres; si queda vacío, «Sin cliente». Ejemplo: `PRE-2026-001 - Diseño Web S.L.pdf` para «Diseño/Web S.L.» (la `/` pasa a espacio).
- **Nombres del zip**: `presupuestospro-copia-AAAA-MM-DD.zip` (Todo) y `presupuestospro-seleccion-AAAA-MM-DD.zip` (Seleccionar), con `fechas.hoy()`. El archivo de datos lleva el mismo nombre base con `.json`.
- **Convive** con `nombre_pdf` (FR-022 de la 001, descarga individual), que no cambia.
- **Unicidad**: el número es único por presupuesto, así que no hay nombres repetidos aunque dos clientes se llamen igual.
- **Alternativas descartadas**: reutilizar `nombre_pdf` (quita tildes y usa guiones: contradice FR-307); normalizar a ASCII (pierde «ñ»).

## E9. Archivo de datos completo y de selección — FR-306, FR-306a

- **Decisión**: `datos_exportacion(conn, ids=None)`. Con `ids=None` produce lo de hoy más `"alcance": "completo"`. Con `ids`: `"alcance": "seleccion"`, `presupuestos` filtrados (con líneas), `clientes` solo los referenciados, `logos` solo los del emisor fijado de esos presupuestos, `servicios` y `contadores` vacíos y `perfil` y `ajustes` a `null`. Mismas claves, mismo `version: 2`, para que un futuro importador distinga por `alcance`.
- **Motivo**: FR-306a (sin catálogo, ajustes ni contadores) y un formato estable.
- **Alternativas descartadas**: quitar las claves en la selección (obliga al lector a comprobar su existencia); subir `version` (el cambio es solo aditivo).

## E10. Retirar la exportación suelta — FR-314

- **Decisión**: se elimina `GET /exportar`, el enlace «Exportar» del menú lateral y el test del JSON; se actualizan el contrato de la 001 (nota de sustitución en `contracts/`), `docs/administracion.md` si la menciona, `README.md` y `specs/README.md`. La orden de copia por línea de comandos (`python -m presupuestos copia`) **no se toca**: es otra cosa (copia de la base de datos, FR-041).
- **Sin redirección** de la URL antigua, como en la 002 con `/cuentas`.

## E11. Pruebas

- **Decisión**: pytest, sin WeasyPrint (como `test_pdf_contenido.py`): se sustituye `generar_pdf` por un doble que devuelve bytes con el HTML. Cubre: contenido y nombres del zip, selección (PDF y archivo de datos), borradores, cliente anonimizado, solo lectura (estado y `emisor_congelado` intactos), sin presupuestos, acceso sin sesión y de asistente, y los nombres conflictivos (`dominio`). La ventana, el estado «Preparando…» y la descarga real se comprueban a mano en el quickstart (principio IV).
