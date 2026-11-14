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

No queda ningún «NEEDS CLARIFICATION».
