# Research: PresupuestosPro v1.1 — Navegación, formularios y alta de usuarios

**Fecha**: 2026-11-14 | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

El stack, las convenciones y la estructura son los de [specs/001-presupuestos-pro/plan.md](../001-presupuestos-pro/plan.md) y [research.md (D1–D20)](../001-presupuestos-pro/research.md). Aquí solo se documentan las decisiones nuevas de esta iteración (R1–R11). Ninguna añade dependencias.

## Hallazgos sobre el código actual (punto de partida)

- La **unidad** del servicio y de la línea ya es un selector (`_catalogo_lista.html`, `_lineas.html`), igual que **tipo de IVA**, **tipo de retención**, **categoría** y **territorio**. De FR-111 solo quedan por convertir **tipo de documento** (nuevo) y **país**.
- `db.inicializar()` aplica `schema.sql` solo si `PRAGMA user_version = 0`; las instalaciones existentes están en `user_version = 1`.
- Ya existe el índice `un_solo_titular` (único parcial sobre `usuarios.tipo = 'titular'`): garantiza a nivel de base de datos que nunca haya dos titulares (FR-109).
- La CSP prohíbe JavaScript en línea: todo comportamiento nuevo va en `static/app.js`.
- El buscador del historial usa `hx-get="/"` sin cambiar la URL, así que la búsqueda no queda en la dirección de la página.
- El Perfil permite subir logo pero no quitarlo.

---

## R1. Menú lateral y botón de hamburguesa — FR-101 a FR-104

- **Decisión**: el menú se dibuja en `base.html` como `<nav>` lateral con dos grupos con título (Trabajo, Configuración) y «Salir». Por encima de 1024 px se muestra fijo con CSS; por debajo se oculta y un `<button aria-expanded aria-controls>` en la cabecera lo abre y cierra. El comportamiento (abrir, cerrar al elegir sección, al pulsar fuera, con Escape, bloquear el desplazamiento del fondo) va en `app.js`. La sección actual se marca con `aria-current="page"` comparando el prefijo de `request.url.path` en la plantilla (`/presupuestos/*` y `/` → Presupuestos).
- **Motivo**: es lo más simple que cumple accesibilidad con teclado y lector de pantalla (FR-104). Sin JS el menú en escritorio funciona igual; en móvil el botón necesita JS, que la app ya exige (HTMX).
- **Alternativas descartadas**: `<details>` actual (no cierra al pulsar fuera ni con Escape, no da `aria-expanded` fiable, no admite menú lateral fijo en escritorio con el mismo marcado); truco CSS con casilla oculta (peor para lectores de pantalla); librería de componentes (dependencia nueva, principio I).

## R2. «Volver al historial» conservando la búsqueda — FR-105

- **Decisión**: los enlaces de la lista del historial añaden la búsqueda activa: `/presupuestos/{id}?volver=<q>` (solo si hay búsqueda). La pantalla de presupuesto pinta el botón «← Volver al historial» con `href="/?q=<volver>"` o `href="/"`. `GET /` ya acepta `?q=` y lo pinta en el buscador.
- **Motivo**: un parámetro en la URL; sin estado en el servidor, sin almacenamiento en el navegador. Funciona también con enlace directo (sin parámetro → historial sin filtros).
- **Alternativas descartadas**: `history.back()` (falla con enlace directo y si se recargó la página); guardar la búsqueda en `sessionStorage` (estado oculto, más JS); `hx-push-url` en el buscador (cambia también el comportamiento del botón «atrás» del navegador, más difícil de verificar).

## R3. No salir con un guardado pendiente — caso límite «Volver con cambios aún guardándose»

- **Decisión**: `app.js` cuenta las peticiones HTMX en curso (`htmx:beforeRequest` / `htmx:afterRequest`). Al pulsar «Volver al historial» (o cualquier enlace del menú) desde el presupuesto con peticiones en curso, se espera a que terminen; si alguna falla, se muestra el aviso existente «No se ha podido guardar…» y no se navega.
- **Motivo**: el guardado automático se dispara en `change`; al pulsar el enlace, el campo pierde el foco y la petición sale justo antes de navegar. Sin esta espera, se podría perder el último cambio sin aviso.
- **Alternativas descartadas**: `beforeunload` (diálogo genérico del navegador, en inglés en algunos, no distingue éxito de error).

## R4. Creación del titular desde el navegador — FR-108 a FR-110

- **Decisión**: nuevas rutas públicas `GET/POST /crear-titular` en `rutas/sesion.py`.
  - Si no existe titular: `GET /entrar` redirige (303) a `/crear-titular`; como toda página sin sesión acaba en `/entrar`, la primera visita a cualquier dirección lleva allí.
  - Si ya existe: `GET` y `POST /crear-titular` → 303 a `/entrar`.
  - `POST` valida nombre, email, contraseña (≥ 10) y repetición; inserta el titular. Si el índice `un_solo_titular` rechaza la inserción (dos envíos a la vez), responde 303 a `/entrar?aviso=titular-existe`, que muestra «La cuenta del titular ya existe. Inicia sesión.».
  - Tras crearla, abre sesión (misma cookie que `/entrar`) y redirige a `/`.
  - La comprobación de origen (D9) y las cabeceras de seguridad se aplican igual; la ruta no muestra datos del autónomo.
- **Se elimina** la orden `crear-titular` de `__main__.py` (la spec la sustituye, FR-108). `restablecer-titular` y `copia` se mantienen.
- **Motivo**: reutiliza `seguridad.hash_contrasena`, `crear_sesion` y la restricción que ya existe; no hace falta bloqueo propio.
- **Alternativas descartadas**: código de instalación (descartado en la sesión de aclaraciones); conservar también la orden de consola (dos caminos para lo mismo, principio I y III).

## R5. Repetir contraseña y errores junto al campo — FR-107

- **Decisión**: los cuatro formularios con contraseña nueva (`/crear-titular`, alta de usuario, restablecer contraseña de asistente, cambiar la propia) añaden el campo `repetir`. La validación vive en una función de `seguridad.py` (`validar_nueva(contrasena, repetir) -> dict[campo, mensaje]`) que devuelve los errores por campo; la plantilla los pinta debajo de cada campo con `aria-describedby`. Respuesta 422 con el formulario, como el resto de la app.
- **Mensajes**: «La contraseña debe tener al menos 10 caracteres.», «Las contraseñas no coinciden.», «Ya existe una cuenta con ese email.».

## R6. Sección «Usuarios» — FR-106

- **Decisión**: se renombran las rutas `/cuentas*` a `/usuarios*` (mismos métodos y comportamiento) y la plantilla `cuentas.html` a `usuarios.html`. «Añadir usuario» es un `<details>` cuyo `<summary>` es el botón y su contenido el formulario de alta (sin JS). Si el alta falla, la respuesta 422 lo devuelve abierto con los errores.
- **Motivo**: la URL coincide con el nombre que ve el usuario; la app no tiene enlaces externos que romper.
- **Alternativas descartadas**: mantener `/cuentas` y cambiar solo el texto (incoherente al verificar); redirección de `/cuentas` a `/usuarios` (código para un caso que no existe).

## R7. Tipo de documento del cliente — FR-112, FR-114

- **Decisión**:
  - Nueva columna `clientes.tipo_documento` con valores `nif`, `cif`, `nie`, `nif_iva_ue`, `extranjero` o `''` (sin indicar). Ver [data-model.md](./data-model.md).
  - La regla «qué tipos se permiten según categoría y territorio» y «cuál se preselecciona» va en un módulo puro nuevo `dominio/documento.py`, probado con pytest. El servidor la aplica al guardar (422 si el tipo no está permitido) y `app.js` la replica para filtrar el selector al cambiar categoría o territorio, igual que ya hace con territorio y «NIF-IVA verificado».
  - El tipo **no es obligatorio**: se puede guardar «Sin indicar», igual que el número de documento puede ir vacío (spec 001). Las reglas de descarga del PDF (FR-023) no cambian.
  - Al anonimizar (FR-043) también se vacía `tipo_documento`.
- **Motivo**: un solo sitio con la regla, coherente con `dominio/tratamiento.py`; la pantalla y el servidor no pueden discrepar porque el servidor tiene la última palabra.
- **Alternativas descartadas**: deducir el tipo del formato del número (la spec 001 descarta validar formatos); hacerlo obligatorio (rompería clientes existentes y la spec no lo pide).

## R8. Selector de país — FR-113, FR-114

- **Decisión**: lista fija de países en español en un módulo puro nuevo `dominio/paises.py` (`PAISES`, `PAISES_UE`), con «España» primero. Opciones según territorio:
  - `peninsula` / `canarias` → solo «España» (selector desactivado, valor fijo).
  - `ue` → países de la UE salvo España, en orden alfabético.
  - `fuera_ue` → países fuera de la UE, en orden alfabético.
  - `clientes.pais` sigue siendo texto: no cambia el modelo. El servidor acepta un país de la lista permitida **o** el valor que ya tenía guardado (clientes de v1). Si el valor guardado no está en la lista, el selector muestra una opción «Revisar país: <texto>» seleccionada hasta que se elija otro.
- **Motivo**: sin dependencias ni datos externos (FR-028); un cambio de la UE se resuelve editando una lista.
- **Alternativas descartadas**: librería de países (dependencia nueva para ~200 nombres); códigos ISO en la base de datos (cambio de modelo y del PDF sin que la spec lo pida).

## R9. Fechas con calendario — FR-115

- **Decisión**: `<input type="date">` nativo en `_fechas.html`, con `value` en `AAAA-MM-DD` (el formato interno, D4) y `min` = fecha de emisión en el campo de validez. El servidor lee la fecha con una función nueva `fechas.leer_fecha()` que acepta `AAAA-MM-DD` (calendario) y `DD/MM/AAAA` (navegadores sin calendario, que muestran un campo de texto). La regla «validez ≥ emisión» y el recálculo de FR-011 se mantienen en el servidor; al recalcular, el fragmento de fechas devuelto actualiza también el `min`.
- **Motivo**: el calendario del propio navegador es el que pide la spec (supuesto «puede ser el propio del navegador») y en móvil abre el selector del sistema sin teclado (US5 AS4). Cero dependencias.
- **Riesgo conocido**: el formato que muestra el calendario nativo lo decide el idioma del navegador o del sistema; con un navegador en español es DD/MM/AAAA. Se indica en la guía de verificación. El PDF y el resto de pantallas siguen usando el formateador propio (DD/MM/AAAA siempre).
- **Alternativas descartadas**: librería de calendario JS (dependencia nueva, más código que verificar, principio I).

## R10. Quitar el logo del perfil — FR-116

- **Decisión**: nueva acción `POST /perfil/logo/quitar` (con `hx-confirm`) que pone `perfil.logo_id = NULL`. La fila de `logos` no se borra (D12: los logos son inmutables y los presupuestos congelados pueden apuntarla).
- **Motivo**: cumple US6 AS4 sin tocar el modelo y respeta la congelación de FR-018.

## R11. Actualizar instalaciones existentes — SC-106

- **Decisión**: `db.inicializar()` pasa a tener dos pasos:
  - Base de datos nueva (`user_version = 0`): aplica `schema.sql`, que ya incluye `tipo_documento` y termina en `PRAGMA user_version = 2`.
  - Base de datos de v1 (`user_version = 1`): ejecuta en una transacción `ALTER TABLE clientes ADD COLUMN tipo_documento TEXT NOT NULL DEFAULT '' CHECK (tipo_documento IN ('', 'nif', 'cif', 'nie', 'nif_iva_ue', 'extranjero'))` y `PRAGMA user_version = 2`.
  - Se ejecuta solo al arrancar la app; no hay pasos manuales para el administrador.
- **Motivo**: es una columna con valor por defecto; no justifica una herramienta de migraciones (la 001 la descarta, principio I). Los datos existentes no se tocan (SC-106).
- **Alternativas descartadas**: reconstruir la tabla (innecesario para añadir una columna); herramienta de migraciones (dependencia nueva).

---

# Ampliación 2026-11-17: modo oscuro (US7, FR-117 a FR-130)

**Fecha**: 2026-11-17. Decisiones R12–R18. Ninguna añade dependencias ni cambia el esquema de la base de datos.

## Hallazgos sobre el código actual (punto de partida de la ampliación)

- Todos los colores están en `static/tokens.css` (`:root`, `color-scheme: light`); `estilos.css` y `pdf.html` solo usan `var(--…)`, y `tests/test_paleta.py` lo comprueba junto con 26 pares de contraste (FR-202, FR-212 de la 003).
- `base.html` declara `<meta name="color-scheme" content="light">`.
- El PDF incluye `tokens.css` leído por `pdf.estilos_comunes()`; no incluye ningún otro archivo CSS.
- La CSP es `script-src 'self'; style-src 'self'`: no se puede poner un `<script>` en el `<head>` que fije el tema antes de pintar, ni estilos en línea.
- Las páginas completas se pintan con `base.html` desde `pagina()` o directamente con `TemplateResponse`; en ambos casos la plantilla recibe `request` (y sus cookies).
- La cookie de sesión se crea en `rutas/sesion.py` con `secure` según `COOKIE_SEGURA`.
- La vista previa del logo (`.logo-previa`, Perfil) no tiene fondo: un logo negro transparente desaparecería sobre fondo oscuro.

## R12. Dónde se recuerda el tema — FR-121, FR-122, FR-124

- **Decisión**: cookie `tema` en el navegador con valor `claro`, `oscuro` o `sistema`; `Path=/`, `SameSite=Lax`, `HttpOnly`, `Secure` según `COOKIE_SEGURA` (como la de sesión), duración 400 días (máximo que admiten los navegadores). La pone el servidor en `POST /tema` (R15). Sin cookie o con un valor desconocido → `sistema`. Las páginas sin sesión ignoran la cookie y usan siempre `sistema` (FR-124).
- **Motivo**: la sesión de aclaraciones fijó «por dispositivo». Una cookie llega al servidor en cada petición, así que el servidor puede pintar la página ya con el tema correcto (R14, sin destello). No toca la base de datos ni `user_version`.
- **Alternativas descartadas**: `localStorage` (el servidor no lo ve: obligaría a fijar el tema con JS antes de pintar, imposible sin script en línea por la CSP, y habría destello); columna en `usuarios` (sería «por usuario», descartado en la aclaración, y exigiría `user_version` 3); cookie escrita desde `app.js` con `document.cookie` (no funciona sin JS, FR-120).

## R13. Paleta oscura en un archivo aparte — FR-125, FR-128, FR-130

- **Decisión**: nuevo `static/tokens-oscuro.css` con un único bloque `:root { color-scheme: dark; … }` que redefine **todas** las variables de color de `tokens.css` (mismos nombres, valores oscuros; ver [contracts/tema.md](./contracts/tema.md#paleta-oscura)). No contiene tamaños, tipografía ni separaciones. `tokens.css` sigue siendo la paleta clara y el lugar de todo lo demás. Se añade un token nuevo `--color-fondo-logo: #ffffff` solo en `tokens.css` (no se redefine en oscuro) para la vista previa del logo (R17).
- **Motivo**:
  - Una sola definición de la paleta oscura, sin duplicar el bloque para «Oscuro» y para «Como el sistema» (R14 decide cuándo se aplica).
  - El PDF solo lee `tokens.css` (`pdf.estilos_comunes()`), así que **nunca** puede salir en oscuro (FR-130) sin escribir código para impedirlo.
  - `estilos.css` no cambia de reglas: sigue usando las mismas variables.
- **Alternativas descartadas**:
  - Función CSS `light-dark()` en cada token: una sola línea por color, pero el generador de PDF puede no entenderla (se quedaría sin colores) y `test_paleta.py` dejaría de poder leer los valores. Riesgo sin beneficio.
  - Bloques `:root[data-tema="oscuro"]` y `@media (prefers-color-scheme: dark) { :root[data-tema="sistema"] }` dentro de `tokens.css`: duplica la paleta oscura y la mete en el CSS que también lee el PDF.

## R14. Aplicar el tema sin destello y siguiendo al sistema — FR-118, FR-123, FR-126

- **Decisión**: `base.html` pinta siempre, después de `tokens.css` y antes de `estilos.css`, `<link id="tokens-oscuro" rel="stylesheet" href="/static/tokens-oscuro.css" media="…">` y `<meta name="color-scheme" content="…">`, con valores según el tema que calcula el servidor (función `tema_actual(request)` en `rutas/__init__.py`, disponible en las plantillas):

  | Tema | `media` del enlace | `color-scheme` (meta) |
  |---|---|---|
  | `claro` | `not all` (no se aplica) | `light` |
  | `oscuro` | `all` | `dark` |
  | `sistema` | `(prefers-color-scheme: dark)` | `light dark` |

- **Motivo**:
  - El HTML ya llega con el tema correcto: no hay destello (FR-126) y no hace falta JS para pintar.
  - Con `sistema`, es el propio navegador quien aplica o retira la hoja cuando el dispositivo cambia de modo, también con la app abierta (FR-123), sin código.
  - `color-scheme` hace que calendarios, desplegables, casillas y barras de desplazamiento del navegador se pinten en oscuro (FR-125).
  - `estilos.css` se carga después, así que sus reglas usan ya los valores oscuros.
- **Alternativas descartadas**: atributo `data-tema` en `<html>` con selectores en CSS (necesita la duplicación descartada en R13); cambiar el tema solo con JS tras cargar (destello y no funciona sin JS).

## R15. Selector «Tema» y cambio inmediato — FR-117 a FR-120

- **Decisión**:
  - En `base.html`, al final del grupo «Configuración» del menú lateral y antes de «Salir»: `<form class="form-tema" method="post" action="/tema">` con un `<fieldset>` cuyo `<legend>` es «Tema» y tres botones de opción (`name="tema"`: Claro, Oscuro, Como el sistema), el actual marcado, un campo oculto `volver` con la ruta actual y un botón «Aplicar».
  - **Sin JS**: se elige y se pulsa «Aplicar» → `POST /tema` pone la cookie y responde 303 a `volver` (FR-120). Se pierde lo no guardado, como en cualquier recarga (aceptado en la spec).
  - **Con JS** (`app.js`): oculta «Aplicar»; al cambiar la opción, cambia en el momento el `media` del enlace `#tokens-oscuro` y el contenido del `meta` según la tabla de R14 (FR-118, sin recargar y sin tocar el resto de la página) y envía el formulario con `fetch` (`POST /tema` con la cabecera `X-Tema-Fetch: 1`, respuesta 204) para guardar la cookie. Si el envío falla, muestra el aviso existente «No se ha podido guardar. Comprueba tu conexión.»; el tema se queda aplicado en la página.
  - `POST /tema` exige sesión (como el resto de la app), pasa por la comprobación de origen (D9), rechaza valores desconocidos (422) y solo acepta en `volver` rutas internas (empiezan por `/` y no por `//`; si no, `/`).
- **Motivo**:
  - Botones de opción dentro de `<fieldset>`/`<legend>`: el lector de pantalla anuncia «Tema», las tres opciones y la marcada, y se manejan con Tab y flechas sin código (FR-119).
  - El cambio con `fetch` no es una petición HTMX: no cuenta como guardado pendiente (R3) y no interfiere con el guardado automático (caso límite).
- **Alternativas descartadas**: interruptor de dos estados (no permite volver a «Como el sistema», Supuestos de la spec); `<select>` (dos interacciones en vez de una, SC-108); llevarlo a «Mi cuenta» (más escondido; la spec lo pone en el menú).

## R16. Contrastes de la paleta oscura — FR-127, SC-110

- **Decisión**: la paleta oscura (valores en [contracts/tema.md](./contracts/tema.md#paleta-oscura)) se elige para cumplir **los mismos 26 pares** de `contracts/sistema-visual.md` de la 003. Comprobados al diseñarla: todos superan 5:1 (el más justo, `--color-borde-control` sobre `--color-fondo`, 5,02:1 con mínimo 3:1). Se comprueba además `--color-borde-control` sobre `--color-fondo-2` (4,50:1, mínimo 3:1), porque en oscuro el menú lateral usa ese fondo. Criterios:
  - Fondos casi negros azulados (`#14191f`, `#1c232b`), texto casi blanco (`#e6e9ee`), no blanco puro, para que deslumbre menos.
  - Marca azul aclarada (`#7fb2e5`): el azul claro `#1f4e79` no llega a 4,5:1 sobre fondo oscuro (supuesto de la spec). En los botones de marca y de error el texto pasa a ser oscuro (`--color-sobre-marca: #0d1620`).
  - Verde, ámbar, rojo y azul conservan su significado (FR-127). Las etiquetas de estado siguen distinguiéndose por icono y forma (FR-210 de la 003), sin cambios en `estilos.css`.
- `tests/test_paleta.py` lee las dos hojas y comprueba los pares en ambos temas, que `tokens-oscuro.css` redefine todos los colores de `tokens.css` salvo `--color-fondo-logo` (para que no quede ninguna zona con colores del claro, SC-109) y que no contiene tamaños ni otros tokens.

## R17. Vista previa del logo legible — FR-129

- **Decisión**: `.logo-previa` gana `background: var(--color-fondo-logo)`, un poco de relleno y el radio pequeño. `--color-fondo-logo` vale blanco en los dos temas (R13), así que el logo siempre se ve como en el PDF.
- **Motivo**: un logo negro con fondo transparente desaparece sobre fondo oscuro. Mostrarlo sobre blanco es además fiel a cómo saldrá en el PDF.
- **Alternativas descartadas**: invertir o filtrar el logo en oscuro (cambiaría los colores de la marca del autónomo).

## R18. Qué no cambia

- El PDF (`pdf.html`, `pdf.py`): no se toca (FR-130).
- La base de datos, `schema.sql`, `user_version` (sigue en 2), las copias de seguridad y la exportación .zip de la 004: el tema no se guarda en el servidor.
- Las reglas de `estilos.css`, salvo la vista previa del logo (R17), los estilos del selector «Tema» en el menú y ocultar «Aplicar» con JS.
- Los textos de las pantallas, salvo los del selector («Tema», «Claro», «Oscuro», «Como el sistema», «Aplicar»).

---

No queda ningún «NEEDS CLARIFICATION».
