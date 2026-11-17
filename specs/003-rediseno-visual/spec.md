# Feature Specification: PresupuestosPro v1.2 — Rediseño visual profesional y accesible

**Feature Branch**: `003-rediseno-visual`

**Created**: 2026-11-14

**Status**: Draft

**Enmienda (2026-11-17)**: la [spec 002, ampliación de modo oscuro](../002-mejoras-ui-usuarios/spec.md) (US7, FR-117 a FR-130) añade un tema oscuro conmutable como segunda paleta de este sistema visual. Quedan modificados el caso límite «Navegador con modo oscuro del sistema», el supuesto «Sin modo oscuro», la exclusión «Modo oscuro» de Fuera de alcance y la lectura de FR-202 («único lugar»). El resto de esta spec no cambia; el PDF sigue teniendo solo la paleta clara.

**Input**: User description: "rediseñar la apariencia visual de toda la aplicación para que resulte profesional y sobria: tipografía consistente, paleta de colores limitada definida en un único lugar, espaciado uniforme, jerarquía visual clara entre títulos, tablas, formularios y totales, y estados visuales distinguibles para los presupuestos (Borrador, Enviado, Aceptado, Rechazado, Caducado). El rediseño debe aplicarse también a la plantilla del PDF para que el documento que recibe el cliente transmita la misma imagen profesional. Debe mantenerse el enfoque mobile-first ya existente y todos los textos en español de España. La lógica de negocio, los cálculos, la API y el esquema de datos no deben cambiar en absoluto, de cumplir criterios minimos y buenas practicas de accesibilidad"

## Contexto

- **Punto de partida**: iteración sobre PresupuestosPro v1.1 (`specs/001-presupuestos-pro/spec.md` y `specs/002-mejoras-ui-usuarios/spec.md`). Todo lo definido allí sigue vigente: pantallas, textos, reglas, cálculos, rutas y datos. Esta spec **solo cambia la apariencia**.
- **Problema**: la app funciona, pero su aspecto es el de un prototipo: tamaños de letra y separaciones distintos en cada pantalla, colores repetidos sin criterio, totales que no destacan sobre el resto y un PDF correcto pero poco cuidado. El autónomo envía ese PDF a sus clientes, y la imagen que da es la suya.
- **Usuarios afectados**: titular y asistentes (todas las pantallas) y, de forma indirecta, los clientes del autónomo (el PDF).
- **Límite explícito del encargo**: la lógica de negocio, los cálculos, las rutas y el esquema de datos **no cambian** (ver FR-215 y «Fuera de alcance»).

## Clarifications

### Session 2026-11-14

- Q: ¿Qué estados de presupuesto se muestran, si el esquema de datos no puede cambiar? → A: Se diseñan las cinco etiquetas (Borrador, Enviado, Aceptado, Rechazado, Caducado) en el sistema visual, pero solo se muestran las tres que se deducen de los datos existentes: Borrador, Enviado y Caducado. Aceptado y Rechazado quedan diseñadas para una futura funcionalidad que guarde esa decisión.
- Q: Si un presupuesto se ha descargado y además su fecha de validez ya ha pasado, ¿qué estado muestra? → A: Caducado tiene prioridad: con la fecha pasada se muestra «Caducado», se haya descargado o no.
- Q: ¿La app y el PDF usan la misma tipografía incluida con la aplicación o las fuentes instaladas en cada dispositivo o servidor? → A: Una única tipografía libre incluida con la aplicación, usada en la app y en el PDF (idéntica en cualquier dispositivo y servidor).
- Q: ¿El PDF usa el color de marca de la app en algunos acentos o es completamente en negro y grises? → A: Color de marca solo en unos pocos acentos (título, cabecera de la tabla, línea sobre el total); el resto en negro y grises, legible impreso en blanco y negro.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Una app con aspecto profesional y coherente en todas las pantallas (Priority: P1)

Como titular o asistente, quiero que todas las pantallas compartan la misma tipografía, los mismos colores y las mismas separaciones, con títulos, formularios, listas y totales claramente diferenciados, para trabajar con una herramienta que transmita seriedad y en la que encuentre cada cosa a la primera.

**Why this priority**: es el núcleo del encargo y afecta a todas las pantallas; sin ello no hay rediseño.

**Independent Test**: recorrer las 13 pantallas en un móvil de 360 px y en un ordenador de 1280 px y comprobar, con la guía de verificación, que los títulos, botones, campos, listas y totales se ven igual en todas y que el total de un presupuesto es lo que más destaca de su bloque.

**Acceptance Scenarios**:

1. **Given** cualquier pantalla con sesión iniciada, **When** la abro, **Then** veo el título de la pantalla como el texto más grande del contenido, con el mismo tamaño, peso y separación que en las demás pantallas.
2. **Given** dos pantallas distintas con formularios (p. ej. Perfil y Cliente), **When** las comparo, **Then** etiquetas, campos, ayudas, mensajes de error y botones tienen el mismo aspecto y la misma separación.
3. **Given** un presupuesto con líneas, **When** miro el bloque de totales, **Then** el «Total» se distingue del resto de filas (base, IVA, retención) por tamaño o peso y por una separación visible, sin depender solo del color.
4. **Given** una acción principal (p. ej. «Guardar perfil», «Descargar PDF») y una secundaria o peligrosa (p. ej. «Borrar presupuesto»), **When** las veo juntas, **Then** las tres clases de botón (principal, secundario, peligro) se distinguen claramente y son iguales en toda la app.
5. **Given** un móvil de 360 px, **When** recorro cualquier pantalla, **Then** no hay desplazamiento horizontal, los campos ocupan el ancho disponible y los botones y enlaces tienen un área táctil de al menos 44 × 44 px (FR-214a).
6. **Given** los mensajes de éxito, aviso y error existentes, **When** aparecen, **Then** cada tipo tiene un aspecto propio y constante en toda la app e incluye un icono o texto que lo identifica además del color.

---

### User Story 2 - Un PDF que el cliente perciba como profesional (Priority: P1)

Como autónomo, quiero que el PDF que envío a mis clientes tenga la misma imagen cuidada que la app (tipografía, colores sobrios, tabla de líneas legible y totales destacados), para que mi presupuesto inspire confianza.

**Why this priority**: es lo único que ve el cliente final; su aspecto repercute directamente en la imagen del autónomo.

**Independent Test**: descargar el PDF de un presupuesto con logo, 3 líneas, IVA y retención, y otro con 40 líneas; comprobar con la guía de verificación la jerarquía, la legibilidad y que el contenido es exactamente el mismo que en v1.1.

**Acceptance Scenarios**:

1. **Given** un presupuesto descargable, **When** descargo el PDF, **Then** contiene exactamente los mismos bloques, textos, importes y orden que en v1.1 (contrato `pdf-presupuesto.md` de la 001) y solo cambia su aspecto.
2. **Given** el PDF, **When** lo miro, **Then** se distinguen a simple vista el emisor, el título con el número, las fechas, el cliente, la tabla de líneas y el bloque de totales, con el «Total» como cifra más destacada.
3. **Given** la tabla de líneas, **When** la leo, **Then** las columnas numéricas (cantidad, precio unitario, importe) están alineadas a la derecha y las filas se distinguen entre sí (separadores o fondo alterno).
4. **Given** un presupuesto con muchas líneas, **When** el PDF ocupa varias páginas, **Then** el encabezado de la tabla se repite en cada página y el aspecto es el mismo en todas (FR-024 de la 001).
5. **Given** el PDF impreso en blanco y negro, **When** lo leo, **Then** toda la información y la jerarquía siguen siendo legibles (nada depende solo del color).
6. **Given** un perfil con logo y otro sin logo, **When** descargo el PDF, **Then** ambos se ven equilibrados: el logo no se deforma ni desplaza otros datos y, sin logo, la cabecera no deja un hueco vacío.
7. **Given** el PDF, **When** busco elementos de color, **Then** el color de marca aparece solo en el título con el número, la cabecera de la tabla de líneas y la línea del «Total»; todo lo demás (salvo el logo del autónomo) está en negro y grises.

---

### User Story 3 - Ver de un vistazo el estado de cada presupuesto (Priority: P2)

Como titular o asistente, quiero que cada presupuesto muestre su estado con una etiqueta visual distinguible en el historial y en la pantalla del presupuesto, para saber de un vistazo cuáles están pendientes, cuáles han caducado y cuáles están cerrados.

**Why this priority**: aporta orientación en el historial sin cambiar los datos: los estados mostrables (Borrador, Enviado, Caducado) se deducen de lo que ya se guarda (FR-209).

**Independent Test**: con presupuestos en cada estado mostrable, abrir el historial en 360 px y en 1280 px y comprobar que cada estado tiene una etiqueta con texto y aspecto propios, distinguibles también sin color.

**Acceptance Scenarios**:

1. **Given** el historial con presupuestos en distintos estados, **When** lo miro, **Then** cada presupuesto muestra una etiqueta con el nombre de su estado en texto, con un aspecto distinto por estado.
2. **Given** las etiquetas de estado, **When** las veo en escala de grises o con un filtro de daltonismo, **Then** sigo distinguiendo el estado por su texto y su icono (y, en «Borrador» y «Caducado», también por su forma), no solo por el color.
3. **Given** un presupuesto cuya fecha «Válido hasta» ya ha pasado, descargado o no, **When** lo veo en el historial o lo abro, **Then** aparece como «Caducado» y solo con esa etiqueta.
4. **Given** la pantalla de un presupuesto, **When** la abro, **Then** su estado aparece junto al número, con la misma etiqueta que en el historial.
5. **Given** un presupuesto «Caducado», **When** cambio su fecha «Válido hasta» a una fecha futura, **Then** vuelve a mostrarse como «Enviado» o «Borrador» según se haya descargado o no.

---

### User Story 4 - Usar la app con teclado, lector de pantalla o con dificultades de visión (Priority: P2)

Como persona que usa el teclado, un lector de pantalla, el zoom del navegador o que tiene baja visión, quiero poder usar todas las pantallas sin perder información ni funcionalidad, para que la herramienta no me excluya.

**Why this priority**: es un requisito mínimo del encargo y una buena práctica; muchas mejoras visuales (contraste, foco, tamaños) lo afectan directamente.

**Independent Test**: recorrer las pantallas principales solo con el teclado, con el zoom al 200 % y con un lector de pantalla, siguiendo la guía de verificación; medir el contraste de los colores de la paleta con un comprobador de contraste.

**Acceptance Scenarios**:

1. **Given** cualquier pantalla, **When** la recorro con Tab, **Then** cada elemento interactivo muestra un indicador de foco claramente visible (no solo un cambio sutil de color) y el orden sigue el orden visual.
2. **Given** los textos y los controles, **When** mido su contraste, **Then** el texto normal tiene al menos 4,5:1, el texto grande al menos 3:1 y los bordes de campos, iconos e indicadores de foco al menos 3:1 frente a su fondo.
3. **Given** el navegador con zoom al 200 % (o una ventana equivalente a 320 px de ancho), **When** uso cualquier pantalla, **Then** todo el contenido y las acciones siguen disponibles sin desplazamiento horizontal ni textos cortados o solapados.
4. **Given** un lector de pantalla, **When** recorro una pantalla, **Then** hay un único título principal, los encabezados siguen un orden lógico, las tablas anuncian sus cabeceras, cada campo tiene su etiqueta y los estados de los presupuestos se leen como texto.
5. **Given** que el sistema tiene activada la preferencia de reducir el movimiento, **When** abro el menú u ocurre cualquier transición, **Then** no hay animaciones (o son instantáneas).
6. **Given** el comienzo de cualquier pantalla con sesión, **When** pulso Tab por primera vez, **Then** aparece un enlace «Saltar al contenido» que lleva directamente al contenido principal.

---

### Edge Cases

- **Textos largos**: un nombre de cliente, una descripción de línea o un importe muy largos (p. ej. 1.000.000,00 €) no rompen la maquetación ni en 360 px ni en el PDF; el texto se ajusta en varias líneas y los importes no se cortan.
- **Presupuesto sin cliente o sin líneas**: los bloques vacíos se ven ordenados (mensaje en texto suave), sin huecos ni bordes descolgados.
- **Cliente anonimizado**: el aviso existente («Cliente eliminado…») conserva su significado y se ve con el estilo de aviso común.
- **Logo con proporciones extremas** (muy ancho o muy alto, SVG sin tamaño): se limita a un área máxima sin deformarse, en la pantalla de Perfil y en el PDF.
- **Navegador con modo oscuro del sistema**: *(enmendado 2026-11-17)* lo regula la spec 002 (FR-122 a FR-124): con «Como el sistema», que es el valor por defecto, la app se ve en oscuro; con «Claro», se sigue viendo con su paleta clara y legible. En ambos casos los controles nativos no quedan ilegibles.
- **Tamaño de letra del navegador aumentado** (p. ej. 20 px por defecto): la app respeta la preferencia y escala sin solapamientos.
- **Impresión de una pantalla** (no del PDF): no es un objetivo; no debe empeorar respecto a v1.1.
- **Presupuestos ya descargados antes del rediseño**: al volver a descargarlos, el PDF sale con el nuevo diseño y con los mismos datos congelados (FR-018 de la 001); los PDF ya enviados no cambian.
- **Estado y fecha de validez en el límite**: un presupuesto cuyo «Válido hasta» es hoy todavía no está «Caducado»; pasa a estarlo al día siguiente (fecha de España, D18 de la 001).
- **Presupuesto caducado que se edita o se vuelve a descargar**: sigue mostrando «Caducado» mientras su «Válido hasta» sea anterior a hoy; descargar el PDF no cambia el estado mostrado (FR-209, prioridad).

## Requirements *(mandatory)*

### Functional Requirements

**Sistema visual común**

- **FR-201**: La app y el PDF DEBEN usar una única familia tipográfica libre (de licencia que permita distribuirla), incluida con la aplicación, para todo el texto; DEBE verse igual en cualquier dispositivo y en el PDF generado en cualquier servidor, sin depender de las fuentes instaladas. La familia DEBE incluir los caracteres del español (tildes, «ñ», «ü», «¿», «¡», «€», «·», «—») y cifras de ancho fijo para alinear importes. La escala de tamaños DEBE ser cerrada, de como máximo 6 tamaños de texto, usada igual en todas las pantallas.
- **FR-202**: La paleta de colores DEBE estar definida en un único lugar y todas las pantallas DEBEN usar solo colores de esa paleta. La paleta DEBE ser limitada: un color de marca/acción, una escala de neutros (texto, texto suave, bordes, fondos) y un color por cada significado (éxito, aviso, error) y por cada estado de presupuesto mostrable. Cambiar un color en ese lugar DEBE cambiarlo en toda la app. *(Desde 2026-11-17, la variante oscura de la paleta de la spec 002, FR-128, forma parte de ese mismo lugar: mismos nombres de color, y ningún otro sitio define colores.)*
- **FR-203**: El espaciado (márgenes, separaciones entre campos, secciones y elementos de lista) DEBE seguir una escala única y cerrada, definida en el mismo lugar que la paleta y aplicada igual en todas las pantallas.
- **FR-204**: La app DEBE tener una jerarquía visual constante: título de pantalla (uno por pantalla) › título de sección › texto normal › texto secundario. Los títulos de pantalla y de sección DEBEN verse igual en todas las pantallas.
- **FR-205**: Los formularios DEBEN tener un aspecto común: etiqueta encima del campo, texto de ayuda debajo con estilo secundario, mensaje de error debajo del campo con estilo de error e icono o prefijo textual, campos con el mismo alto, borde y radio, y estado de foco visible.
- **FR-206**: Los botones DEBEN reducirse a tres variantes con aspecto constante en toda la app: principal (una por grupo de acciones como norma), secundaria y peligro. Los enlaces con aspecto de botón (p. ej. «Descargar PDF», «← Volver al historial») DEBEN usar esas mismas variantes.
- **FR-207**: Las listas y tablas (historial, clientes, catálogo, usuarios, líneas del presupuesto) DEBEN tener un aspecto común: cabeceras o etiquetas diferenciadas, filas separadas visualmente, importes alineados a la derecha con cifras de ancho fijo, y, en móvil, presentación en tarjetas cuando la tabla no quepa.
- **FR-208**: El bloque de totales del presupuesto (pantalla y PDF) DEBE destacar el «Total» como la cifra más visible del bloque (mayor tamaño o peso y separación superior), con las demás filas (base imponible, IVA, retención) en un nivel inferior y alineadas a la derecha.

**Estados de los presupuestos**

- **FR-209**: Cada presupuesto DEBE mostrar una etiqueta de estado en el historial y junto al número en su pantalla. El estado se deduce de los datos existentes, sin guardar nada nuevo:
  - **Borrador**: el PDF no se ha descargado nunca.
  - **Enviado**: el PDF se ha descargado al menos una vez.
  - **Caducado**: la fecha «Válido hasta» es anterior a hoy (fecha de España).
  - **Prioridad**: cada presupuesto muestra un único estado. «Caducado» prevalece sobre los demás: con la fecha pasada se muestra «Caducado», se haya descargado o no. Si no ha caducado, se muestra «Enviado» o «Borrador» según se haya descargado o no.
- **FR-209a**: El sistema visual DEBE definir también las etiquetas **Aceptado** y **Rechazado** (texto, color de la paleta y forma o icono), aunque ningún presupuesto las muestre en esta versión: quedan preparadas para una funcionalidad futura que guarde esa decisión (fuera de alcance).
- **FR-210**: Cada estado (los mostrables y los solo diseñados de FR-209a) DEBE tener una etiqueta con su nombre en texto, un color de la paleta y un icono propio. Además, «Borrador» y «Caducado» DEBEN distinguirse por su forma (p. ej. borde discontinuo o texto en cursiva), para que los tres estados mostrables se diferencien entre sí sin color incluso sin fijarse en el icono. Las etiquetas DEBEN cumplir el contraste de FR-212.
- **FR-211**: El estado NO DEBE aparecer en el PDF que recibe el cliente (es información de gestión interna).

**Accesibilidad (mínimo: nivel AA de las pautas WCAG 2.1)**

- **FR-212**: El contraste DEBE ser de al menos 4,5:1 para texto normal, 3:1 para texto grande (≥ 24 px, o ≥ 18,66 px en negrita) y 3:1 para bordes de campos, iconos con significado e indicadores de foco, en la app y en el PDF.
- **FR-213**: Todo elemento interactivo DEBE mostrar un indicador de foco visible y constante en toda la app; el orden de foco DEBE seguir el orden visual; DEBE existir un enlace «Saltar al contenido» al inicio de cada pantalla con sesión.
- **FR-214**: Ninguna información DEBE transmitirse solo por el color (estados, errores, avisos, campos obligatorios, sección actual del menú). La app DEBE seguir siendo usable con zoom del 200 % y con un ancho de 320 px sin desplazamiento horizontal (además de la regla de 360 px de la 001), respetar el tamaño de letra elegido en el navegador y desactivar animaciones cuando el sistema pida reducir el movimiento. Cada pantalla DEBE tener un único título principal y encabezados en orden lógico; las tablas DEBEN tener cabeceras asociadas a sus celdas.
- **FR-214a**: Todo elemento interactivo (botones, enlaces del menú, enlaces con aspecto de botón, casillas y selectores) DEBE tener un área táctil de al menos 44 × 44 px, aunque su parte visible sea menor.
- **FR-214b**: Cada pantalla y el PDF DEBEN declarar el español como idioma del documento, para que los lectores de pantalla lo pronuncien correctamente.

**Límites del cambio**

- **FR-215**: El rediseño NO DEBE cambiar la lógica de negocio, los cálculos, las rutas y sus respuestas (salvo el marcado HTML y los estilos), los datos guardados ni su estructura, ni el contenido del archivo de exportación. Los textos visibles DEBEN mantenerse salvo los nuevos que esta spec introduce (etiquetas de estado, «Saltar al contenido», prefijos de mensajes) y DEBEN estar en español de España.
- **FR-216**: El rediseño DEBE mantener el enfoque mobile-first y todo lo definido en la 002 para la navegación (menú lateral desde 1024 px, botón de menú por debajo, sección actual resaltada).
- **FR-217**: El PDF DEBE aplicar la misma tipografía y jerarquía que la app y usar el color de marca de la paleta solo en unos pocos acentos (el título «PRESUPUESTO» con el número, la cabecera de la tabla de líneas y la línea que separa el «Total»); el resto del documento DEBE ir en negro y grises de la paleta, sin fondos de color en bloques grandes. El PDF DEBE conservar íntegros el contenido, el orden y las reglas de paginación del contrato del PDF de la 001. El PDF DEBE seguir generándose sin descargar nada de internet (FR-028 de la 001): usa la tipografía incluida con la aplicación (FR-201).
- **FR-218**: El rediseño NO DEBE añadir dependencias de servicios externos (tipos de letra, iconos o estilos cargados desde internet) en la app ni en el PDF.

### Key Entities

- **Sistema visual** (no es un dato guardado): conjunto único de decisiones de diseño (tipografía, escala de tamaños, paleta, escala de espaciado, radios, sombras, estilos de foco) del que beben todas las pantallas y el PDF.
- **Estado del presupuesto** (mostrado, no guardado como dato nuevo): etiqueta visible que resume la situación de un presupuesto. En esta versión se deduce de si el PDF se ha descargado alguna vez y de la fecha «Válido hasta» (FR-209). Aceptado y Rechazado solo existen como diseño (FR-209a).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-201**: En las 13 pantallas, comparadas en 360 px y 1280 px, el revisor no encuentra ninguna diferencia de tipografía, tamaño de título, aspecto de campo, botón, lista o mensaje entre pantallas (0 incoherencias en la lista de comprobación de la guía de verificación).
- **SC-202**: El 100 % de las combinaciones de texto/fondo y de controles de la paleta cumplen los contrastes de FR-212, medidos con cualquier comprobador de contraste.
- **SC-203**: Una persona puede completar el flujo principal (entrar, crear presupuesto, elegir cliente, añadir una línea, descargar el PDF) solo con el teclado, viendo en todo momento dónde está el foco.
- **SC-204**: Con zoom al 200 % y a 320 px de ancho, el 100 % de las pantallas se usan sin desplazamiento horizontal y sin textos cortados o solapados.
- **SC-205**: En un historial con presupuestos de cada estado mostrable, 5 de 5 personas identifican correctamente el estado de cada uno en menos de 5 segundos por presupuesto, también viendo la pantalla en escala de grises.
- **SC-206**: Colocados uno junto a otro un PDF de v1.1 y el del rediseño del mismo presupuesto, contienen exactamente los mismos textos, importes y orden de bloques (0 diferencias de contenido), y al menos 4 de 5 personas eligen el nuevo como «más profesional».
- **SC-207**: Impreso en blanco y negro, el PDF del rediseño se lee completo y el «Total» se identifica a la primera.
- **SC-208**: Todos los tests automáticos existentes siguen pasando sin modificar ninguna regla de cálculo, ruta ni dato, y una base de datos de v1.1 funciona con el rediseño sin ningún paso de actualización.
- **SC-209**: Cambiar el color de marca en el único lugar donde está definido cambia ese color en el 100 % de las pantallas sin tocar nada más (comprobable por el administrador técnico, «(Técnico)» en la guía).
- **SC-210**: Abiertas la misma pantalla en dos dispositivos distintos (p. ej. un Mac y un móvil Android) y el PDF del mismo presupuesto, el revisor comprueba que los tres usan la misma tipografía y que todos los caracteres del español (incluido «€») se ven correctamente.

## Assumptions

- **Nivel de accesibilidad**: «criterios mínimos y buenas prácticas» se interpreta como el nivel AA de las pautas WCAG 2.1, la referencia habitual en España (norma UNE-EN 301 549). No se persigue el nivel AAA.
- **Tipografía**: una fuente libre incluida con la aplicación (FR-201); la familia concreta se elige en el plan entre las que cumplan los requisitos de caracteres y cifras. Si la fuente no llegara a cargarse en un dispositivo, la app sigue siendo legible con una fuente de reserva del sistema.
- **Modo oscuro** *(enmendado 2026-11-17)*: esta spec definió un único tema claro. El modo oscuro entró después como alcance nuevo en la spec 002 (US7): es una segunda paleta con los mismos nombres de color, que cumple los mismos contrastes (FR-212) y no cambia tipografía, tamaños, separaciones ni el PDF.
- **Sin personalización por autónomo**: la paleta es la misma para todas las instalaciones; no se adapta a los colores de la marca de cada autónomo (no se pide). El logo del autónomo sigue siendo su elemento de marca en el PDF.
- **Iconos**: si se usan, son pocos, sencillos y van incluidos con la aplicación; nunca sustituyen al texto.
- **Marcado HTML**: cambiar la estructura de las plantillas (clases, encabezados, envoltorios) para aplicar el diseño o mejorar la accesibilidad se considera parte del rediseño y no un cambio de la API (FR-215).
- **PDF y estados**: el estado del presupuesto es información interna y no se imprime (FR-211); el cliente recibe el mismo documento con independencia del estado.
- **Verificación**: la comprobación de contraste, teclado, zoom y lector de pantalla se hace siguiendo la guía de verificación con herramientas gratuitas del navegador; la prueba con 5 personas (SC-205, SC-206) puede hacerse de manera informal con usuarios reales o compañeros.

### Fuera de alcance

- Cualquier cambio en cálculos, reglas fiscales, numeración, rutas, datos guardados o exportación (FR-215).
- Temas adicionales o colores personalizables por autónomo. *(Enmendado 2026-11-17: el modo oscuro ya no está fuera de alcance; lo define la spec 002, US7.)*
- Nuevas pantallas, filtros del historial por estado, acciones nuevas sobre los presupuestos o cambios de flujo.
- Marcar presupuestos como Aceptado o Rechazado (requiere guardar un dato nuevo); solo se dejan diseñadas sus etiquetas (FR-209a).
- Cambios en el contenido del PDF (bloques, textos, orden) o numeración de páginas.
- Logo de cliente (excluido en la 002).
