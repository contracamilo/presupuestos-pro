---

description: "Lista de tareas de PresupuestosPro v1.1 — Navegación, formularios y alta de usuarios"
---

# Tasks: PresupuestosPro v1.1 — Navegación, formularios y alta de usuarios

**Input**: documentos de diseño de `/specs/002-mejoras-ui-usuarios/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md) (R1–R11), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: se mantiene la política de la 001 (research.md D20): tests pytest **solo** para reglas de dominio, control de acceso, actualización de datos y exportación. Se incluye `tests/test_clientes.py` (T025) porque comprueba datos que se guardan y se exportan (tipo de documento y país validados en el servidor, país forzado a «España», anonimización): es la frontera entre las reglas de dominio y la exportación, no la presentación. Todo lo demás se verifica en la app con [quickstart.md](./quickstart.md) (constitución, principio IV).

**Organization**: tareas agrupadas por historia de usuario; cada historia se puede implementar, verificar y entregar por separado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede hacer en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: historia de usuario de la spec (US1–US6)

## Path Conventions

Proyecto Python único de la 001: `presupuestos/` (aplicación), `tests/`, `docs/`. Stack, convenciones y estructura: [specs/001-presupuestos-pro/plan.md](../001-presupuestos-pro/plan.md). **No se añade ninguna dependencia.** Restricciones que aplican a todas las tareas:

- Textos visibles en español de España.
- La CSP prohíbe JavaScript en línea: todo el JS va en `presupuestos/static/app.js` (sin dependencias, mismo estilo IIFE `"use strict"`).
- Errores de validación: respuesta 422 con el formulario o fragmento y el mensaje junto a su campo (regla común de la 001).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: comprobar el punto de partida antes de tocar nada.

- [X] T001 Ejecutar `pytest` desde la raíz del repositorio y confirmar que todos los tests de la 001 pasan antes de empezar (anotar el resultado; si alguno falla, parar y avisar)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: no hay prerrequisitos compartidos. Las historias tocan archivos mayoritariamente distintos; los puntos de contacto (`base.html`, `app.js`, `estilos.css`, `test_acceso.py`) se indican en cada tarea y en «Dependencies».

**Checkpoint**: se puede empezar por cualquier historia.

---

## Phase 3: User Story 1 - Navegar con un menú lateral siempre visible (Priority: P1) 🎯 MVP

**Goal**: menú lateral con grupos «Trabajo» y «Configuración», sección actual resaltada, fijo desde 1024 px y con botón de hamburguesa por debajo (FR-101 a FR-104; research R1; [contracts/interfaz.md](./contracts/interfaz.md#menú-lateral-fr-101-a-fr-104)).

**Independent Test**: quickstart A1–A8.

### Implementation for User Story 1

- [X] T002 [US1] Sustituir en `presupuestos/templates/base.html` el `<details class="menu">` de la cabecera por: (a) cabecera `<header class="barra">` con la marca «PresupuestosPro» y un `<button type="button" class="boton-menu" aria-controls="menu-lateral" aria-expanded="false" aria-label="Abrir menú">☰</button>`; (b) `<nav id="menu-lateral" class="menu-lateral" aria-label="Menú principal">` con un título de grupo «Trabajo» (Presupuestos `/`, Clientes `/clientes`, Catálogo `/catalogo`), un título «Configuración» (Perfil `/perfil`, Ajustes `/ajustes`, Usuarios `/cuentas` solo si `usuario.tipo == 'titular'`, Mi cuenta `/mi-cuenta`, Exportar `/exportar`) y al final el formulario `POST /salir` con el botón «Salir»; (c) un `<div class="menu-fondo" hidden></div>` para la superposición en móvil. Mantener el bloque `{% if usuario %}` (sin menú en `/entrar` ni en errores sin sesión), el `#aviso-conexion` y el `<main>`. El enlace de Usuarios apunta a `/cuentas` hasta que US3 (T019) renombre la ruta
- [X] T003 [US1] Marcar la sección actual en `presupuestos/templates/base.html` con `aria-current="page"` según `request.url.path`: Presupuestos si la ruta es `/` o empieza por `/presupuestos`; Clientes `/clientes`; Catálogo `/catalogo`; Perfil `/perfil`; Ajustes `/ajustes`; Usuarios `/cuentas` o `/usuarios`; Mi cuenta `/mi-cuenta`. Exportar nunca se resalta. Usar una macro Jinja2 `enlace(href, texto, prefijos)` en la propia plantilla para no repetir la comparación
- [X] T004 [P] [US1] Estilos del menú en `presupuestos/static/estilos.css`: eliminar las reglas `.menu`, `.menu summary`, `.menu nav` y el `@media (min-width: 900px)` del menú antiguo. Añadir: por debajo de 1024 px, `.menu-lateral` oculto (fuera de pantalla a la izquierda) y visible como panel superpuesto cuando `body` tiene la clase `menu-abierto`; `.menu-fondo` como capa oscurecida a pantalla completa; `body.menu-abierto { overflow: hidden; }` para que el fondo no se desplace. Desde `@media (min-width: 1024px)`: `.boton-menu` y `.menu-fondo` ocultos, `.menu-lateral` fijo a la izquierda con ancho fijo (~220 px) y `main` con margen izquierdo igual. Títulos de grupo en texto pequeño en mayúsculas; enlace `[aria-current="page"]` con fondo y borde izquierdo (no solo color). Sin desplazamiento horizontal desde 360 px (FR-031)
- [X] T005 [P] [US1] Comportamiento del menú en `presupuestos/static/app.js`: funciones `abrirMenu()` (añade `menu-abierto` a `body`, quita `hidden` a `.menu-fondo`, `aria-expanded="true"`, `aria-label="Cerrar menú"`, foco en el primer enlace del menú) y `cerrarMenu(devolverFoco)` (lo contrario; si `devolverFoco`, foco al botón). Eventos: clic en `.boton-menu` alterna; clic en `.menu-fondo` cierra; tecla `Escape` cierra con el menú abierto; clic en un enlace del menú cierra. No hace nada si no existe `.boton-menu` (pantallas sin sesión)
- [X] T006 [US1] Revisar con el navegador en 360 px, 800 px y 1280 px todas las plantillas de `presupuestos/templates/` (historial, presupuesto, clientes, cliente, catálogo, perfil, ajustes, mi cuenta, cuentas, exportar) y corregir en `presupuestos/static/estilos.css` cualquier desbordamiento horizontal causado por el nuevo ancho de `main` (en especial la tabla de líneas del presupuesto)

**Checkpoint**: quickstart A1–A8 en verde; el resto de la app funciona igual que en la 001.

---

## Phase 4: User Story 2 - Volver al historial desde un presupuesto (Priority: P1)

**Goal**: botón «← Volver al historial» que conserva la búsqueda y no sale con guardados pendientes (FR-105; research R2, R3).

**Independent Test**: quickstart C1–C8.

### Implementation for User Story 2

- [X] T007 [P] [US2] En `presupuestos/templates/fragmentos/_historial_lista.html`, cambiar el enlace de cada presupuesto a `/presupuestos/{{ p.id }}{% if q %}?volver={{ q|urlencode }}{% endif %}`. Comprobar en `presupuestos/rutas/presupuestos.py` que el historial (`GET /`, página y fragmento) pasa `q` a la plantilla en ambos casos
- [X] T008 [US2] En `presupuestos/rutas/presupuestos.py`, la ruta `GET /presupuestos/{id}` acepta el parámetro opcional `volver: str = ""` y lo pasa a la plantilla. En `presupuestos/templates/presupuesto.html`, añadir como primer elemento del contenido `<a class="boton-volver" href="/{% if volver %}?q={{ volver|urlencode }}{% endif %}">← Volver al historial</a>` (FR-105). Si al abrir un presupuesto recién creado con «Nuevo presupuesto» no hay `volver`, el enlace va a `/`
- [X] T009 [P] [US2] Estilo `.boton-volver` en `presupuestos/static/estilos.css`: aspecto de botón secundario, visible arriba a la izquierda, área táctil de al menos 44 px de alto
- [X] T010 [US2] Espera de guardados pendientes en `presupuestos/static/app.js` (research R3): contador de peticiones HTMX en curso (`htmx:beforeRequest` suma; `htmx:afterRequest` resta). En la pantalla de presupuesto (`.boton-volver` presente), al hacer clic en `.boton-volver` o en un enlace de `#menu-lateral`: si el contador es 0, navegar normalmente; si no, `preventDefault()`, esperar a que llegue a 0 y entonces navegar al `href`, salvo que alguna de esas peticiones haya fallado, en cuyo caso no navegar: `htmx:sendError` o `htmx:responseError` con estado 0 o ≥ 500 (el aviso `#aviso-conexion` ya lo muestra el código existente) **o cualquier otro estado ≥ 400, incluido 422** (el error ya aparece junto a su campo; el cambio no se ha guardado y no se sale del presupuesto). Si no hay peticiones pendientes, la navegación es inmediata aunque haya un error de validación anterior visible

**Checkpoint**: quickstart C1–C8 en verde.

---

## Phase 5: User Story 3 - Gestionar usuarios desde una sección propia y sin comandos (Priority: P1)

**Goal**: sección «Usuarios» clara (alta, baja, restablecer con repetición de contraseña) y creación del titular desde el navegador (FR-106 a FR-110; research R4–R6; [contracts/cambios-rutas-y-pantallas.md](./contracts/cambios-rutas-y-pantallas.md)).

**Independent Test**: quickstart B1–B11.

### Tests for User Story 3

- [X] T011 [US3] Actualizar `tests/test_acceso.py`: (a) añadir `"/crear-titular"` a `PUBLICAS`; (b) cambiar todas las rutas `/cuentas…` por `/usuarios…` y el import `cuentas` sigue siendo el módulo `presupuestos.rutas.cuentas`; (c) añadir `repetir` con el mismo valor en los POST de alta, restablecer y cambiar contraseña existentes; (d) nuevos tests: `test_crear_titular_sin_titular` (sin usuarios, `GET /entrar` → 303 a `/crear-titular`; `POST /crear-titular` válido → 303 a `/`, cookie de sesión y fila `tipo='titular'`), `test_crear_titular_con_titular_existente` (con titular, `GET` y `POST /crear-titular` → 303 a `/entrar` o `/entrar?aviso=titular-existe` y sigue habiendo un solo titular), `test_crear_titular_validacion` (contraseña de 9 caracteres → 422; `repetir` distinto → 422 con «Las contraseñas no coinciden.»; no se crea usuario), `test_crear_titular_duplicado_por_carrera` (insertar un titular directamente en la BD entre el `GET` y el `POST` → el `POST` redirige a `/entrar?aviso=titular-existe` sin error 500), `test_repetir_distinto_en_alta_y_mi_cuenta` (422 en `POST /usuarios` y `POST /mi-cuenta/contrasena`), `test_rutas_cuentas_eliminadas` (`GET /cuentas` con sesión de titular → 404)

### Implementation for User Story 3

- [X] T012 [P] [US3] En `presupuestos/seguridad.py`, añadir `validar_nueva(contrasena: str, repetir: str) -> dict[str, str]` que devuelve errores por campo: `{"contrasena": "La contraseña debe tener al menos 10 caracteres."}` si `len < 10` (reutilizar `validar_longitud`) y `{"repetir": "Las contraseñas no coinciden."}` si difieren; diccionario vacío si es válida
- [X] T013 [US3] En `presupuestos/rutas/sesion.py`, añadir las rutas públicas (sin `usuario_actual`) de research R4: `GET /crear-titular` → si existe un usuario `tipo='titular'`, 303 a `/entrar`; si no, página `crear_titular.html`. `POST /crear-titular` con `nombre`, `email`, `contrasena`, `repetir` → si ya existe titular, 303 a `/entrar?aviso=titular-existe`; validar nombre y email obligatorios (email en minúsculas, `strip()`) y `seguridad.validar_nueva`; con errores → 422 con el formulario y los errores por campo; si no, `INSERT INTO usuarios (nombre, email, hash_contrasena, tipo, activo, creado_en) VALUES (?, ?, ?, 'titular', 1, ?)` capturando `sqlite3.IntegrityError` (índice `un_solo_titular`) → 303 a `/entrar?aviso=titular-existe`; tras insertar, `seguridad.crear_sesion` y la misma cookie que `POST /entrar` (reutilizar el bloque `set_cookie` extrayéndolo a una función local `_respuesta_con_sesion(token)`) → 303 a `/`
- [X] T014 [US3] En `presupuestos/rutas/sesion.py`, `GET /entrar`: si no existe ningún titular, 303 a `/crear-titular`; si llega `aviso=titular-existe`, pasar a la plantilla el texto «La cuenta del titular ya existe. Inicia sesión.» y mostrarlo en `presupuestos/templates/entrar.html` con `role="status"`
- [X] T015 [P] [US3] Crear `presupuestos/templates/crear_titular.html` (extiende `base.html`, sin sesión → sin menú): título «Crear la cuenta del titular», texto «Esta cuenta tendrá acceso a todos los datos y podrá dar de alta a otros usuarios.», campos Nombre, Email, Contraseña (ayuda «Mínimo 10 caracteres»), Repetir contraseña y botón «Crear cuenta». Cada error debajo de su campo con un `id` y el input enlazado con `aria-describedby`; conservar nombre y email tras un error, nunca las contraseñas. Comprobar que la página (incluidos `base.html` y el `<title>`) no muestra ningún dato del perfil del autónomo: ni nombre, ni logo, ni datos fiscales (FR-110); la ruta no debe pasar `perfil` al contexto
- [X] T016 [US3] En `presupuestos/rutas/cuentas.py`, `POST /mi-cuenta/contrasena`: leer `repetir`, validar con `seguridad.validar_nueva(nueva, repetir)` y devolver 422 con los errores por campo; actualizar `presupuestos/templates/mi_cuenta.html` con el campo «Repetir contraseña nueva» y los errores bajo cada campo (`aria-describedby`)
- [X] T017 [US3] En `presupuestos/rutas/cuentas.py`, renombrar las rutas `/cuentas`, `/cuentas/{id_}/baja` y `/cuentas/{id_}/contrasena` a `/usuarios…` (mismos métodos y lógica; redirecciones internas a `/usuarios`); `_pagina_cuentas` pasa a `_pagina_usuarios` y renderiza `usuarios.html`. `POST /usuarios` y `POST /usuarios/{id_}/contrasena` leen `repetir` y validan con `seguridad.validar_nueva`; email repetido → error en el campo `email` «Ya existe una cuenta con ese email.». En errores del alta, pasar `abrir_alta=True` a la plantilla
- [X] T018 [US3] Renombrar `presupuestos/templates/cuentas.html` a `presupuestos/templates/usuarios.html` y rehacerla según [contracts/interfaz.md](./contracts/interfaz.md#usuarios-fr-106-fr-107): título «Usuarios»; lista con Nombre, Email, Tipo (Titular/Asistente), Estado (Activa/Dada de baja); para asistentes activos, «Restablecer contraseña» (formulario con Contraseña nueva y Repetir contraseña) y «Dar de baja» (con el `hx-confirm` actual, apuntando a `/usuarios/{id}/baja`); al final `<details class="alta-usuario"{% if abrir_alta %} open{% endif %}><summary class="boton">Añadir usuario</summary>` con el formulario Nombre, Email, Contraseña, Repetir contraseña y «Dar de alta». Errores bajo cada campo con `aria-describedby`
- [X] T019 [US3] En `presupuestos/templates/base.html`, cambiar el enlace «Usuarios» del menú de `/cuentas` a `/usuarios` (el resaltado de T003 ya contempla ambos prefijos; quitar `/cuentas`)
- [X] T020 [US3] En `presupuestos/__main__.py`, eliminar la orden `crear-titular` (función `crear_titular`, su subcomando y su línea en el docstring); mantener `restablecer-titular` y `copia` sin cambios. Si `_pedir_contrasena` solo la usaba `crear_titular`, dejarla si la usa `restablecer-titular`
- [X] T021 [P] [US3] Actualizar `docs/administracion.md`: sustituir el paso con `docker compose exec app python -m presupuestos crear-titular …` por «Abre `https://tu-dominio` nada más arrancar el servidor y crea la cuenta del titular en la pantalla "Crear la cuenta del titular"», con la advertencia: «Hasta que crees esa cuenta, cualquiera que conozca la dirección podría crearla. Hazlo inmediatamente después de arrancar. Si al abrir la dirección ves la pantalla de inicio de sesión en lugar de la de creación sin haberla creado tú, reinstala con los datos vacíos.» Cambiar «Cuentas» por «Usuarios» en el texto sobre restablecer contraseñas de asistentes

**Checkpoint**: `pytest tests/test_acceso.py` en verde; quickstart B1–B11 en verde.

---

## Phase 6: User Story 4 - Elegir opciones cerradas con selectores (Priority: P2)

**Goal**: tipo de documento y país del cliente con selectores dependientes de categoría y territorio; actualización automática de instalaciones v1 (FR-111 a FR-114, SC-106; research R7, R8, R11; [data-model.md](./data-model.md)).

**Independent Test**: quickstart D1–D5 y E1–E5.

### Tests for User Story 4

- [X] T022 [P] [US4] Crear `tests/dominio/test_documento.py` con la tabla de [data-model.md](./data-model.md#tipos-de-documento-permitidos--dominiodocumentopy-r7): `tipos_permitidos("particular", "peninsula") == ["nif", "nie"]` (ídem `canarias`); `("empresa", "peninsula") == ["nif", "cif", "nie"]` (ídem `canarias`); `("empresa", "ue") == ["nif_iva_ue", "extranjero"]`; `("empresa", "fuera_ue") == ["extranjero"]`; `preseleccion("empresa", "ue") == "nif_iva_ue"`, `preseleccion("empresa", "fuera_ue") == "extranjero"`, `preseleccion` en España `== ""`; `es_valido(categoria, territorio, "")` siempre `True`; `es_valido("particular", "peninsula", "cif")` `False`; `ETIQUETAS` con «NIF», «CIF», «NIE», «NIF-IVA UE», «Otro documento extranjero», «Sin indicar»
- [X] T023 [P] [US4] Crear `tests/dominio/test_paises.py`: `PAISES[0] == "España"`; `PAISES_UE` tiene 27 países e incluye «España», «Alemania», «Francia» y no «Reino Unido» ni «Suiza»; `opciones("peninsula") == ["España"]` (ídem `canarias`); `opciones("ue")` no contiene «España», todos sus elementos están en `PAISES_UE` y está en orden alfabético español; `opciones("fuera_ue")` no contiene ningún país de `PAISES_UE`; `es_valido("ue", "Alemania", guardado="")` `True`; `es_valido("ue", "Alemania (Berlín)", guardado="Alemania (Berlín)")` `True` (valor de v1); `es_valido("ue", "Japón", guardado="")` `False`
- [X] T024 [P] [US4] Crear `tests/test_actualizacion.py`: crear una BD con el `schema.sql` de v1 (copiar en el test el `CREATE TABLE clientes` **sin** `tipo_documento` más las tablas necesarias, o ejecutar `schema.sql` y luego reconstruir `clientes` sin la columna) con `PRAGMA user_version = 1`, insertar un cliente y un presupuesto con líneas; llamar a `db.inicializar(ruta)`; comprobar `user_version == 2`, que el cliente tiene `tipo_documento == ''` y que el resto de columnas y el presupuesto con sus líneas no han cambiado; llamar otra vez a `db.inicializar(ruta)` y comprobar que no falla (idempotente). Comprobar también que una BD nueva queda en `user_version == 2` con la columna
- [X] T025 [US4] Ampliar `tests/test_exportar_copia.py`: `datos["version"] == 2` y cada cliente exportado tiene la clave `tipo_documento`. Crear `tests/test_clientes.py` (usa el fixture `titular` de `tests/conftest.py`): `POST /clientes` con `categoria=particular`, `territorio=peninsula`, `tipo_documento=cif` → 422 «Tipo de documento no válido para este cliente.»; con `territorio=ue`, `pais=Japón` → 422 «Elige un país de la lista.»; alta válida guarda `tipo_documento` y `pais`; con territorio `peninsula` se guarda `pais = "España"` aunque se envíe otro; anonimizar deja `tipo_documento = ''`

### Implementation for User Story 4

- [X] T026 [P] [US4] Crear `presupuestos/dominio/documento.py` (módulo puro, sin web ni BD): `TIPOS = ("nif", "cif", "nie", "nif_iva_ue", "extranjero")`; `ETIQUETAS = {"": "Sin indicar", "nif": "NIF", "cif": "CIF", "nie": "NIE", "nif_iva_ue": "NIF-IVA UE", "extranjero": "Otro documento extranjero"}`; `tipos_permitidos(categoria, territorio) -> list[str]`, `preseleccion(categoria, territorio) -> str` y `es_valido(categoria, territorio, tipo) -> bool` según la tabla de data-model.md («`''` = "Sin indicar"», siempre válido)
- [X] T027 [P] [US4] Crear `presupuestos/dominio/paises.py` (módulo puro): `PAISES` (lista de países en español con «España» primero y el resto en orden alfabético español), `PAISES_UE` (los 27 Estados miembros vigentes, nombres idénticos a los de `PAISES`), `opciones(territorio) -> list[str]` (`peninsula`/`canarias` → `["España"]`; `ue` → `PAISES_UE` sin España, alfabético; `fuera_ue` → `PAISES` sin los de `PAISES_UE`, alfabético) y `es_valido(territorio, pais, guardado) -> bool` (en la lista de `opciones(territorio)` o igual a `guardado` no vacío). Orden alfabético con una clave que ignore tildes (`unicodedata`), sin dependencias
- [X] T028 [US4] En `presupuestos/schema.sql`, añadir a `clientes` la columna `tipo_documento TEXT NOT NULL DEFAULT '' CHECK (tipo_documento IN ('', 'nif', 'cif', 'nie', 'nif_iva_ue', 'extranjero'))` y cambiar el final a `PRAGMA user_version = 2;`
- [X] T029 [US4] En `presupuestos/db.py`, `inicializar()` (research R11): si `user_version == 0`, aplicar `schema.sql` (queda en 2); si `user_version == 1`, en una transacción ejecutar `ALTER TABLE clientes ADD COLUMN tipo_documento TEXT NOT NULL DEFAULT '' CHECK (tipo_documento IN ('', 'nif', 'cif', 'nie', 'nif_iva_ue', 'extranjero'))` y `PRAGMA user_version = 2`; si es 2, nada. Comentario en español explicando por qué no hay herramienta de migraciones (principio I)
- [X] T030 [US4] En `presupuestos/rutas/clientes.py`: añadir `tipo_documento` a `CAMPOS` y a los `INSERT`/`UPDATE`; en alta y edición, validar con `documento.es_valido(categoria, territorio, tipo_documento)` → error «Tipo de documento no válido para este cliente.» en el campo; país: si `territorio in ("peninsula", "canarias")` guardar siempre `"España"`, si no validar con `paises.es_valido(territorio, pais, guardado)` (en alta `guardado = ""`; en edición, el `pais` actual del cliente) → error «Elige un país de la lista.»; en `anonimizar`, añadir `tipo_documento = ''` al `UPDATE`. Pasar a las plantillas `tipos_documento` (etiquetas), `opciones_pais` y la tabla de tipos permitidos por categoría/territorio para que el formulario y `app.js` la usen. Incluir `tipo_documento` en la ficha y en los SELECT que alimentan el formulario
- [X] T031 [US4] En `presupuestos/templates/fragmentos/_cliente_form.html`, según [contracts/interfaz.md](./contracts/interfaz.md#formulario-de-cliente-fr-111-a-fr-114): orden Nombre · Categoría · Territorio · [NIF-IVA verificado] · Tipo de documento · Número de documento · País · Dirección · Email. «Tipo de documento» es un `<select name="tipo_documento">` con primera opción «Sin indicar» (`value=""`) y una opción por cada tipo de `ETIQUETAS`, marcando con `data-permitido-en` (lista `categoria:territorio`) dónde es válida cada una y seleccionando el valor guardado. La etiqueta del campo `nif` pasa a «Número de documento». «País» es un `<select name="pais">` con todas las opciones de `PAISES` marcadas con `data-ue="1"` si están en `PAISES_UE`; si el cliente tiene un país guardado que no está en `PAISES`, añadir una primera opción `value="<texto>"` con texto «Revisar país: <texto>» seleccionada. Aplicar los mismos cambios de etiqueta en `presupuestos/templates/fragmentos/_ficha_cliente.html` (mostrar la etiqueta del tipo y el número)
- [X] T032 [US4] En `presupuestos/static/app.js`, ampliar `ajustarCliente(form)`: (a) tipo de documento — ocultar y desactivar las opciones cuyo `data-permitido-en` no incluya `categoria:territorio` actual; si la opción seleccionada queda desactivada o está vacía, seleccionar la preselección (`nif_iva_ue` en `ue`, `extranjero` en `fuera_ue`, «Sin indicar» en España); el campo «Número de documento» no se toca; (b) país — en `peninsula`/`canarias` seleccionar «España» y desactivar el selector añadiendo un `<input type="hidden" name="pais" value="España">` (un `select` desactivado no se envía); en `ue` mostrar solo opciones con `data-ue="1"` salvo España; en `fuera_ue` solo las que no tienen `data-ue`; si el valor seleccionado deja de estar permitido, vaciar la selección; la opción «Revisar país: …» se mantiene visible mientras esté seleccionada. Se ejecuta al cargar, tras `htmx:afterSettle` y al cambiar categoría o territorio (código existente)
- [X] T033 [US4] En `presupuestos/rutas/exportar.py`, añadir `tipo_documento` al `SELECT` de clientes y cambiar `"version": 1` por `"version": 2`

**Checkpoint**: `pytest` en verde; quickstart D1–D5 y E1–E5 en verde.

---

## Phase 7: User Story 5 - Elegir fechas con un calendario (Priority: P2)

**Goal**: fechas de emisión y validez con el calendario nativo, validez con mínimo = emisión (FR-115; research R9).

**Independent Test**: quickstart D6–D8.

### Tests for User Story 5

- [X] T034 [P] [US5] Ampliar `tests/dominio/test_formato_fechas_nombre.py`: `leer_fecha("2026-11-20") == "2026-11-20"`; `leer_fecha("20/11/2026") == "2026-11-20"`; `leer_fecha("2026-02-30")`, `leer_fecha("30/02/2026")` y `leer_fecha("mañana")` lanzan el mismo error que hoy lanza `leer_dmy` con texto inválido

### Implementation for User Story 5

- [X] T035 [P] [US5] En `presupuestos/dominio/fechas.py`, añadir `leer_fecha(texto: str) -> str` que acepta `AAAA-MM-DD` (calendario) o `DD/MM/AAAA` (respaldo) y devuelve `AAAA-MM-DD`, reutilizando `leer_dmy` y `de_iso` y lanzando el mismo tipo de error con el mismo mensaje en español ante una fecha inválida
- [X] T036 [US5] En `presupuestos/rutas/presupuestos.py`, en `PUT /presupuestos/{id}`, sustituir `fechas.leer_dmy(form["fecha_emision"])` y `fechas.leer_dmy(form["fecha_validez"])` por `fechas.leer_fecha(...)`; el resto (validez ≥ emisión, recálculo si `validez_editada_a_mano = 0`) no cambia
- [X] T037 [US5] En `presupuestos/templates/fragmentos/_fechas.html`, cambiar ambos inputs a `type="date"` con `value="{{ p.fecha_emision }}"` / `value="{{ p.fecha_validez }}"` (formato `AAAA-MM-DD`, sin el filtro `fecha`), quitar `placeholder` e `inputmode`, y añadir `min="{{ p.fecha_emision }}"` a `fecha_validez`. Mantener `hx-put`, `hx-trigger="change"`, `hx-target` y `hx-swap`. Comprobar que la respuesta de `PUT` incluye el fragmento `#fechas` con `hx-swap-oob` para que el `min` y la validez recalculada se actualicen; si no lo incluye en el cambio de emisión, añadirlo en `presupuestos/rutas/presupuestos.py`

**Checkpoint**: `pytest tests/dominio` en verde; quickstart D6–D8 en verde.

---

## Phase 8: User Story 6 - Subir mi logo de forma clara para que salga en el PDF (Priority: P3)

**Goal**: apartado de logo claro en Perfil con subir, cambiar y quitar (FR-116; research R10).

**Independent Test**: quickstart D9–D12.

### Implementation for User Story 6

- [X] T038 [US6] En `presupuestos/rutas/perfil.py`, añadir `POST /perfil/logo/quitar`: `UPDATE perfil SET logo_id = NULL WHERE id = 1` (no borrar la fila de `logos`: D12, los presupuestos congelados pueden apuntarla) y volver a `/perfil` con el mensaje «Logo quitado.» usando `redirigir()` (la acción llega por HTMX con `hx-confirm`). La ruta exige sesión como el resto (`test_toda_ruta_exige_sesion` la cubre automáticamente). Mostrar el mensaje en `/perfil` con un parámetro `?logo=quitado` o el mecanismo que ya use `logo_guardado`
- [X] T039 [US6] En `presupuestos/templates/perfil.html`, rehacer la sección del logo según [contracts/interfaz.md](./contracts/interfaz.md#perfil--logo-fr-116): título «Logo (aparece en tus PDF)», texto «PNG, JPG o SVG, hasta 2 MB». Sin logo: formulario actual con botón «Subir logo». Con logo: vista previa, el mismo formulario con botón «Cambiar logo» y un botón «Quitar logo» con `hx-post="/perfil/logo/quitar"` y `hx-confirm="¿Quitar el logo? Los presupuestos ya descargados lo conservan."`. Mantener los mensajes `error_logo` y `logo_guardado` y añadir «Logo quitado.» con `role="status"`

**Checkpoint**: quickstart D9–D12 en verde.

---

## Phase 9: Polish & Cross-Cutting Concerns

- [X] T040 Buscar y eliminar referencias obsoletas: `grep -rn "cuentas\|crear-titular" presupuestos docs tests` (salvo el nombre del módulo `rutas/cuentas.py`, que se mantiene) y `grep -rn "NIF/NIE o NIF-IVA" presupuestos/templates`; corregir lo que quede
- [X] T041 Ejecutar `pytest` completo y confirmar que todo pasa (tests de la 001 y nuevos)
- [ ] T042 Recorrer [quickstart.md](./quickstart.md) completo (A–E), incluida la regresión E6 con la guía de la 001, en un navegador en español a 360 px, 800 px y 1280 px; anotar cualquier fallo y corregirlo antes de dar la entrega por terminada (constitución, «Verificación de cada entrega»)
- [X] T043 Revisar la entrega contra los principios I–V de `.specify/memory/constitution.md`: ninguna dependencia nueva en `pyproject.toml`, ningún JS en línea en las plantillas, ninguna funcionalidad fuera de la spec (sin logo de cliente, sin pestañas, sin redirección de `/cuentas`), textos en español de España

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias.
- **Foundational (Phase 2)**: vacía.
- **Historias (Phases 3–8)**: dependen solo de T001; se pueden hacer en cualquier orden o en paralelo, con estos puntos de contacto:
  - `base.html`: T002–T003 (US1) antes de T019 (US3). Si US3 se hace antes que US1, T019 se aplica al menú antiguo (cambiar `/cuentas` por `/usuarios` en el `<details>`).
  - `app.js`: T005 (US1), T010 (US2) y T032 (US4) añaden bloques independientes al mismo archivo; hacerlos en serie.
  - `estilos.css`: T004 y T006 (US1) y T009 (US2); en serie.
  - T010 (US2) usa `#menu-lateral` para interceptar enlaces del menú; si US1 no está hecha, solo intercepta `.boton-volver`.
- **Polish (Phase 9)**: después de todas las historias que se entreguen.

### Within Each User Story

- Tests de dominio y de acceso primero (deben fallar), luego módulos de dominio, luego rutas, luego plantillas y JS.
- US4: T028 → T029 (esquema antes del paso de actualización); T026–T027 antes de T030–T032.
- US3: T012 antes de T013, T016 y T017; T017 antes de T018 y T019.
- US5: T035 antes de T036.

### Parallel Opportunities

- US1: T004 (CSS) y T005 (JS) en paralelo tras T002.
- US2: T007 y T009 en paralelo.
- US3: T012, T015 y T021 en paralelo.
- US4: T022, T023, T024, T026 y T027 en paralelo (archivos distintos).
- US5: T034 y T035 en paralelo.
- Historias distintas en paralelo respetando los puntos de contacto anteriores.

---

## Parallel Example: User Story 4

```bash
# Tests y módulos de dominio a la vez (archivos distintos):
Task: "T022 tests/dominio/test_documento.py"
Task: "T023 tests/dominio/test_paises.py"
Task: "T024 tests/test_actualizacion.py"
Task: "T026 presupuestos/dominio/documento.py"
Task: "T027 presupuestos/dominio/paises.py"
```

## Parallel Example: User Story 3

```bash
Task: "T012 validar_nueva en presupuestos/seguridad.py"
Task: "T015 presupuestos/templates/crear_titular.html"
Task: "T021 docs/administracion.md"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. T001 (punto de partida).
2. Phase 3 (US1): menú lateral y hamburguesa.
3. **Parar y verificar**: quickstart A1–A8 y una pasada rápida de la 001.
4. Entregable: la navegación nueva, sin cambios en datos.

### Incremental Delivery

1. US1 → menú (navegación).
2. US2 → volver al historial (completa el problema de navegación).
3. US3 → usuarios y titular sin comandos (desbloquea instalaciones nuevas sin perfil técnico).
4. US4 → selectores (única historia que cambia la base de datos; incluye la actualización automática v1 → v2).
5. US5 → calendario.
6. US6 → logo del perfil.
7. Phase 9 → verificación completa.

Cada historia se verifica con su bloque de quickstart antes de pasar a la siguiente.

---

## Notes

- [P] = archivos distintos, sin dependencias pendientes.
- Cada tarea cita el requisito o la decisión que la justifica; nada fuera de la spec (principio III).
- Hacer commit tras cada tarea o grupo lógico.
- La única tarea que modifica datos existentes es T029 (añade una columna con valor por defecto); probarla con T024 antes de desplegar en una instalación real.
