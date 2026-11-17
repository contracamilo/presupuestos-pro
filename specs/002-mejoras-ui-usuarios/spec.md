# Feature Specification: PresupuestosPro v1.1 — Navegación, formularios, alta de usuarios y modo oscuro

**Feature Branch**: `002-mejoras-ui-usuarios`

**Created**: 2026-11-14

**Updated**: 2026-11-17 (ampliación: modo oscuro conmutable — US7, FR-117 a FR-130, SC-108 a SC-112)

**Status**: Draft

**Input**: User description: "quiero iterar sobre un par de cosas en 001-presupuestos-pro debemos tener pestaña o tab de creacion de datos de usuario, los selectores por ejemplo de tipo de documento CIF, deben ser selectores, las fechas deben ser date pickers, si voy a historial deberia tenr un boton de volver o que ver historial se un tab, podriamos tener un menu lateral y un hambrurguer en mobile, tambien en la parte de cliente deberia poder añadir una imagen de logo, deberia poder crear usuarios de manera clara no haciendo comandos de docker"

**Input (ampliación 2026-11-17)**: "se debe trabajar sobre la spec existente 002-mejoras-ui-usuarios modificandola, no creando una nueva, agregando criterios y casos borde y demás documentados en modo-oscuro-dpec.md" — pre-especificación de un modo oscuro conmutable (Claro / Oscuro / Como el sistema).

## Contexto

- **Punto de partida**: esta spec es una iteración sobre `specs/001-presupuestos-pro/spec.md` (PresupuestosPro v1). Todo lo definido allí sigue vigente salvo lo que esta spec cambia de forma explícita.
- **Problemas detectados al usar v1**:
  - La navegación es un menú desplegable en la cabecera; no se ve en qué sección se está y, al entrar en un presupuesto desde el historial, no hay una forma clara de volver.
  - Algunos datos con opciones cerradas se escriben a mano (por ejemplo, el tipo de documento del cliente: NIF, CIF, NIE…), lo que provoca errores.
  - Las fechas se escriben a mano en formato DD/MM/AAAA, sin calendario.
  - Las cuentas de usuario no tienen un lugar evidente en la app, y la primera cuenta (titular) solo se puede crear ejecutando un comando en el servidor.
  - El autónomo no encuentra con claridad dónde subir su propio logo para que salga en el PDF (ya existe en Perfil desde v1, pero no se ve).
  - *(Ampliación 2026-11-17)* La app solo se ve en claro: con poca luz la pantalla blanca cansa la vista, y la app ignora que muchos dispositivos ya están en modo oscuro.
- **Usuarios afectados**: titular y asistentes (uso diario) y administrador técnico (instalación). Ver roles en la spec 001. Los clientes del autónomo no se ven afectados por el modo oscuro: el PDF no cambia.
- **Relación con la spec 003**: el modo oscuro es una segunda paleta del sistema visual de la spec 003 (colores definidos en un único lugar, contrastes WCAG 2.1 AA, etiquetas de estado). No cambia tipografía, tamaños, separaciones ni maquetación.

## Clarifications

### Session 2026-11-14

- Q: Mientras la instalación no tiene titular, ¿cómo se evita que otra persona lo cree antes desde el navegador? → A: No se protege con código: la pantalla «Crear la cuenta del titular» está abierta y la primera persona que la completa crea el titular. Se acepta el riesgo; la guía de instalación indica crear el titular nada más arrancar el servidor.
- Q: ¿De quién es el logo que se quería poder subir: de cada cliente o del propio autónomo? → A: Solo del autónomo (emisor), que es el que sale en el PDF. No se añade logo a los clientes; se pide que el logo del Perfil se vea y se suba con claridad.
- Q: ¿La «pestaña de creación de datos de usuario» es la sección «Usuarios» o una pantalla con pestañas para Perfil, Ajustes y Mi cuenta? → A: Cada opción es una entrada propia del menú lateral (incluida «Usuarios» para dar de alta cuentas); no hay pantalla con pestañas. El menú se ordena en dos grupos: «Trabajo» y «Configuración».

### Session 2026-11-17

- Q: ¿La preferencia de tema se recuerda por usuario o por dispositivo? → A: Por dispositivo: cada navegador recuerda su elección, compartida por quien use ese equipo. No se guarda en la cuenta ni cambia los datos almacenados (FR-121).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navegar con un menú lateral siempre visible (Priority: P1)

Como titular o asistente, quiero un menú lateral con cada sección como entrada propia, ordenadas en «Trabajo» (Presupuestos/Historial, Clientes, Catálogo) y «Configuración» (Perfil, Ajustes, Usuarios, Mi cuenta y el selector «Tema» de US7; «Exportar» lo retiró la spec 004), más «Salir», que me indique en qué sección estoy, y que en el móvil se abra con un botón de menú (hamburguesa), para moverme por la herramienta sin perderme.

**Why this priority**: afecta a todas las pantallas y resuelve el problema de «no sé cómo volver». Es la base sobre la que se apoyan las demás mejoras.

**Independent Test**: en un ordenador, comprobar que el menú lateral está visible en todas las pantallas con la sección actual resaltada; en un móvil de 360 px, comprobar que el menú está oculto, se abre con el botón de hamburguesa y se cierra al elegir una sección.

**Acceptance Scenarios**:

1. **Given** una sesión iniciada en una pantalla de al menos 1024 px de ancho, **When** abro cualquier sección, **Then** veo el menú lateral fijo a la izquierda con todas las secciones a las que tengo acceso, agrupadas en «Trabajo» y «Configuración», y la sección actual resaltada.
2. **Given** una sesión iniciada en un móvil de 360 px, **When** abro cualquier sección, **Then** el menú lateral está oculto y veo un botón de menú (icono de tres líneas) en la cabecera.
3. **Given** el móvil con el menú cerrado, **When** pulso el botón de menú, **Then** el menú se despliega por encima del contenido; **When** elijo una sección, pulso fuera del menú o pulso de nuevo el botón, **Then** el menú se cierra.
4. **Given** una sesión de asistente, **When** veo el menú, **Then** no aparece la sección «Usuarios».
5. **Given** la pantalla de inicio de sesión (sin sesión), **When** la abro, **Then** no se muestra el menú lateral.
6. **Given** cualquier sección del menú, **When** la uso con teclado, **Then** puedo abrir y cerrar el menú y llegar a cada sección solo con el teclado.

---

### User Story 2 - Volver al historial desde un presupuesto (Priority: P1)

Como titular o asistente, cuando abro un presupuesto desde el historial, quiero un botón «Volver al historial» bien visible, para regresar a la lista sin usar el botón «atrás» del navegador.

**Why this priority**: el historial es la pantalla de inicio y el punto de entrada a cada presupuesto; quedarse «atrapado» en un presupuesto es el problema de navegación más citado.

**Independent Test**: abrir un presupuesto desde el historial habiendo escrito una búsqueda, pulsar «Volver al historial» y comprobar que se vuelve a la lista con la misma búsqueda aplicada.

**Acceptance Scenarios**:

1. **Given** el historial, **When** abro un presupuesto, **Then** veo en la parte superior un botón «← Volver al historial».
2. **Given** un presupuesto abierto con cambios recién hechos, **When** pulso «Volver al historial», **Then** vuelvo a la lista y los cambios están guardados (el guardado automático de la spec 001 se mantiene).
3. **Given** el historial filtrado por «Acme», **When** abro un presupuesto y pulso «Volver al historial», **Then** la lista sigue filtrada por «Acme».
4. **Given** un presupuesto recién creado con «Nuevo presupuesto», **When** pulso «Volver al historial», **Then** vuelvo a la lista y el presupuesto nuevo aparece en ella.

---

### User Story 3 - Gestionar usuarios desde una sección propia y sin comandos (Priority: P1)

Como titular, quiero una sección «Usuarios» en el menú donde ver, dar de alta, dar de baja y restablecer la contraseña de los asistentes con un formulario claro; y como administrador técnico, quiero crear la cuenta del titular desde el navegador al instalar, sin tener que ejecutar comandos en el servidor.

**Why this priority**: hoy dar de alta la primera cuenta exige conocimientos técnicos (comando en el servidor), lo que bloquea que un autónomo sin perfil técnico ponga en marcha su instalación.

**Independent Test**: con una instalación recién hecha y sin cuentas, abrir la herramienta en el navegador, crear la cuenta del titular siguiendo la pantalla, entrar con ella, ir a «Usuarios» y dar de alta a un asistente; comprobar que el asistente puede entrar.

**Acceptance Scenarios**:

1. **Given** una instalación sin cuenta de titular, **When** abro la herramienta, **Then** veo la pantalla «Crear la cuenta del titular» en lugar de la de inicio de sesión, sin que se me pida ningún código.
2. **Given** la pantalla «Crear la cuenta del titular», **When** introduzco nombre, email y una contraseña de al menos 10 caracteres repetida dos veces, **Then** se crea el titular, entro directamente en la herramienta y la pantalla de creación deja de estar disponible para siempre.
3. **Given** ya existe un titular, **When** cualquiera intenta abrir la pantalla «Crear la cuenta del titular», **Then** ve la pantalla de inicio de sesión.
4. **Given** soy el titular, **When** abro «Usuarios», **Then** veo la lista de cuentas (nombre, email, tipo, activa o dada de baja) y un botón «Añadir usuario».
5. **Given** «Usuarios», **When** pulso «Añadir usuario» y relleno nombre, email y contraseña inicial (con repetición), **Then** el asistente aparece en la lista y puede entrar con esos datos.
6. **Given** el formulario de alta con email repetido, contraseña de menos de 10 caracteres o contraseñas que no coinciden, **When** lo envío, **Then** se indica el error junto al campo y no se crea la cuenta.
7. **Given** un asistente de la lista, **When** pulso «Dar de baja» y confirmo, **Then** se comporta como en la spec 001 (FR-035).
8. **Given** un asistente de la lista, **When** pulso «Restablecer contraseña» e introduzco una nueva, **Then** se comporta como en la spec 001 (FR-039).

---

### User Story 4 - Elegir opciones cerradas con selectores (Priority: P2)

Como titular o asistente, quiero que todos los datos que tienen opciones cerradas (tipo de documento del cliente, categoría, territorio, país, unidad, tipo de IVA, tipo de retención) se elijan en un selector desplegable, para no cometer errores de escritura.

**Why this priority**: reduce errores en datos que afectan a los impuestos y al PDF, pero la herramienta ya funciona sin ello.

**Independent Test**: dar de alta un cliente y un servicio y comprobar que ninguno de los campos con opciones cerradas permite escribir texto libre.

**Acceptance Scenarios**:

1. **Given** el formulario de cliente, **When** relleno el documento, **Then** primero elijo el tipo de documento en un selector (NIF, CIF, NIE, NIF-IVA UE, Otro documento extranjero) y después escribo el número.
2. **Given** categoría «Particular», **When** abro el selector de tipo de documento, **Then** solo se ofrecen NIF y NIE.
3. **Given** territorio «Otro país UE», **When** abro el selector de tipo de documento, **Then** se ofrece «NIF-IVA UE» preseleccionado; con territorio «Fuera de la UE», se ofrece «Otro documento extranjero» preseleccionado.
4. **Given** el formulario de cliente, **When** elijo el país, **Then** lo hago en un selector con la lista de países en español y con «España» primero; para territorio «Otro país UE» solo se ofrecen países de la UE distintos de España.
5. **Given** el formulario de servicio o una línea manual, **When** elijo la unidad, **Then** lo hago en un selector (hora, día, proyecto, unidad; en la línea manual, también la opción «—», que significa sin unidad, como en la v1).
6. **Given** un cliente creado en v1 sin tipo de documento, **When** abro su ficha, **Then** el selector muestra «Sin indicar», el documento escrito se conserva y puedo elegir el tipo y guardar.

---

### User Story 5 - Elegir fechas con un calendario (Priority: P2)

Como titular o asistente, quiero elegir la fecha de emisión y la de validez del presupuesto en un calendario, para no tener que escribirlas a mano.

**Why this priority**: mejora la comodidad y evita fechas mal escritas; las fechas ya se rellenan solas por defecto.

**Independent Test**: en ordenador y en móvil, abrir un presupuesto, cambiar la fecha de emisión con el calendario y comprobar que la validez se recalcula según la spec 001.

**Acceptance Scenarios**:

1. **Given** un presupuesto abierto, **When** pulso en la fecha de emisión o de validez, **Then** se abre un calendario donde elijo el día; la fecha se muestra en formato DD/MM/AAAA.
2. **Given** emisión 13/11/2026 y validez sin editar a mano con 30 días, **When** elijo 20/11/2026 en el calendario de emisión, **Then** la validez pasa a 20/12/2026 (FR-011 de la spec 001).
3. **Given** emisión 20/11/2026, **When** abro el calendario de validez, **Then** no puedo elegir días anteriores al 20/11/2026.
4. **Given** un móvil, **When** pulso en una fecha, **Then** se abre el calendario propio del móvil y no aparece el teclado de texto.

---

### User Story 6 - Subir mi logo de forma clara para que salga en el PDF (Priority: P3)

Como titular, quiero ver con claridad en mi Perfil dónde subir, cambiar o quitar mi logo y cuál tengo ahora, para asegurarme de que mis presupuestos en PDF salen con mi imagen corporativa.

**Why this priority**: la función ya existe en v1 (FR-001, FR-002, FR-021 de la spec 001); solo se mejora su visibilidad.

**Independent Test**: abrir Perfil, subir un logo, descargar un presupuesto y comprobar que el logo aparece en la cabecera del PDF; quitarlo y comprobar que el siguiente PDF de un presupuesto nunca descargado sale sin logo.

**Acceptance Scenarios**:

1. **Given** el Perfil sin logo, **When** lo abro, **Then** veo un apartado «Logo (aparece en tus PDF)» con un botón «Subir logo» y la indicación de formatos y tamaño (PNG, JPG o SVG, hasta 2 MB).
2. **Given** el Perfil con logo, **When** lo abro, **Then** veo la vista previa del logo actual y los botones «Cambiar logo» y «Quitar logo».
3. **Given** un logo subido, **When** descargo un presupuesto nunca descargado, **Then** el PDF muestra el logo en la cabecera (CA1 de la spec 001).
4. **Given** el Perfil con logo, **When** pulso «Quitar logo» y confirmo, **Then** desaparece la vista previa y los presupuestos nunca descargados salen sin logo; los ya descargados conservan el logo con el que salieron (FR-018 de la spec 001).

---

### User Story 7 - Elegir entre tema claro, oscuro o el del sistema (Priority: P2)

Como titular o asistente, quiero elegir desde el menú lateral si la app se ve en **Claro**, **Oscuro** o **Como el sistema**, que el cambio sea inmediato sin perder lo que estoy escribiendo y que la app lo recuerde, para trabajar cómodo con cualquier luz; y como autónomo, quiero que el PDF que envío a mis clientes salga siempre igual, en claro, use el tema que use.

**Why this priority**: mejora la comodidad y la accesibilidad de uso diario, pero la herramienta ya funciona sin ello; se apoya en el menú lateral (US1) y en el sistema visual de la spec 003.

**Independent Test**: con un presupuesto abierto a medio editar, elegir «Oscuro» en el menú, comprobar que toda la pantalla cambia al momento y que nada se pierde; recargar, cambiar de sección y volver a entrar otro día y comprobar que sigue en oscuro; descargar el PDF y comprobar que sale en claro.

**Acceptance Scenarios**:

1. **Given** la app en claro, **When** elijo «Oscuro» en el selector «Tema» del menú lateral, **Then** toda la pantalla pasa a oscuro al momento, sin recargar.
2. **Given** un presupuesto con una línea a medio escribir, **When** cambio de tema, **Then** la línea y lo escrito siguen ahí, los totales no cambian y el guardado automático continúa con normalidad.
3. **Given** elegí «Oscuro», **When** recargo, voy a Clientes, cierro el navegador y vuelvo a entrar, **Then** la app sigue en oscuro en todos los casos.
4. **Given** tema «Como el sistema» y el dispositivo en claro, **When** cambio el dispositivo a oscuro con la app abierta, **Then** la app pasa a oscuro sin tocar nada.
5. **Given** el dispositivo en oscuro, **When** elijo «Claro» en la app, **Then** la app se ve en claro y no vuelve a oscuro al recargar.
6. **Given** nunca he elegido tema, **When** entro en la app, **Then** el selector muestra «Como el sistema» y la app sigue la preferencia del dispositivo.
7. **Given** la app en oscuro, **When** descargo el PDF de un presupuesto, **Then** el PDF tiene fondo blanco y es igual al que se descarga con la app en claro.
8. **Given** la app en oscuro, **When** recorro todas las pantallas, el menú, un error de formulario, el aviso «No se ha podido guardar» y el historial con presupuestos Borrador, Enviado y Caducado, **Then** todo se lee bien, no queda ningún fondo blanco suelto (salvo la vista previa del logo, que va sobre blanco a propósito, FR-129) ni texto oscuro sobre fondo oscuro, y las etiquetas de estado se distinguen entre sí.
9. **Given** la app en oscuro, **When** abro el calendario de fecha de emisión y el selector de tipo de cliente, **Then** se muestran también en oscuro y legibles.
10. **Given** solo uso teclado y lector de pantalla, **When** llego al selector «Tema» y cambio de opción, **Then** el foco es visible en ambos temas y se anuncia el nombre «Tema», las opciones y la opción elegida.
11. **Given** tema «Oscuro» guardado, **When** recargo varias veces cualquier pantalla, **Then** en ningún momento aparece un destello del tema claro.
12. **Given** un logo negro con fondo transparente, **When** abro Perfil en oscuro, **Then** la vista previa del logo se distingue con claridad.

---

### Edge Cases

- **Pantalla pequeña con menú abierto**: el contenido de detrás no se desplaza mientras el menú está abierto, y no aparece desplazamiento horizontal a partir de 360 px (FR-031 de la spec 001).
- **Tableta (entre 768 y 1023 px)**: se usa el comportamiento de móvil (botón de menú), para no restar espacio a la tabla de líneas.
- **Abrir un presupuesto con un enlace directo** (sin pasar por el historial): «Volver al historial» lleva al historial sin filtros.
- **Volver con cambios aún guardándose**: si un cambio no ha llegado al servidor, se avisa como en la spec 001 («No se ha podido guardar») antes de salir y no se da por guardado. Si el servidor rechaza el cambio por un dato no válido (p. ej., una fecha incorrecta), no se sale del presupuesto y el error se muestra junto al campo.
- **Dos personas intentan crear el titular a la vez** en una instalación nueva: solo se crea una cuenta de titular; la segunda persona ve la pantalla de inicio de sesión con un aviso de que la cuenta ya existe.
- **Navegador sin calendario propio**: la fecha se puede seguir escribiendo en DD/MM/AAAA con la validación de la spec 001. En ese caso el campo puede mostrar la fecha guardada en formato AAAA-MM-DD; se acepta para no añadir código ni dependencias (principio I). El resto de pantallas y el PDF siguen mostrando DD/MM/AAAA.
- **Tipo de documento incoherente tras cambiar categoría o territorio** (p. ej., CIF y se cambia a «Particular»): el selector se vacía y pide elegir de nuevo; el número escrito se conserva.
- **Copia de seguridad y exportación**: incluyen el tipo de documento de cada cliente.
- **Restablecer la contraseña del titular** sigue siendo tarea del administrador técnico (FR-039 de la spec 001); esta spec solo elimina el comando para la creación inicial.

**Modo oscuro (US7)**

- **Sin JavaScript o si no carga**: el selector «Tema» sigue funcionando recargando la página, y el tema guardado se aplica igual (FR-120).
- **Navegador sin preferencia de sistema**: «Como el sistema» equivale a «Claro».
- **Pantallas sin sesión** (inicio de sesión y «Crear la cuenta del titular»): siguen la preferencia del sistema y no muestran el selector, igual que no muestran el menú (US1 AS5).
- **Logo oscuro o con fondo transparente**: su vista previa se muestra siempre sobre una superficie clara para que no desaparezca (FR-129). El PDF no cambia.
- **Titular y asistente en el mismo equipo y navegador**: comparten el tema elegido en ese equipo (FR-121).
- **Mismo usuario en dos dispositivos**: cada dispositivo recuerda su propia elección; cambiarla en uno no afecta al otro.
- **Navegador que borra sus datos o ventana privada**: se pierde la elección y vuelve a «Como el sistema» (FR-122).
- **Sin conexión al cambiar de tema**: con JavaScript, el tema elegido se aplica igualmente a la pantalla abierta, pero no se puede recordar; aparece el aviso existente «No se ha podido guardar. Comprueba tu conexión.» y, al recargar con conexión, vuelve el tema que estaba guardado.
- **Páginas de error que se muestran sin comprobar la sesión** (p. ej., una dirección que no existe): siguen la preferencia del sistema, igual que no muestran el menú (FR-124).
- **Cambiar de tema durante un guardado automático**: el guardado termina con normalidad; el tema no interfiere con los datos.
- **Cerrar sesión**: la pantalla de inicio de sesión sigue la preferencia del sistema (FR-124); al volver a entrar se aplica de nuevo la elección guardada en ese dispositivo.
- **Modo de alto contraste forzado por el sistema** (p. ej., Windows): la app no lo impide; no se diseña una paleta específica para él.
- **Imprimir una pantalla desde el navegador**: fuera de alcance; el documento imprimible es el PDF.

## Requirements *(mandatory)*

### Functional Requirements

**Navegación**

- **FR-101**: Con sesión iniciada, todas las pantallas DEBEN mostrar un menú lateral con cada sección como entrada propia, ordenadas en dos grupos con título: **Trabajo** (Presupuestos —el historial—, Clientes, Catálogo) y **Configuración** (Perfil, Ajustes, Usuarios —solo titular—, Mi cuenta, Tema), y al final «Salir». Sustituye al menú desplegable de la cabecera de v1. No hay pantallas con pestañas. *(La entrada «Exportar» que tenía «Configuración» la retiró la spec 004, que la sustituyó por el botón «Exportar…» de la lista de presupuestos; el selector «Tema» lo añade FR-117.)*
- **FR-102**: El menú DEBE resaltar la sección en la que está el usuario; al estar dentro de un presupuesto, se resalta «Presupuestos».
- **FR-103**: En pantallas de menos de 1024 px de ancho, el menú DEBE estar oculto y abrirse con un botón de menú (hamburguesa) en la cabecera. DEBE cerrarse al elegir una sección, al pulsar fuera de él o al pulsar de nuevo el botón.
- **FR-104**: El menú y su botón DEBEN poder usarse solo con teclado y estar identificados para lectores de pantalla («Abrir menú» / «Cerrar menú»).
- **FR-105**: La pantalla de presupuesto DEBE mostrar en la parte superior un botón «← Volver al historial» que lleva al historial conservando la búsqueda que había al abrir el presupuesto; si no la había o se abrió con un enlace directo, lleva al historial sin filtros.

**Usuarios**

- **FR-106**: La sección «Cuentas» de v1 pasa a llamarse «Usuarios» y DEBE mostrar la lista de cuentas (nombre, email, tipo, estado) con un botón «Añadir usuario» que abre un formulario con nombre, email, contraseña inicial y repetición de la contraseña. Solo el titular accede a ella.
- **FR-107**: Los formularios de cambio y de restablecimiento de contraseña DEBEN pedir también la contraseña nueva dos veces, como el alta de FR-106. En todos ellos, cada error DEBE mostrarse junto a su campo (email repetido, menos de 10 caracteres, contraseñas distintas).
- **FR-108**: Si la instalación no tiene cuenta de titular (en la práctica, ninguna cuenta: los asistentes solo los puede crear el titular), la herramienta DEBE mostrar, en lugar del inicio de sesión, la pantalla «Crear la cuenta del titular» con nombre, email, contraseña y repetición. Al crearla, el usuario entra directamente. Sustituye la creación por comando de FR-040 de la spec 001; sigue sin existir alta pública de cuentas.
- **FR-109**: Una vez existe una cuenta de titular, la pantalla «Crear la cuenta del titular» NO DEBE estar disponible para nadie; quien la abra ve el inicio de sesión. Aunque dos personas la envíen a la vez, NUNCA DEBE existir más de un titular.
- **FR-110**: La pantalla «Crear la cuenta del titular» NO pide código ni otra protección adicional: la primera persona que la completa crea el titular. Mientras exista, es la única pantalla accesible sin sesión además del inicio de sesión, y NO DEBE mostrar ningún dato del autónomo.

**Selectores**

- **FR-111**: Todo dato con opciones cerradas DEBE elegirse con un selector, sin escritura libre: tipo de documento, categoría y territorio del cliente, país del cliente, unidad del servicio y de la línea, tipo de IVA y tipo de retención.
- **FR-112**: El cliente DEBE tener un campo «Tipo de documento» con las opciones NIF, CIF, NIE, NIF-IVA UE y Otro documento extranjero, seguido del número de documento escrito a mano. Las opciones ofrecidas DEBEN depender de la categoría y el territorio (un Particular solo puede estar en territorios de España, como en la spec 001): Particular → NIF o NIE; Empresa/autónomo en España → NIF, CIF o NIE; Otro país UE → NIF-IVA UE (preseleccionado) u Otro documento extranjero; Fuera de la UE → Otro documento extranjero (preseleccionado). Si un cambio de categoría o territorio deja el tipo elegido fuera de las opciones, el selector se vacía y el número se conserva.
- **FR-113**: El país del cliente DEBE elegirse de una lista de países en español con «España» en primer lugar. Para territorio «Otro país UE» solo se ofrecen países de la UE distintos de España; para territorios de España, el país es «España» y no se puede cambiar.
- **FR-114**: Los clientes de v1 sin tipo de documento DEBEN mostrar «Sin indicar» y conservar su número; los clientes de v1 con país escrito a mano que no coincida con la lista DEBEN conservar el texto y mostrar «Revisar país» hasta que se elija uno de la lista. Las reglas de la spec 001 para descargar el PDF (FR-023) no cambian: el número de documento sigue siendo lo que se exige.

**Fechas**

- **FR-115**: Las fechas de emisión y de validez del presupuesto DEBEN poder elegirse con un calendario, en ordenador y en móvil, y mostrarse en formato DD/MM/AAAA en navegadores con calendario propio en español (excepción: ver «Navegador sin calendario propio» en casos límite). El calendario de validez NO DEBE permitir días anteriores a la fecha de emisión. Se mantienen las reglas de FR-011 de la spec 001.

**Logo del emisor**

- **FR-116**: El Perfil DEBE mostrar un apartado «Logo (aparece en tus PDF)» con la indicación de formatos y tamaño permitidos, la vista previa del logo actual si existe y los botones «Subir logo» (sin logo) o «Cambiar logo» y «Quitar logo» (con logo). «Quitar logo» pide confirmación. Las reglas de formato, tamaño y congelación en la primera descarga de la spec 001 (FR-002, FR-018) no cambian.
- Los clientes NO tienen logo (decisión de la sesión de aclaraciones).

**Tema (modo oscuro)**

- **FR-117**: Con sesión iniciada, el menú lateral DEBE incluir un selector «Tema» con tres opciones: «Claro», «Oscuro» y «Como el sistema», como última entrada del grupo «Configuración» (después de «Mi cuenta», con las entradas vigentes de FR-101) e inmediatamente antes de «Salir». En pantallas de menos de 1024 px está dentro del menú desplegable (FR-103).
- **FR-118**: Al elegir una opción, el tema DEBE aplicarse a la pantalla actual de inmediato, sin recargar, sin perder lo escrito en formularios ni las líneas de un presupuesto en edición y sin interrumpir el guardado automático.
- **FR-119**: El selector DEBE poder usarse solo con teclado y estar identificado para lectores de pantalla: nombre «Tema», sus tres opciones y cuál está activa.
- **FR-120**: El selector DEBE funcionar aunque el JavaScript del navegador no se ejecute; en ese caso basta con que el cambio se vea tras recargar la pantalla. Sin JavaScript, esa recarga pierde lo que no se haya guardado todavía, como cualquier recarga; la garantía de no perder nada de FR-118 aplica al cambio inmediato con JavaScript. Tras la recarga se vuelve a la misma pantalla; si esa pantalla es el resultado de un envío con errores (no se puede volver a abrir tal cual), se vuelve al historial.
- **FR-121**: La elección DEBE recordarse al recargar, al cambiar de sección y al cerrar y volver a abrir el navegador. Se recuerda **por dispositivo**: cada navegador guarda su elección, compartida por quien use ese equipo; no se guarda en la cuenta del usuario ni cambia los datos almacenados de la herramienta.
- **FR-122**: Sin elección previa, el tema DEBE ser «Como el sistema». Si el navegador no informa de ninguna preferencia, «Como el sistema» equivale a «Claro».
- **FR-123**: Con «Como el sistema», la app DEBE seguir la preferencia del dispositivo y cambiar sola si esta cambia mientras la app está abierta.
- **FR-124**: La elección explícita del usuario («Claro» u «Oscuro») DEBE prevalecer sobre la preferencia del sistema. Las pantallas sin sesión (inicio de sesión y «Crear la cuenta del titular») siguen la preferencia del sistema y no muestran el selector.
- **FR-125**: El tema oscuro DEBE cubrir todas las pantallas (las de sesión iniciada y las de sin sesión), el menú lateral y su fondo de superposición, los avisos (p. ej., «No se ha podido guardar»), los diálogos de confirmación, la ventana «Exportar…» de la spec 004 y su aviso «No hay presupuestos que exportar», los mensajes de error, las cinco etiquetas de estado de la spec 003 (las tres mostrables y las dos solo diseñadas) y los controles propios del navegador (calendarios, selectores desplegables, casillas y barras de desplazamiento).
- **FR-126**: Cada pantalla DEBE mostrarse desde el primer momento con el tema que corresponde, sin destello del tema contrario al cargar o recargar.
- **FR-127**: Ambos temas DEBEN cumplir los contrastes de FR-212 de la spec 003 (4,5:1 texto normal; 3:1 texto grande, bordes de campos, iconos con significado e indicador de foco) e incluir el indicador de foco de FR-213. Cada color conserva su significado en los dos temas (marca = azul, éxito = verde, aviso = ámbar, error = rojo) y los estados siguen sin distinguirse solo por color (FR-210 de la spec 003).
- **FR-128**: Los colores de ambos temas DEBEN definirse en el sistema visual de la spec 003, que sigue siendo el único lugar con colores (FR-202): la paleta clara y su variante oscura, que usa **los mismos nombres de color** con otros valores y no define nada más (ni tamaños, ni tipografía, ni separaciones). La variante oscura puede guardarse aparte de la clara; ninguna pantalla ni ningún otro sitio define colores propios. Cambiar un color en una de las dos paletas lo cambia en todas las pantallas con ese tema.
- **FR-129**: La vista previa del logo del emisor en Perfil (FR-116) DEBE mostrarse sobre una superficie clara en ambos temas, para que logos oscuros o con fondo transparente se distingan.
- **FR-130**: El PDF DEBE generarse siempre con la paleta clara de la spec 003, sea cual sea el tema de quien lo descarga; su contenido y aspecto no cambian.


### Key Entities

- **Cliente** (cambia): se añade *tipo de documento* (NIF, CIF, NIE, NIF-IVA UE, Otro documento extranjero o sin indicar). El campo «NIF/NIE o NIF-IVA» de v1 pasa a ser el *número de documento*; *país* pasa a elegirse de una lista.
- **Usuario** (sin cambios en sus datos): cambia solo cómo se crea la cuenta del titular (desde el navegador en la primera puesta en marcha).
- **Línea de presupuesto / Servicio** (sin cambios en sus datos): la unidad pasa a elegirse con selector.
- **Preferencia de tema** (nueva): una de «Claro», «Oscuro» o «Como el sistema» (por defecto). Se guarda en el dispositivo (navegador), no en la cuenta (FR-121). No forma parte de presupuestos, clientes, catálogo, perfil ni ajustes fiscales; no se guarda en el servidor, por lo que no aparece en las copias de seguridad ni en la exportación (.zip de la spec 004).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-101**: Un usuario que no conoce la herramienta llega a cualquier sección y vuelve al historial desde un presupuesto sin usar el botón «atrás» del navegador, en el 100 % de los intentos de una prueba con 5 tareas de navegación.
- **SC-102**: Una persona sin conocimientos técnicos crea la cuenta del titular en una instalación nueva y da de alta a un asistente en menos de 3 minutos, sin escribir ningún comando.
- **SC-103**: El 100 % de los campos con opciones cerradas listados en FR-111 se eligen con selector; no queda ninguno de escritura libre.
- **SC-104**: Cambiar la fecha de emisión de un presupuesto con el calendario lleva menos de 10 segundos en ordenador y en móvil.
- **SC-105**: En un móvil de 360 px, el menú se abre y se cierra con un toque y ninguna pantalla presenta desplazamiento horizontal.
- **SC-106**: Tras la actualización, el 100 % de los clientes, presupuestos e importes creados con v1 siguen presentes y con los mismos importes.
- **SC-107**: Cada escenario de aceptación de esta spec puede comprobarse en la app siguiendo pasos escritos, sin leer código, incluida la creación del titular.
- **SC-108**: Con el menú abierto, cambiar de tema lleva un solo toque o pulsación y menos de 5 segundos, sin pérdida de datos en el 100 % de los intentos.
- **SC-109**: En un recorrido de todas las pantallas en oscuro a 360 px y a 1280 px, el 100 % de los textos, campos, botones, avisos y etiquetas de estado se leen con claridad y no queda ninguna zona con los colores del tema claro, salvo la vista previa del logo sobre blanco (FR-129).
- **SC-110**: El 100 % de las combinaciones de texto/fondo y de controles cumplen los contrastes de FR-212 de la spec 003 en ambos temas, medidos con cualquier comprobador de contraste.
- **SC-111**: El 100 % de los PDF descargados con la app en oscuro son iguales a los descargados en claro.
- **SC-112**: El tema elegido se mantiene en el 100 % de las recargas, cambios de sección y reaperturas del navegador, sin destello del tema contrario.

## Assumptions

- Esta iteración no cambia cálculos, numeración, reglas fiscales (RN1–RN11) ni el contenido del PDF.
- El tipo de documento es informativo: la herramienta sigue sin validar el formato del número (supuesto de la spec 001).
- El punto de corte entre «móvil» y «escritorio» para el menú es 1024 px; tableta usa el comportamiento de móvil.
- El calendario puede ser el propio del navegador; no se exige un diseño concreto, solo el comportamiento de US5.
- La lista de países es la estándar de países en español; la lista de la UE es la vigente a la fecha de la entrega.
- Las operaciones de copias de seguridad, restauración y restablecimiento de la contraseña del titular siguen siendo tareas del administrador técnico, con los pasos escritos de la spec 001.
- La guía de administración se actualizará para quitar el comando de creación del titular y para indicar que el titular se cree nada más arrancar el servidor.
- **Modo oscuro**: no cambia tipografía, tamaños, separaciones ni maquetación de la spec 003. El color de marca puede aclararse en el tema oscuro (mismo tono, más luminoso) para cumplir FR-127; el PDF conserva el color de marca actual.
- **Modo oscuro**: elegir tema no altera presupuestos, clientes, catálogo, perfil ni ajustes fiscales.
- **Modo oscuro**: se ofrecen tres opciones en lugar de un interruptor claro↔oscuro, para poder volver a seguir al sistema tras haber elegido un tema.
- **Riesgo aceptado (FR-110)**: entre el arranque del servidor y la creación del titular, cualquiera que conozca la dirección podría crear el titular. Se acepta por simplicidad (principio I). Si ocurre, el administrador técnico lo detecta porque no puede crear el titular y reinstala con los datos vacíos (aún no hay datos que perder).

### Fuera de alcance

- Pestañas o vistas nuevas no descritas aquí (p. ej., panel de inicio con resúmenes).
- Personalizar el orden o los colores del menú.
- Cambiar los permisos de titular y asistente o añadir roles nuevos.
- Recuperación de contraseña por email (sigue fuera, como en la spec 001).
- Validación online del número de documento (VIES u otros).
- Selector de hora o rangos de fechas en el historial.
- Logo de los clientes (ni en la herramienta ni en el PDF).
- Guardar el tema en la cuenta del usuario o sincronizarlo entre dispositivos.
- Temas adicionales al claro y el oscuro (alto contraste propio, sepia, colores personalizables o color de marca elegido por el usuario).
- PDF en oscuro o elegir el tema del PDF.
- Programar el cambio de tema por horario dentro de la app (para eso está «Como el sistema»).
- Selector de tema en las pantallas sin sesión.
