# Feature Specification: PresupuestosPro v1.3 — Exportar en un .zip

**Feature Branch**: `004-exportar-zip`

**Created**: 2026-11-17

**Status**: Draft

**Input**: User description: "Exportar todos mis presupuestos en un .zip: que el autónomo pueda llevarse todos sus presupuestos de una sola vez, en un único archivo comprimido, como copia de seguridad y para archivarlos donde quiera. Un botón «Exportar…» visible en la lista de presupuestos que abre una ventana previa (modal) para elegir entre exportar todo o seleccionar qué presupuestos exportar; el zip contiene un PDF por presupuesto (el mismo que ya genera la app) y un archivo de datos con toda la información (presupuestos, catálogo, perfil y logo). Solo lectura. Sin importar, sin Excel/CSV, sin copias automáticas, sin enviar por email ni a la nube."

## Contexto

- **Punto de partida**: PresupuestosPro v1.2 (specs 001, 002 y 003). Todo lo definido allí sigue vigente: presupuestos, PDF, estados, cuentas y reglas. Esta spec **añade una forma de exportar** y sustituye a la exportación en archivo de datos que ya existe.
- **Problema**: hoy el autónomo solo puede descargar un archivo de datos que no sabe abrir y los PDF de uno en uno. Para archivar su trabajo o tener una copia propia tendría que descargar cada presupuesto a mano.
- **Usuarios afectados**: titular y asistentes (cualquier cuenta con sesión iniciada). Es un autónomo no técnico: sabe descargar un archivo y descomprimir un .zip con doble clic, y no tiene por qué saber qué hay dentro de un «archivo de datos».
- **Límite del encargo**: la exportación es **solo lectura**. No cambia presupuestos, estados, numeración ni ningún otro dato (FR-305).

## Clarifications

### Session 2026-11-17

- Q: La primera descarga de un PDF fija los datos del emisor y marca el presupuesto como «Enviado». ¿Qué hace la exportación con los presupuestos que aún son «Borrador»? → A: Solo se incluye PDF de los presupuestos ya descargados (los que ya tienen su PDF fijado). Los borradores van únicamente en el archivo de datos, y la exportación no cambia su estado.
- Q: ¿Qué relación tiene el zip con la exportación en archivo de datos que ya existe? → A: El zip la sustituye. Se retira la descarga suelta del archivo de datos y el zip pasa a ser la única exportación; el archivo de datos va dentro del zip con el mismo contenido que la exportación actual.
- Q: ¿Cómo se nombra cada PDF, dado que el ejemplo («2026-001 - Estudio García») difiere del número real de la app («PRE-2026-001»)? → A: Número tal como lo muestra la app + cliente, p. ej. «PRE-2026-001 - Estudio García.pdf». El número es único, así que ningún nombre se repite.
- Q: ¿Quién puede exportar y qué ve el usuario mientras tarda? → A: Titular y asistentes (cualquier cuenta con sesión). Al pulsar, el botón se desactiva y muestra «Preparando la copia…» hasta que empieza la descarga; sin barra de progreso.

### Session 2026-11-17 (ampliación: paso previo con ventana modal)

- Q: ¿Qué se elige al «seleccionar qué exportar»? → A: Presupuestos individuales, con una casilla por presupuesto y «marcar todos».
- Q: ¿Qué lleva el archivo de datos cuando se exporta una selección? → A: Con «Todo» lleva todo (copia completa). Si el usuario selecciona algo en concreto, el archivo de datos lleva solo lo seleccionado.
- Q: ¿Qué pasa con los presupuestos en Borrador en la selección? → A: No aparecen en la lista de selección (solo se ofrecen los que tienen PDF). Los borradores solo viajan en la opción «Todo».
- Q: ¿Cómo se llama el botón de la lista? → A: «Exportar…», que abre la ventana; el estado «Preparando la copia…» se muestra en el botón de descarga de la ventana.

### Session 2026-11-17 (clarify)

- Q: ¿Cómo debe llamarse el .zip cuando se exporta una selección, para no confundirlo con una copia completa? → A: Con «Todo»: `presupuestospro-copia-AAAA-MM-DD.zip`; con «Seleccionar»: `presupuestospro-seleccion-AAAA-MM-DD.zip`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Llevarme todos mis presupuestos de una vez (Priority: P1)

Como autónomo, quiero pulsar «Exportar…» en la lista de presupuestos, elegir «Todo» en la ventana que se abre y descargar un único .zip con mis presupuestos en PDF y un archivo con todos mis datos, para tener una copia propia y archivarla donde quiera.

**Why this priority**: es todo el valor de la funcionalidad; sin ella no hay exportación.

**Independent Test**: con 3 presupuestos ya descargados, pulsar «Exportar…», dejar «Todo» y descargar; descomprimir el archivo y comprobar que hay 3 PDF con nombre «número - cliente» y un archivo de datos, y que cada PDF es el mismo que se descarga desde la app.

**Acceptance Scenarios**:

1. **Given** 3 presupuestos ya descargados, **When** pulso «Exportar…» y, en la ventana, «Descargar .zip» con «Todo» marcado, **Then** se descarga un único archivo llamado `presupuestospro-copia-AAAA-MM-DD.zip` con la fecha de hoy.
2. **Given** el zip descargado, **When** lo descomprimo con doble clic, **Then** veo 3 PDF con nombre «número - cliente» y un archivo de datos, y nada más.
3. **Given** un PDF del zip y el PDF que descargo desde la app para ese mismo presupuesto, **When** los abro, **Then** tienen exactamente el mismo contenido, aspecto e importes (p. ej. el presupuesto de control con total 3.604,00 €).
4. **Given** un presupuesto cuyo perfil del emisor cambió después de su primera descarga, **When** exporto, **Then** su PDF del zip muestra los datos del emisor de la primera descarga, igual que su descarga normal.
5. **Given** cualquier cuenta con sesión (titular o asistente), **When** abro la lista de presupuestos, **Then** veo el botón «Exportar…» y puedo exportar.

---

### User Story 1b - Elegir qué presupuestos exportar (Priority: P1)

Como autónomo, quiero poder elegir en una ventana previa si exporto todo o solo algunos presupuestos concretos, para llevarme, por ejemplo, solo los de un cliente o los de un trimestre sin descargar el resto.

**Why this priority**: es el paso previo pedido para la exportación; define cómo se usa el botón.

**Independent Test**: con 5 presupuestos descargados y 1 borrador, abrir «Exportar…», elegir «Seleccionar», marcar 2 y descargar; comprobar que el zip tiene 2 PDF y que el archivo de datos solo contiene esos 2 presupuestos.

**Acceptance Scenarios**:

1. **Given** la lista de presupuestos, **When** pulso «Exportar…», **Then** se abre una ventana con dos opciones, «Todo» (marcada por defecto) y «Seleccionar qué exportar», y un botón «Descargar .zip» (sin que se descargue nada hasta pulsarlo).
2. **Given** la ventana abierta, **When** elijo «Seleccionar qué exportar», **Then** veo una lista con una casilla por presupuesto (número, cliente y estado), una opción «Marcar todos» y el recuento de marcados.
3. **Given** la lista de selección, **When** la miro, **Then** solo contiene presupuestos ya descargados; los borradores no aparecen.
4. **Given** 2 presupuestos marcados, **When** pulso «Descargar .zip», **Then** se descarga `presupuestospro-seleccion-AAAA-MM-DD.zip` (no «copia») y el zip contiene exactamente 2 PDF y un archivo de datos con solo esos 2 presupuestos (con sus líneas y sus clientes).
5. **Given** «Seleccionar» sin ninguna casilla marcada, **When** miro el botón, **Then** «Descargar .zip» está desactivado y un texto indica que hay que marcar al menos un presupuesto.
6. **Given** que elijo «Seleccionar» y marco algo, **When** vuelvo a «Todo», **Then** la selección se ignora y se exporta todo.
7. **Given** la ventana abierta, **When** pulso «Cancelar», la tecla Esc o fuera de la ventana, **Then** se cierra sin descargar nada y sin cambiar nada.
8. **Given** la opción «Seleccionar», **When** leo la ventana, **Then** un texto me avisa de que esa copia no incluye el resto de mis datos y no sirve como copia de seguridad completa.

---

### User Story 2 - Que exportar no cambie nada y me diga qué incluye (Priority: P1)

Como autónomo, quiero tener la seguridad de que exportar no altera mis presupuestos y saber de antemano qué llevará el zip, para no perder ni estropear nada.

**Why this priority**: una copia que modifica los datos que copia (p. ej. marcando borradores como «Enviado») rompería la confianza en la app.

**Independent Test**: con 2 presupuestos descargados y 1 borrador, anotar estados y datos, exportar, y comprobar que todo sigue igual y que el borrador no tiene PDF en el zip pero sí aparece en el archivo de datos.

**Acceptance Scenarios**:

1. **Given** un presupuesto en «Borrador», **When** exporto, **Then** sigue en «Borrador», sus datos del emisor siguen sin fijar y no aparece su PDF en el zip.
2. **Given** el mismo borrador, **When** miro el archivo de datos del zip, **Then** el presupuesto está incluido con todas sus líneas.
3. **Given** que hay presupuestos aún sin descargar, **When** miro la opción «Todo» de la ventana, **Then** un texto me indica cuántos PDF llevará el zip y que los borradores solo irán en el archivo de datos.
4. **Given** cualquier exportación, **When** termina, **Then** la lista, los estados, la numeración y el perfil están exactamente como antes.
5. **Given** que la exportación falla, **When** ocurre, **Then** veo un mensaje claro en español y los datos siguen intactos.

---

### User Story 3 - Saber que está trabajando cuando son muchos (Priority: P2)

Como autónomo con muchos presupuestos, quiero ver que la app está preparando la copia, para no pensar que se ha bloqueado ni pulsar varias veces.

**Why this priority**: mejora la confianza con volúmenes altos, pero la exportación funciona sin ello.

**Independent Test**: con 50 presupuestos descargados, pulsar «Descargar .zip» en la ventana y comprobar que, mientras se prepara, el botón está desactivado y muestra «Preparando la copia…», y que la descarga empieza al terminar.

**Acceptance Scenarios**:

1. **Given** que acabo de pulsar «Descargar .zip», **When** la copia se está preparando, **Then** el botón queda desactivado con el texto «Preparando la copia…», la ventana no se puede lanzar otra vez y no puedo iniciar una segunda exportación.
2. **Given** que la descarga ha empezado, **When** termina la preparación, **Then** el botón vuelve a su estado normal y la ventana se cierra.
3. **Given** 200 presupuestos, **When** exporto, **Then** se descarga un único zip completo.

---

### Edge Cases

- **Sin presupuestos**: al pulsar «Exportar…», en lugar de la ventana de opciones se muestra un aviso claro («No hay presupuestos que exportar») y no se descarga ningún zip vacío.
- **Presupuestos, pero ninguno descargado todavía**: con «Todo» el zip se descarga con el archivo de datos y sin PDF, y el texto de la ventana avisa de ello antes de pulsar. La opción «Seleccionar» aparece desactivada, con el motivo («Aún no hay presupuestos descargados»).
- **Selección con muchos presupuestos**: la lista de selección admite desplazamiento dentro de la ventana y «Marcar todos» marca todos los de la lista, no solo los visibles.
- **Presupuesto que cambia mientras la ventana está abierta** (otra persona descarga un borrador): la selección se aplica sobre los presupuestos de la lista tal como se mostró; los demás no se incluyen.
- **Nombre de cliente con caracteres conflictivos** («Diseño/Web S.L.», con `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`): el nombre del PDF se limpia (esos caracteres se sustituyen o eliminan) y el zip se abre sin errores.
- **Nombre de cliente muy largo o que queda vacío tras la limpieza**: el nombre del PDF queda con una longitud razonable y, si no hay nombre utilizable, se usa el texto fijo «Sin cliente».
- **Clientes archivados**: sus presupuestos se exportan igual.
- **Presupuesto descargado cuyo cliente se anonimizó después**: la app ya no puede generar su PDF («El cliente de este presupuesto fue eliminado», 001 FR-023), así que tampoco hay PDF en el zip ni aparece en la lista de selección; con «Todo» sí va en el archivo de datos.
- **Dos clientes con el mismo nombre**: no hay conflicto, porque el número del presupuesto es único y va en el nombre.
- **Presupuesto creado o modificado mientras se prepara la copia**: la copia refleja un estado coherente de un único momento; no queda a medias.
- **Se pulsa dos veces**: la segunda pulsación se ignora mientras la primera se prepara.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-301**: La lista de presupuestos DEBE mostrar de forma visible un botón «Exportar…», disponible para cualquier cuenta con sesión iniciada. Al pulsarlo se abre una ventana modal previa; no se descarga nada hasta confirmar en ella con «Descargar .zip».
- **FR-301a**: La ventana DEBE ofrecer dos opciones: «Todo» (marcada por defecto) y «Seleccionar qué exportar». Con «Seleccionar», DEBE mostrar una lista con una casilla por presupuesto (número, cliente y estado), una opción «Marcar todos» y el recuento de marcados.
- **FR-301b**: La lista de selección DEBE ofrecer únicamente presupuestos ya descargados; los borradores NO aparecen. Sin ninguna casilla marcada, «Descargar .zip» DEBE estar desactivado con una indicación de que hay que marcar al menos un presupuesto.
- **FR-301c**: La ventana DEBE poder cerrarse con «Cancelar», con la tecla Esc o pulsando fuera, sin descargar ni cambiar nada. Debe ser accesible con teclado y lector de pantalla (foco dentro de la ventana mientras está abierta y devuelto al botón «Exportar…» al cerrarla) y usable desde 320 px de ancho.
- **FR-302**: Al confirmar, el sistema DEBE descargar **un único** archivo .zip, con la fecha del día de la exportación: `presupuestospro-copia-AAAA-MM-DD.zip` con «Todo» y `presupuestospro-seleccion-AAAA-MM-DD.zip` con «Seleccionar».
- **FR-303**: Con «Todo», el zip DEBE contener un PDF por cada presupuesto ya descargado (con su emisor fijado) y un único archivo de datos. Con «Seleccionar», DEBE contener un PDF por cada presupuesto marcado y un único archivo de datos. No DEBE contener nada más.
- **FR-304**: Cada PDF del zip DEBE ser el mismo documento que genera la app al descargar ese presupuesto (mismo contenido, aspecto, importes y datos del emisor fijados), con los importes cuadrando al céntimo.
- **FR-305**: La exportación DEBE ser de solo lectura: no DEBE cambiar el estado de ningún presupuesto, fijar datos del emisor, consumir numeración ni modificar ningún otro dato.
- **FR-306**: Con «Todo», el archivo de datos DEBE incluir todos los presupuestos (también los borradores, con sus líneas), clientes, el catálogo de servicios, el perfil del autónomo con su logo, los ajustes y los contadores de numeración, con el mismo contenido que la exportación actual. NO DEBE incluir cuentas de usuario ni nada relacionado con contraseñas o sesiones.
- **FR-306a**: Con «Seleccionar», el archivo de datos DEBE contener solo los presupuestos marcados, con sus líneas y los clientes a los que pertenecen (y el logo que muestran sus PDF), y NO el resto de presupuestos, el catálogo, los ajustes ni los contadores de numeración.
- **FR-306b**: Cuando se elige «Seleccionar», la ventana DEBE avisar, antes de descargar, de que esa copia es parcial y no sirve como copia de seguridad completa.
- **FR-307**: Cada PDF del zip DEBE llamarse «número - cliente.pdf», con el número tal como lo muestra la app (p. ej. `PRE-2026-001 - Estudio García.pdf`).
- **FR-308**: Los nombres de archivo DEBEN limpiarse de caracteres no válidos en nombres de archivo, y tener una longitud razonable, de modo que el zip se abra sin errores en los sistemas habituales; los nombres con tildes y «ñ» DEBEN conservarse.
- **FR-309**: Sin presupuestos, el sistema DEBE avisar con un mensaje claro de que no hay nada que exportar y NO DEBE descargar ningún zip.
- **FR-310**: En la ventana DEBE mostrarse cuántos PDF incluirá el zip con la opción elegida y, con «Todo», si hay presupuestos aún sin descargar, que estos solo irán en el archivo de datos. Si no hay ningún presupuesto descargado, «Seleccionar» DEBE aparecer desactivada con el motivo.
- **FR-311**: Mientras se prepara la copia, el botón «Descargar .zip» DEBE quedar desactivado y mostrar «Preparando la copia…», sin permitir una segunda exportación simultánea, y volver a su estado normal al empezar la descarga.
- **FR-312**: La copia DEBE reflejar los datos de un único instante coherente, aunque otra persona esté trabajando mientras se prepara.
- **FR-313**: Si la preparación falla, el sistema DEBE mostrar un mensaje claro en español de España y NO DEBE dejar datos a medias.
- **FR-314**: La exportación en archivo de datos suelto que existe hoy DEBE retirarse; el zip pasa a ser la única exportación de la app. Los textos, ayudas y documentación que la mencionen DEBEN actualizarse.
- **FR-315**: Todos los textos nuevos DEBEN estar en español de España y el botón, la ventana y los avisos DEBEN cumplir el sistema visual y los criterios de accesibilidad de la spec 003.

### Key Entities

- **Copia exportada**: el archivo .zip descargado. Contiene los PDF de los presupuestos ya descargados y un archivo de datos. No se guarda en la app ni deja rastro: cada exportación se genera en el momento.
- **PDF de presupuesto**: el documento que ya existe para cada presupuesto descargado; la copia incluye el mismo, sin variantes.
- **Archivo de datos**: con «Todo», la información completa del negocio (presupuestos con líneas, clientes, catálogo, perfil con logo, ajustes y contadores), pensada para poder restaurar la aplicación en el futuro. Con «Seleccionar», solo los presupuestos marcados con sus líneas y clientes. Nunca incluye cuentas ni contraseñas.
- **Selección**: el conjunto de presupuestos ya descargados que el autónomo marca en la ventana; existe solo mientras la ventana está abierta y no se guarda.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-301**: Con 3 presupuestos ya descargados, el autónomo obtiene su copia completa con **dos clics** («Exportar…» y «Descargar .zip») y un único archivo descargado.
- **SC-309**: Con 5 presupuestos descargados, el autónomo marca 2 y el zip contiene exactamente 2 PDF y un archivo de datos con exactamente esos 2 presupuestos; ningún borrador aparece en la lista de selección.
- **SC-310**: La ventana se puede abrir, recorrer, marcar, descargar y cerrar usando solo el teclado, y no hay desplazamiento horizontal a 320 px.
- **SC-302**: Al descomprimir, el 100 % de los PDF esperados está presente, con nombre «número - cliente», y el archivo de datos contiene el 100 % de los presupuestos (incluidos borradores).
- **SC-303**: Los PDF del zip coinciden en contenido e importes con los de la descarga individual en el 100 % de los casos; el presupuesto de control muestra un total de 3.604,00 €.
- **SC-304**: Tras exportar, el 100 % de los datos y estados queda idéntico a antes (ningún borrador pasa a «Enviado», ningún emisor se fija, la numeración no avanza).
- **SC-305**: Con 0 presupuestos, ninguna exportación genera un zip y el autónomo ve un aviso claro.
- **SC-306**: Un cliente con nombre «Diseño/Web S.L.» produce un PDF cuyo zip se abre sin errores con el descompresor del sistema (Windows, macOS).
- **SC-307**: Con 50 presupuestos, durante toda la preparación el autónomo ve que la app está trabajando, y con 200 la descarga acaba completa.
- **SC-308**: El 100 % de los autónomos de una prueba con 3 personas, sin ayuda, consigue exportar y descomprimir su copia en menos de 1 minuto.

## Assumptions

- Un presupuesto entra en los PDF del zip si ya está descargado **y** la app todavía puede generar su PDF con las mismas reglas que la descarga individual (p. ej. no si su cliente fue anonimizado). «Descargado» significa que el presupuesto tiene sus datos de emisor fijados. No se deduce de la etiqueta de estado: un presupuesto «Caducado» puede haberse descargado o no (la 003 da prioridad a «Caducado»), y solo entra en los PDF si se descargó.
- Si hay presupuestos pero ninguno descargado, «Todo» genera el zip igualmente (el archivo de datos tiene valor por sí solo) y solo se avisa de que no hay PDF; «Seleccionar» queda desactivada porque no hay nada que marcar.
- Los borradores solo salen con «Todo»: por decisión de la sesión de aclaraciones, la selección no los ofrece, y por tanto una selección nunca los incluye ni en PDF ni en el archivo de datos.
- El archivo de datos de una selección conserva el mismo formato que el completo, pero con menos contenido; su restauración no es objetivo de esta spec.
- La fecha del nombre del zip es la del día en España al pulsar el botón (la misma que usa la app en el resto de pantallas).
- El archivo de datos conserva el nombre y el formato de la exportación actual dentro del zip, para poder restaurarlo en la futura spec de importación.
- Cualquier cuenta con sesión puede exportar, igual que hoy con la exportación actual; el archivo no incluye cuentas ni contraseñas, por lo que puede viajar sin ese riesgo (FR-036 de la 001).
- No hay límite de presupuestos; el volumen previsto es de cientos.

## Fuera de alcance

- **Importar** la copia (restaurar los datos): será otra spec.
- Exportar a Excel o CSV con formato contable.
- Copias automáticas o programadas: solo bajo demanda.
- Enviar el zip por correo o subirlo a ninguna nube.
- Generar PDF para los borradores dentro del zip (decisión de la sesión de aclaraciones; si se quiere, irá a [`propuestas.md`](../propuestas.md)).
- Filtros para elegir presupuestos (por año, estado o cliente): la selección es manual, uno a uno, con «Marcar todos».
- Elegir qué datos adicionales (catálogo, perfil, clientes) entran en el archivo de datos: dependen solo de «Todo» o «Seleccionar».
- Barra de progreso con porcentaje.
