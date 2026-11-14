# Feature Specification: PresupuestosPro v1

**Feature Branch**: `001-presupuestos-pro`

**Created**: 2026-11-14

**Status**: Draft

**Input**: User description: "Especificación: PresupuestosPro v1 — Herramienta para que un autónomo en España cree presupuestos con su imagen corporativa, con IVA e IRPF calculados automáticamente, y los descargue en PDF para enviarlos él mismo por email." (Descripción completa con objetivo, usuarios, HU1–HU7, RF, RN1–RN11, tabla de tratamiento por tipo de cliente, CA1–CA15, CL1–CL15 y fuera de alcance, aportada por el usuario el 2026-11-14.)

## Contexto

- **Problema**: hoy cada presupuesto se hace a mano: el autónomo repite sus datos, busca precios y calcula impuestos, con riesgo de error.
- **Resultado esperado**: crear un presupuesto correcto en menos de 5 minutos, sin errores de cálculo.
- **Contexto legal**: un presupuesto no es una factura y no está sujeto al Reglamento de facturación. Aun así, sus importes deben coincidir con los de la factura posterior, por lo que aplica las mismas reglas de IVA e IRPF.
- **Usuarios**:
  - **Titular (autónomo)** — uso principal: configura perfil, ajustes fiscales, catálogo y clientes; crea y descarga presupuestos; da de alta y de baja las cuentas de sus asistentes.
  - **Asistente o encargado** — uso ocasional: con su propia cuenta, crea y descarga presupuestos en nombre del titular, con los mismos datos (un único emisor, un solo NIF).
  - **Administrador técnico** — no usa la aplicación en el día a día: instala el servidor, crea la cuenta del titular, vigila las copias de seguridad y restaura datos o contraseñas cuando hace falta. Puede ser el propio titular si tiene conocimientos técnicos.
  - **Cliente** — no usa la aplicación; recibe el PDF por email. Puede ser empresa, autónomo o particular.
- **Instalación**: cada autónomo tiene su propia instalación (servidor y datos propios). Los datos de distintos autónomos nunca comparten servidor.
- **Flujo principal**: (0) iniciar sesión; (1) configurar perfil, ajustes fiscales y catálogo una sola vez; (2) elegir un cliente de la lista o darlo de alta; (3) añadir líneas desde el catálogo o escritas a mano; (4) revisar base, IVA, retención y total; (5) descargar el PDF y enviarlo por email fuera de la herramienta.

## Clarifications

### Session 2026-11-14

- Q: ¿Cuándo se congelan los datos de emisor y cliente en un presupuesto (RN9)? → A: Mientras el presupuesto no se ha descargado nunca, muestra los datos actuales del perfil y del cliente; se congelan en la primera descarga del PDF. Las líneas siempre son copia desde que se añaden. (Para el cliente, sustituido por una aclaración posterior: sus datos son siempre los actuales.)
- Q: ¿Se puede editar un presupuesto después de descargarlo (P5)? → A: Sí, libremente y con el mismo número; volver a descargar genera el PDF actualizado. Sin estados de solo lectura ni versiones.
- Q: ¿Cuándo se asigna el número y con qué año? → A: Al crear el presupuesto, con el año de la fecha de creación.
- Q: ¿Se pueden borrar presupuestos? → A: Sí, cualquiera, con confirmación. El número no se reutiliza.
- Q: ¿El tipo de IVA se puede cambiar por presupuesto (P4)? → A: Sí. El tipo por defecto viene de Ajustes (21 %) y en cada presupuesto se puede elegir 21 %, 10 %, 4 % o 0 %. El tipo de cliente decide si se aplica IVA o no.
- Q: ¿Cómo se trata Canarias, Ceuta y Melilla? → A: Entra en v1 con la regla dada (sin IVA; retención si el emisor la aplica). La mención es un texto que el usuario edita en Ajustes, vacío por defecto.
- Q: ¿El tipo de cliente se elige o se deduce? → A: Se eligen categoría (Empresa/autónomo o Particular) y territorio (Península y Baleares, Canarias/Ceuta/Melilla, Otro país UE, Fuera de la UE), más la casilla «NIF-IVA verificado» si es UE. El tratamiento se deduce. «Particular» fuera de España no es seleccionable.
- Q: ¿Cómo se comunica el 7 % al cliente (RN4)? → A: Basta con que el PDF muestre el porcentaje en la fila de retención («Retención IRPF (−7 %)»). Sin mención adicional.
- Q: ¿Exportar/importar (RF15) entra en v1? → A: Sí: exportar todos los datos a un archivo e importarlos en otro equipo; la importación sustituye los datos existentes tras confirmar. (Sustituido por la sesión de cambio de almacenamiento: solo queda Exportar.)
- Q: ¿Qué necesita el historial (HU7)? → A: Lista ordenada por fecha (número, cliente, fecha de emisión, total) con búsqueda por número o nombre de cliente.
- Q: ¿En qué dispositivos debe poder usarse la herramienta en v1? → A: Aplicación web con diseño adaptable (responsive): ordenador, tableta y móvil.
- Q: Si un presupuesto ya descargado tiene un dato del cliente mal y lo corrijo en la ficha del cliente, ¿cómo llega la corrección al presupuesto? → A: Los datos del cliente no se congelan: el presupuesto muestra siempre los datos actuales del cliente seleccionado y cada descarga los usa. Perfil del emisor y ajustes de retención siguen congelados desde la primera descarga.
- Q: ¿Debe la herramienta avisar del riesgo de perder los datos guardados solo en el navegador? → A: Sí, con un aviso fijo y discreto («Tus datos se guardan solo en este navegador. Exporta una copia de vez en cuando») con acceso directo a Exportar. (Sustituido por la sesión de cambio de almacenamiento: el aviso se elimina.)
- Q: ¿Qué debe pasar si se abre la herramienta en varias pestañas del mismo navegador a la vez? → A: Se permiten varias pestañas activas; la numeración nunca se duplica y, si dos pestañas editan el mismo elemento, prevalece el último guardado. (Ampliado en la sesión de cambio de almacenamiento a varios equipos y personas.)

### Session 2026-11-14 — cambio de almacenamiento

Motivo: los datos no deben perderse si se borran los datos del navegador o se daña el equipo. Se pasa de guardar los datos solo en el navegador a guardarlos en un servidor propio del autónomo.

- Q: ¿Dónde se guardan los datos? → A: En un servidor propio de cada autónomo (una instalación por autónomo), no en el navegador. Borrar el navegador o cambiar de equipo no hace perder datos.
- Q: ¿Quién usa cada instalación? → A: Un único autónomo (un emisor, un NIF). Sin registro público ni varios autónomos en la misma instalación.
- Q: ¿Cómo entra el asistente? → A: Con su propia cuenta (email y contraseña), creada por el titular. Ve los mismos datos y puede hacer lo mismo que el titular, salvo gestionar cuentas. El titular puede darle de baja sin cambiar su propia contraseña.
- Q: ¿Qué pasa con Exportar/Importar y el aviso de «solo en este navegador»? → A: El servidor hace una copia de seguridad automática diaria, conservada 30 días y guardada fuera del servidor. En la app solo queda Exportar (descargar todos los datos). Se eliminan Importar y el aviso fijo.
- Q: ¿Cómo se crea la primera cuenta? → A: La crea el administrador técnico durante la instalación; la app no tiene alta pública de cuentas.
- Q: ¿Qué pasa si alguien olvida su contraseña? → A: Como la herramienta no envía emails, el titular restablece la contraseña de un asistente desde la app, y el administrador técnico restablece la del titular.
- Q: Si un cliente particular pide que se borren sus datos (derecho de supresión del RGPD), ¿qué debe permitir la herramienta? → A: Un botón «Anonimizar cliente», con confirmación, que borra nombre, NIF, dirección, país y email y los sustituye por «Cliente eliminado». Sus presupuestos se conservan con número e importes, pero ya no se pueden descargar en PDF.
- Q: ¿Quién debe poder descargar el archivo con todos los datos (Exportar)? → A: Titular y asistentes, sin diferencia de permisos.
- Q: Cuando un presupuesto ya se ha descargado, ¿debe conservar el texto de mención de Canarias, Ceuta y Melilla con el que salió? → A: No. Cada descarga usa el texto actual de Ajustes; no se congela.
- Q: Mientras un presupuesto todavía no tiene cliente elegido, ¿qué totales debe mostrar la pantalla? → A: Totales provisionales como si fuera Empresa/autónomo de Península y Baleares (IVA del presupuesto y retención si el emisor la aplica), con el aviso «Totales provisionales: elige un cliente».
- Q: ¿Debe la herramienta guardar un registro de accesos que el titular pueda consultar? → A: No. Sin registro de accesos ni de cambios en v1.

## User Scenarios & Testing *(mandatory)*

Datos base usados en los escenarios salvo que se indique otra cosa: emisor con retención activada al 15 %, IVA 21 %, líneas 10 × 45,00 € y 1 × 300,00 €.

### User Story 1 - Crear un presupuesto con cálculo correcto de impuestos (Priority: P1)

Como autónomo, quiero crear un presupuesto eligiendo un cliente, añadiendo líneas (desde el catálogo o a mano, con cantidad y precio editables) y ver en pantalla la base imponible, el IVA, la retención de IRPF cuando corresponda y el total, para no cometer errores de cálculo. (HU4, HU5)

**Why this priority**: es el núcleo del producto. Sin cálculo correcto no hay valor, aunque el resto exista.

**Independent Test**: con un cliente y dos líneas, comprobar que los totales en pantalla cuadran al céntimo con los ejemplos de esta spec para cada tipo de cliente.

**Acceptance Scenarios**:

1. **Given** cliente Empresa/autónomo en Península y Baleares y las líneas base, **When** reviso los totales, **Then** veo base 750,00 €; IVA 21 % 157,50 €; retención 15 % −112,50 €; total 795,00 €. (CA6)
2. **Given** cliente Particular en España y las líneas base, **When** reviso los totales, **Then** el total es 907,50 € y no aparece fila de retención. (CA7, CL2)
3. **Given** cliente Empresa/autónomo de otro país UE con «NIF-IVA verificado» y las líneas base, **When** reviso los totales, **Then** IVA 0,00 €, sin fila de retención, total 750,00 € y se muestra la mención «Inversión del sujeto pasivo». (CA8)
4. **Given** el presupuesto del escenario 1, **When** cambio la cantidad de 10 a 12, **Then** sin recargar veo base 840,00 €; IVA 176,40 €; retención −126,00 €; total 890,40 €. (CA9)
5. **Given** «Hora de desarrollo» a 45,00 € en el catálogo, **When** la añado al presupuesto y pongo cantidad 10, **Then** la línea muestra 450,00 € y el catálogo sigue a 45,00 €. (CA4)
6. **Given** un presupuesto abierto, **When** añado una línea manual «Licencia anual», 1 × 120,00 €, **Then** la línea muestra 120,00 € y no se añade al catálogo. (CA5)
7. **Given** líneas «Diseño de página web» 1.500,00 € y «Sesión de fotos de producto» 500,00 € con cliente Empresa en España, **When** reviso los totales, **Then** base 2.000,00 €; IVA 21 % 420,00 €; retención −15 % −300,00 €; total 2.120,00 €. Con retención al 7 % el total es 2.280,00 €; con cliente particular, 2.420,00 €.
8. **Given** una línea con cantidad 0, **When** intento confirmarla, **Then** se muestra un error y no se acepta. (RN10)
9. **Given** un presupuesto con varias líneas, **When** reordeno o elimino una línea, **Then** el orden se actualiza y los totales se recalculan al instante. (RF8)
10. **Given** cliente Empresa fuera de la UE y las líneas base, **When** reviso los totales, **Then** IVA 0,00 €, sin retención, total 750,00 € y mención «Operación no sujeta — Art. 69.Uno.1.º Ley 37/1992». (CL3)
11. **Given** un presupuesto sin cliente con las líneas base, **When** reviso los totales, **Then** veo base 750,00 €; IVA 157,50 €; retención −112,50 €; total 795,00 € y el aviso «Totales provisionales: elige un cliente». (FR-044)

---

### User Story 2 - Descargar el presupuesto en PDF con imagen corporativa (Priority: P1)

Como autónomo, quiero descargar el presupuesto en PDF con mi logo y mis datos, para enviárselo yo al cliente por email. (HU6)

**Why this priority**: el PDF es el entregable que llega al cliente. Junto con la Historia 1 forma el producto mínimo.

**Independent Test**: descargar un presupuesto completo y comparar el PDF con la pantalla: cabecera, cliente, número, fechas, líneas, desglose, notas, mención y nombre de archivo.

**Acceptance Scenarios**:

1. **Given** perfil completo con logo, **When** descargo cualquier presupuesto, **Then** el PDF muestra en la cabecera logo, nombre o razón social, NIF, dirección, email y teléfono. (CA1)
2. **Given** perfil sin NIF, **When** intento descargar un PDF, **Then** no se genera y se me pide completar el perfil indicando el campo que falta. (CA2)
3. **Given** emisión el 13/11/2026 y validez de 30 días, **When** descargo el PDF, **Then** muestra «Válido hasta el 13/12/2026». (CA11)
4. **Given** un presupuesto completo PRE-2026-015 para «Acme SL», **When** descargo el PDF, **Then** el archivo se llama `PRE-2026-015_Acme-SL.pdf` y sus importes coinciden con la pantalla al céntimo. (CA12)
5. **Given** un presupuesto sin cliente o sin líneas, **When** intento descargar el PDF, **Then** no se genera y se indica qué falta. (CA13)
6. **Given** un cliente Empresa en España sin NIF, **When** intento descargar el PDF, **Then** no se genera y se pide completar el NIF del cliente; el presupuesto sí se puede guardar. (CL13)
7. **Given** un presupuesto con muchas líneas o descripciones largas, **When** descargo el PDF, **Then** el PDF ocupa varias páginas, repite la cabecera de la tabla de líneas en cada página y muestra los totales en la última. (CL8)
8. **Given** un presupuesto con notas y condiciones, **When** descargo el PDF, **Then** las notas aparecen en el PDF. (RF10)

---

### User Story 3 - Configurar perfil del emisor y ajustes fiscales (Priority: P2)

Como autónomo, quiero configurar una vez mi nombre o razón social, NIF, dirección fiscal, email, teléfono y logo, y mis ajustes fiscales por defecto, para que los presupuestos salgan con mi marca y los impuestos correctos sin reescribirlos. (HU1)

**Why this priority**: es imprescindible para descargar el PDF, pero se configura una sola vez.

**Independent Test**: rellenar el perfil y los ajustes, cerrar y reabrir la herramienta y comprobar que se conservan y se usan en un presupuesto nuevo.

**Acceptance Scenarios**:

1. **Given** el perfil vacío, **When** intento guardarlo sin nombre, NIF, dirección o email, **Then** se indica qué campos obligatorios faltan.
2. **Given** un logo PNG, JPG o SVG de hasta 2 MB, **When** lo subo, **Then** se acepta y se muestra una vista previa.
3. **Given** un logo de más de 2 MB o en otro formato, **When** lo subo, **Then** se rechaza con un mensaje claro que indica formatos y tamaño permitidos. (CL9)
4. **Given** ajustes con validez 30 días e IVA 21 %, **When** creo un presupuesto nuevo, **Then** la fecha de emisión es hoy, la de validez es hoy + 30 días y el IVA es 21 %.
5. **Given** un presupuesto ya descargado con la dirección antigua, **When** cambio la dirección en el perfil, **Then** ese presupuesto conserva la dirección antigua. (CL12)

---

### User Story 4 - Gestionar clientes, también desde el presupuesto (Priority: P2)

Como autónomo, quiero elegir el cliente de una lista o darlo de alta sin salir del presupuesto, indicando su tipo, para dirigirle el presupuesto y que se apliquen los impuestos correctos. (HU3)

**Why this priority**: el tipo de cliente determina IVA, retención y mención; sin cliente no se puede descargar.

**Independent Test**: dar de alta «Acme SL» desde un presupuesto con líneas ya escritas y comprobar que queda seleccionado, que las líneas siguen y que aparece en la lista de clientes.

**Acceptance Scenarios**:

1. **Given** el cliente «Acme SL» no existe y tengo líneas escritas, **When** lo doy de alta desde el presupuesto, **Then** queda seleccionado, mis líneas siguen ahí y aparece en la lista de clientes. (CA3)
2. **Given** varios clientes, **When** escribo parte del nombre o NIF en el buscador del presupuesto, **Then** la lista se filtra y puedo seleccionar uno. (RF5)
3. **Given** un cliente con categoría «Particular», **When** elijo el territorio, **Then** solo puedo seleccionar territorios de España. (P3)
4. **Given** un cliente usado en presupuestos, **When** lo archivo, **Then** desaparece de las listas de selección y los presupuestos que lo usaban lo conservan. (CL11)
5. **Given** un cliente Empresa de otro país UE sin marcar «NIF-IVA verificado», **When** lo uso en un presupuesto, **Then** se aplica IVA 21 %, sin retención ni mención. (CL1)
6. **Given** un cliente usado en presupuestos, **When** pulso «Anonimizar cliente» y confirmo, **Then** su nombre pasa a «Cliente eliminado», se borran NIF, dirección, país y email, desaparece de las listas de selección, sus presupuestos siguen en el historial con número e importes y no se pueden descargar en PDF. (FR-043)

---

### User Story 5 - Mantener el catálogo de servicios (Priority: P3)

Como autónomo, quiero mantener una lista de mis servicios con su precio habitual, para añadirlos a un presupuesto sin buscar precios. (HU2)

**Why this priority**: ahorra tiempo, pero se puede crear un presupuesto solo con líneas manuales.

**Independent Test**: crear un servicio, añadirlo a un presupuesto, cambiar su precio en el catálogo y comprobar que el presupuesto no cambia.

**Acceptance Scenarios**:

1. **Given** el catálogo vacío, **When** creo «Hora de desarrollo», unidad hora, 45,00 € sin IVA, **Then** aparece en el catálogo y en el selector de líneas.
2. **Given** PRE-2026-010 con una línea de «Hora de desarrollo» a 45,00 €, **When** cambio ese servicio a 50,00 € en el catálogo, **Then** PRE-2026-010 sigue mostrando 45,00 €. (CA15)
3. **Given** un servicio usado en presupuestos, **When** lo archivo, **Then** desaparece del selector y los presupuestos lo conservan. (CL11)

---

### User Story 6 - Consultar y reabrir presupuestos anteriores (Priority: P3)

Como autónomo, quiero consultar y reabrir presupuestos anteriores, para revisarlos o corregirlos. (HU7)

**Why this priority**: aporta valor tras el uso continuado; no bloquea crear el primer presupuesto.

**Independent Test**: guardar varios presupuestos, cerrar y reabrir la herramienta, buscarlos por número y cliente, reabrir uno y comprobar sus importes.

**Acceptance Scenarios**:

1. **Given** perfil, catálogo, clientes y presupuestos guardados, **When** cierro y vuelvo a abrir la herramienta, **Then** todo sigue ahí con los mismos importes. (CA14)
2. **Given** varios presupuestos, **When** abro el historial, **Then** veo una lista ordenada por fecha de emisión (más reciente primero) con número, cliente, fecha y total.
3. **Given** el historial, **When** busco «015» o «Acme», **Then** la lista muestra solo los presupuestos que coinciden.
4. **Given** un presupuesto ya descargado, **When** lo reabro y cambio una línea, **Then** conserva su número y la siguiente descarga refleja el cambio.
5. **Given** un presupuesto, **When** lo borro y confirmo, **Then** desaparece del historial y su número no se vuelve a asignar.

---

### User Story 7 - Numeración automática (Priority: P2)

Como autónomo, quiero que cada presupuesto reciba un número automático PRE-AAAA-NNN correlativo por año, para no llevar la cuenta a mano. (RF6)

**Why this priority**: el número identifica el presupuesto y aparece en el PDF y en el nombre del archivo.

**Independent Test**: crear presupuestos consecutivos y comprobar la secuencia, incluido el cambio de año.

**Acceptance Scenarios**:

1. **Given** el último presupuesto es PRE-2026-014, **When** creo dos más, **Then** reciben PRE-2026-015 y PRE-2026-016. (CA10)
2. **Given** el último presupuesto de 2026 es PRE-2026-120, **When** creo el primero de 2027, **Then** recibe PRE-2027-001. (CL10)
3. **Given** PRE-2026-016 es el último y lo borro, **When** creo uno nuevo, **Then** recibe PRE-2026-017.
4. **Given** la herramienta abierta en dos pestañas o en dos equipos y el último número PRE-2026-017, **When** creo un presupuesto en cada una a la vez, **Then** reciben PRE-2026-018 y PRE-2026-019 (sin duplicados). (FR-033)

---

### User Story 8 - Acceso con cuenta propia (Priority: P1)

Como titular, quiero que solo las personas a las que yo dé acceso puedan ver y modificar mis datos y los de mis clientes, cada una con su propia cuenta, para que nadie más en internet pueda leerlos. (FR-034 a FR-040)

**Why this priority**: los datos están en un servidor accesible desde internet; sin control de acceso, cualquiera con la dirección podría leer los datos de los clientes. Es imprescindible antes de usar la herramienta con datos reales.

**Independent Test**: abrir la herramienta en una ventana privada y comprobar que solo aparece la pantalla de inicio de sesión; entrar como titular, crear un asistente, entrar como asistente y ver los mismos datos; dar de baja al asistente y comprobar que ya no puede entrar.

**Acceptance Scenarios**:

1. **Given** no he iniciado sesión, **When** abro la herramienta, **Then** solo veo la pantalla de inicio de sesión y ningún dato. (FR-034)
2. **Given** el email y la contraseña correctos, **When** inicio sesión, **Then** accedo a la herramienta con todos los datos del autónomo.
3. **Given** una contraseña incorrecta, **When** intento entrar, **Then** veo «Email o contraseña incorrectos», sin indicar cuál de los dos falla.
4. **Given** 5 intentos fallidos seguidos con el mismo email, **When** lo intento de nuevo antes de 15 minutos, **Then** se rechaza aunque la contraseña sea correcta y se indica que espere. (FR-038)
5. **Given** soy el titular, **When** doy de alta a un asistente con nombre, email y contraseña inicial, **Then** el asistente puede entrar y ve los mismos datos. (FR-035)
6. **Given** un asistente dado de alta, **When** el titular le da de baja, **Then** el asistente no puede volver a entrar y, si tenía la sesión abierta, la pierde en su siguiente acción. Los presupuestos que creó se conservan. (FR-035)
7. **Given** soy asistente, **When** busco la gestión de cuentas, **Then** no tengo acceso a ella. (FR-035)
8. **Given** una sesión abierta, **When** pulso «Cerrar sesión», **Then** vuelvo a la pantalla de inicio de sesión y, al volver atrás en el navegador, no veo datos. (FR-037)
9. **Given** una sesión sin actividad durante 8 horas, **When** intento hacer algo, **Then** se me pide iniciar sesión de nuevo. (FR-037)
10. **Given** soy el titular y un asistente olvidó su contraseña, **When** le asigno una nueva desde la gestión de cuentas, **Then** el asistente entra con la nueva y la anterior deja de funcionar. (FR-039)
11. **Given** cualquier usuario con sesión, **When** cambio mi contraseña indicando la actual y una nueva de al menos 10 caracteres, **Then** la nueva funciona y la anterior no. (FR-036, FR-039)

---

### User Story 9 - Datos a salvo y exportación (Priority: P2)

Como titular, quiero que mis datos no se pierdan si borro el navegador, cambio de equipo o se estropea el ordenador, y poder descargar una copia completa cuando quiera. (FR-027, FR-029, FR-041)

**Why this priority**: es el motivo del cambio a servidor; perder el historial de presupuestos y clientes obligaría a rehacerlo todo.

**Independent Test**: crear datos, borrar los datos del navegador (o entrar desde otro equipo) e iniciar sesión: todo sigue igual. Exportar y comprobar que el archivo contiene todo.

**Acceptance Scenarios**:

1. **Given** datos guardados, **When** borro los datos del navegador y vuelvo a iniciar sesión, **Then** perfil, ajustes, catálogo, clientes, presupuestos y numeración siguen igual. (SC-004)
2. **Given** datos guardados desde un equipo, **When** inicio sesión desde otro equipo o desde el móvil, **Then** veo los mismos datos. (CL14)
3. **Given** datos guardados, **When** exporto, **Then** obtengo un único archivo con todos los datos, incluido el logo y la numeración. (FR-029)
4. **Given** el servidor en funcionamiento durante un día, **When** el administrador técnico descarga del almacenamiento externo la copia de ese día y la restaura siguiendo los pasos escritos, **Then** la herramienta muestra los datos tal como estaban al hacer la copia. (FR-041, FR-042; lo comprueba el administrador técnico)
5. **Given** un presupuesto creado después de la última copia, **When** el administrador técnico restaura esa copia, **Then** la herramienta ya no muestra ese presupuesto y el resto de los datos está intacto: se pierde como máximo un día de cambios. (SC-011; lo comprueba el administrador técnico)

---

### Edge Cases

- **CL1** Cliente UE que dice ser empresa pero sin «NIF-IVA verificado»: se trata como Empresa UE sin NIF-IVA válido (IVA 21 %, sin retención, sin mención). La herramienta no consulta VIES.
- **CL2** Cliente particular en España con retención activada en el perfil: sin retención.
- **CL3** Cliente empresa fuera de la UE: sin IVA ni retención, con mención de no sujeción.
- **CL4** Cliente empresa/autónomo en Canarias, Ceuta o Melilla: sin IVA; retención si el emisor la aplica; mención = texto configurado en Ajustes (si está vacío, no se muestra mención).
- **CL5** Servicio exento o con tipo reducido: un único tipo de IVA por presupuesto (21 %, 10 %, 4 % o 0 %).
- **CL6** Línea a 0,00 € (cortesía): permitida; aparece en las líneas y no altera totales.
- **CL7** Cantidad decimal (1,5 h): permitida hasta 2 decimales; 1,5 × 45,00 € = 67,50 €.
- **CL8** Muchas líneas o descripciones largas: el PDF pagina, repite la cabecera de líneas y pone los totales en la última página.
- **CL9** Logo de más de 2 MB o formato no soportado: se rechaza con mensaje claro.
- **CL10** Primer presupuesto del año: la numeración reinicia en PRE-AAAA-001.
- **CL11** Borrar un cliente o servicio: no se borra, se archiva; sale de las listas y los presupuestos lo conservan. Si un cliente ejerce su derecho de supresión, se anonimiza (FR-043).
- Cliente anonimizado: la anonimización no se puede deshacer; no se puede editar ni volver a seleccionar; sus presupuestos muestran «Cliente eliminado», mantienen el tratamiento fiscal con el que se calcularon (categoría y territorio se conservan) y la descarga del PDF queda bloqueada indicando el motivo.
- **CL12** Cambio de dirección en el perfil: los presupuestos ya descargados conservan los datos antiguos; los nunca descargados muestran los nuevos.
- Cambio de datos de un cliente (dirección, NIF, categoría o territorio) usado en presupuestos ya descargados: esos presupuestos muestran los datos nuevos, recalculan IVA, retención y mención si cambia el tratamiento, y la siguiente descarga los refleja.
- **CL13** Cliente empresa española sin NIF: se puede guardar el presupuesto, pero no descargar el PDF hasta completar el NIF.
- **CL14** El asistente usa otro equipo: inicia sesión con su cuenta y ve los mismos datos.
- **CL15** Vence el periodo del 7 %: el usuario cambia el tipo en Ajustes; los presupuestos ya descargados no cambian.
- Cantidad o precio con más de 2 decimales, precio negativo o cantidad ≤ 0: se rechaza con mensaje.
- Fecha de validez editada a mano anterior a la fecha de emisión: se rechaza con mensaje.
- Nombre de cliente con tildes, «ñ» o símbolos: el nombre de archivo los sustituye por su equivalente sin acento o los elimina, y cambia espacios por guiones (p. ej., «Peña & Cía» → `Pena-Cia`).
- Presupuesto creado y abandonado vacío: conserva su número; puede borrarse, y el número no se reutiliza.
- Cambio de tipo de cliente o de cliente seleccionado: IVA, retención y mención se recalculan al instante.
- Mismo presupuesto (u otro elemento) editado a la vez en dos pestañas, equipos o por dos personas: prevalece el último guardado; los números nunca se duplican (FR-033).
- Sin conexión a internet o servidor no disponible: la herramienta indica que no puede guardar y no da por guardado ningún cambio que no haya llegado al servidor.
- Un asistente dado de baja con la sesión abierta: su siguiente acción se rechaza y vuelve a la pantalla de inicio de sesión.
- El titular no puede darse de baja a sí mismo; siempre existe exactamente una cuenta de titular.
- Email de cuenta repetido al dar de alta un asistente: se rechaza con mensaje.

## Requirements *(mandatory)*

### Functional Requirements

**Perfil y ajustes**

- **FR-001 (RF1)**: El sistema DEBE permitir guardar y editar el perfil del emisor: nombre o razón social, NIF, dirección fiscal, email, teléfono y logo. Son obligatorios nombre, NIF, dirección y email.
- **FR-002 (RF1, CL9)**: El sistema DEBE aceptar logos PNG, JPG o SVG de hasta 2 MB y rechazar otros con un mensaje que indique formatos y tamaño permitidos.
- **FR-003 (RF2)**: El sistema DEBE permitir configurar ajustes fiscales por defecto: tipo de IVA (21 % por defecto; 21, 10, 4 o 0 %), si se aplica retención de IRPF (sí/no), tipo de retención (15 % o 7 %), días de validez (30 por defecto) y texto de mención para clientes de Canarias, Ceuta y Melilla (vacío por defecto).

**Catálogo**

- **FR-004 (RF3)**: El sistema DEBE permitir crear, editar y archivar servicios con nombre, descripción, unidad (hora, día, proyecto, unidad) y precio unitario sin IVA.
- **FR-005 (CL11)**: Los servicios archivados NO DEBEN aparecer en el selector de líneas; los presupuestos que los usan los conservan sin cambios.

**Clientes**

- **FR-006 (RF4)**: El sistema DEBE permitir crear, editar y archivar clientes con nombre o razón social, NIF/NIE o NIF-IVA, dirección, país, email, categoría (Empresa/autónomo o Particular) y territorio (Península y Baleares; Canarias, Ceuta o Melilla; Otro país UE; Fuera de la UE). Para territorio «Otro país UE» DEBE ofrecer la casilla «NIF-IVA verificado».
- **FR-007 (P3)**: El sistema NO DEBE permitir combinar la categoría Particular con un territorio fuera de España.
- **FR-008 (RF5)**: Desde el presupuesto, el usuario DEBE poder buscar un cliente por nombre o NIF y seleccionarlo, o darlo de alta sin perder lo ya escrito; el cliente nuevo queda seleccionado y aparece en la lista de clientes.
- **FR-009 (CL11)**: Los clientes archivados NO DEBEN aparecer en las listas de selección; los presupuestos que los usan los conservan.
- **FR-043 (RGPD)**: El usuario DEBE poder anonimizar un cliente, tras confirmación y de forma irreversible: se borran nombre, NIF, dirección, país y email, y el nombre pasa a «Cliente eliminado». Se conservan categoría y territorio para que los importes de sus presupuestos no cambien. El cliente anonimizado NO DEBE aparecer en listas de selección ni poder editarse, y sus presupuestos NO DEBEN poder descargarse en PDF.

**Presupuesto**

- **FR-010 (RF6, RN7)**: Al crear un presupuesto, el sistema DEBE asignarle un número PRE-AAAA-NNN, donde AAAA es el año de creación y NNN un correlativo de 3 dígitos por año que empieza en 001 cada año, sin duplicados y sin reutilizar números de presupuestos borrados.
- **FR-011 (RF7, RN8)**: El presupuesto DEBE tener fecha de emisión (hoy por defecto) y fecha de validez (emisión + días de validez de Ajustes), ambas editables. Si se cambia la emisión y la validez no se ha editado a mano, la validez se recalcula. La validez no puede ser anterior a la emisión.
- **FR-012 (RF8)**: El usuario DEBE poder añadir, editar, reordenar y eliminar líneas. Una línea del catálogo precarga descripción, unidad y precio (editables) y es una copia independiente del servicio. Una línea manual tiene descripción, cantidad, precio y unidad opcional, y no se añade al catálogo. Cada línea muestra descripción, cantidad, precio unitario e importe.
- **FR-013 (RN10)**: El sistema DEBE validar cantidad > 0 y precio ≥ 0, ambos con un máximo de 2 decimales, mostrando un mensaje si no se cumple.
- **FR-014 (P4)**: Cada presupuesto DEBE tener un único tipo de IVA, inicializado desde Ajustes al crearlo y editable entre 21, 10, 4 y 0 %.
- **FR-015 (RF9)**: El sistema DEBE recalcular base, IVA, retención y total en pantalla tras cada cambio, sin recargar, según RN1–RN6.
- **FR-044**: Mientras el presupuesto no tenga cliente seleccionado, DEBE mostrar totales provisionales calculados como Empresa/autónomo de Península y Baleares (IVA del presupuesto y retención si el emisor la aplica), sin mención, junto al aviso «Totales provisionales: elige un cliente».
- **FR-016 (RF10)**: El presupuesto DEBE tener un campo opcional de notas y condiciones (forma de pago, plazos de entrega).
- **FR-017 (RF11, P5)**: El presupuesto DEBE guardarse automáticamente y poder seguir editándose antes y después de descargarlo, conservando su número.
- **FR-018 (RN9)**: Mientras un presupuesto no se haya descargado nunca, DEBE mostrar los datos actuales del perfil y de los ajustes de retención. En la primera descarga DEBE guardar una copia de esos datos, que ya no cambia aunque se modifiquen perfil o ajustes. El texto de mención para Canarias, Ceuta y Melilla NO se congela: cada descarga usa el texto actual de Ajustes. Los datos del cliente NO se congelan: el presupuesto DEBE mostrar siempre los datos actuales del cliente seleccionado (incluido el tratamiento de IVA, retención y mención que se deduce de su categoría y territorio), y cada descarga DEBE usar esos datos actuales.
- **FR-019**: El usuario DEBE poder borrar cualquier presupuesto tras confirmarlo.

**Cálculo e impuestos** — ver reglas de negocio RN1–RN6 más abajo.

- **FR-020 (RF12 original, RN3)**: El sistema NO DEBE aplicar retención a clientes Particular, aunque el emisor tenga la retención activada.

**PDF**

- **FR-021 (RF12)**: El sistema DEBE generar un PDF descargable con: logo y datos del emisor (nombre, NIF, dirección, email, teléfono); datos del cliente; número; fecha de emisión y «Válido hasta el DD/MM/AAAA»; líneas; desglose con base, % y cuota de IVA, % y cuota de retención (solo si aplica), total; notas; y mención legal cuando aplique (RN6).
- **FR-022**: El nombre del archivo DEBE ser `<número>_<nombre-cliente>.pdf`, con el nombre del cliente sin tildes ni símbolos y con guiones en lugar de espacios (ej.: `PRE-2026-015_Acme-SL.pdf`).
- **FR-023 (RN10, CA2, CA13, CL13)**: El sistema NO DEBE generar el PDF si falta algún dato obligatorio del perfil, si no hay cliente, si no hay al menos una línea, si el cliente es Empresa/autónomo en España sin NIF, o si el cliente está anonimizado (FR-043); DEBE indicar exactamente qué falta o por qué no se puede.
- **FR-024 (CL8)**: Cuando las líneas no quepan en una página, el PDF DEBE paginar, repetir la cabecera de la tabla de líneas en cada página y poner los totales en la última.
- **FR-025**: Los importes del PDF DEBEN coincidir al céntimo con los mostrados en pantalla.

**Historial**

- **FR-026 (HU7)**: El sistema DEBE mostrar una lista de presupuestos ordenada por fecha de emisión (más reciente primero) con número, cliente, fecha de emisión y total, con búsqueda por número o nombre de cliente, y permitir reabrir cualquiera.

**Persistencia y datos**

- **FR-027 (RF13)**: Todos los datos (perfil, ajustes, catálogo, clientes, presupuestos y numeración) DEBEN guardarse en el servidor de la instalación y persistir tras recargar, cerrar el navegador, borrar los datos del navegador o acceder desde otro equipo.
- **FR-028 (RF14)**: Los datos DEBEN guardarse solo en el servidor propio de la instalación del autónomo. NO DEBEN enviarse a servicios de terceros (analítica, publicidad, generación de PDF externa u otros), salvo el alojamiento del propio servidor y el destino de las copias de seguridad. Toda comunicación entre navegador y servidor DEBE ir cifrada.
- **FR-029 (RF15)**: El titular y los asistentes, con el mismo permiso, DEBEN poder exportar todos los datos a un único archivo descargable (incluidos logo y numeración). No hay importación desde la app.
- **FR-032**: *Eliminado* (el aviso «Tus datos se guardan solo en este navegador» ya no aplica).
- **FR-033 (RN7)**: La herramienta DEBE poder usarse a la vez desde varias pestañas, equipos y por varias personas. Los números de presupuesto NUNCA DEBEN duplicarse. Si dos sesiones modifican el mismo elemento (presupuesto, cliente, servicio, perfil o ajustes), prevalece la versión guardada en último lugar.

**Cuentas y acceso**

- **FR-034**: Ningún dato ni función (salvo la pantalla de inicio de sesión) DEBE ser accesible sin haber iniciado sesión. Se entra con email y contraseña.
- **FR-035**: Existen dos tipos de cuenta: **titular** (exactamente una) y **asistente** (cero o más). Ambos ven y modifican los mismos datos con los mismos permisos, salvo que solo el titular puede dar de alta, dar de baja y restablecer la contraseña de asistentes. Dar de baja a un asistente le impide entrar y cierra sus sesiones abiertas; lo que creó se conserva.
- **FR-036**: Las contraseñas DEBEN tener al menos 10 caracteres y NO DEBEN poder leerse por nadie, tampoco por el administrador técnico, ni aparecer en las copias de seguridad de forma legible.
- **FR-037**: El usuario DEBE poder cerrar sesión. La sesión DEBE caducar tras 8 horas sin actividad.
- **FR-038**: Tras 5 intentos fallidos seguidos de inicio de sesión con el mismo email, ese email DEBE quedar bloqueado 15 minutos. El mensaje de error NO DEBE indicar si el fallo está en el email o en la contraseña.
- **FR-039**: Cualquier usuario DEBE poder cambiar su contraseña indicando la actual. El titular DEBE poder asignar una contraseña nueva a un asistente. La contraseña del titular la restablece el administrador técnico siguiendo pasos escritos.
- **FR-040**: La cuenta del titular la crea el administrador técnico al instalar. NO DEBE existir alta pública de cuentas.

**Copias de seguridad**

- **FR-041**: El servidor DEBE hacer una copia de seguridad automática de todos los datos al menos una vez al día, guardarla fuera del propio servidor y conservar las de los últimos 30 días.
- **FR-042**: DEBE existir un procedimiento escrito para que el administrador técnico restaure cualquiera de esas copias.

**Idioma y formato**

- **FR-030 (RN11)**: Toda la interfaz, los mensajes y el PDF DEBEN estar en español de España; los importes en EUR con formato español (1.234,56 €) y las fechas en DD/MM/AAAA.

**Plataforma**

- **FR-031**: La herramienta DEBE ser una aplicación web que se usa desde el navegador, con diseño adaptable: todas las funciones (inicio de sesión, perfil, ajustes, catálogo, clientes, presupuesto, PDF, historial, exportar, gestión de cuentas) DEBEN poder usarse en ordenador, tableta y móvil, sin desplazamiento horizontal de la página a partir de 360 px de ancho.

### Business Rules

- **RN1**: Importe de línea = cantidad × precio unitario, redondeado a 2 decimales (mitad hacia arriba). Base imponible = suma de importes de línea. Ej.: 10 × 45,00 = 450,00; 1 × 300,00 = 300,00; base 750,00 €.
- **RN2**: Cuota de IVA = base × tipo de IVA, redondeada a 2 decimales (mitad hacia arriba), si el tipo de cliente lleva IVA; si no, 0,00 €. Ej.: 750,00 × 21 % = 157,50 €.
- **RN3**: Retención = base × tipo de retención, redondeada a 2 decimales (mitad hacia arriba); nunca sobre base + IVA. Solo se aplica si el emisor tiene la retención activada **y** el tipo de cliente la admite (tabla RN6). Ej.: 750,00 × 15 % = 112,50 €.
- **RN4**: Tipo de retención: 15 % general; 7 % el año de inicio de actividad y los dos siguientes si no hubo actividad profesional el año anterior. El usuario elige el tipo en Ajustes; la herramienta no lo calcula. El porcentaje se muestra en la fila de retención del PDF.
- **RN5**: Total = base + IVA − retención. Ej.: 750,00 + 157,50 − 112,50 = 795,00 €.
- **RN6**: IVA, retención y mención dependen del tipo de cliente:

| Categoría y territorio | IVA | Retención IRPF | Mención en el PDF |
|---|---|---|---|
| Empresa/autónomo — Península y Baleares | Tipo del presupuesto | Sí, si el emisor la aplica | Ninguna |
| Particular — España (cualquier territorio) | Tipo del presupuesto | No | Ninguna |
| Empresa/autónomo — Otro país UE con «NIF-IVA verificado» | Sin IVA (0,00 €) | No | «Inversión del sujeto pasivo» |
| Empresa/autónomo — Otro país UE sin verificar | Tipo del presupuesto | No | Ninguna |
| Empresa/autónomo — Fuera de la UE | Sin IVA (0,00 €) | No | «Operación no sujeta — Art. 69.Uno.1.º Ley 37/1992» |
| Empresa/autónomo — Canarias, Ceuta o Melilla | Sin IVA (0,00 €) | Sí, si el emisor la aplica | Texto configurado en Ajustes (ninguna si está vacío) |
| Particular — fuera de España | Fuera de v1 (no seleccionable) | — | — |

  La fila de retención solo aparece (en pantalla y en el PDF) cuando la retención aplica. La fila de IVA aparece siempre, con 0,00 € cuando no aplica.
- **RN7**: Número PRE-AAAA-NNN, correlativo por año, sin duplicados; reinicia cada año; un número usado no se reutiliza aunque se borre el presupuesto.
- **RN8**: Fecha de validez = fecha de emisión + días de validez. Ej.: 13/11/2026 + 30 días → 13/12/2026.
- **RN9**: Las líneas son copia desde que se añaden; los datos de emisor y retención se copian en la primera descarga; los datos del cliente son siempre los actuales (FR-018).
- **RN10**: Cantidad > 0 y precio ≥ 0, máximo 2 decimales. Para descargar hacen falta cliente y al menos una línea.
- **RN11**: Moneda única EUR, formato español: 1.234,56 €.

### Key Entities

- **Perfil del emisor**: único. Nombre o razón social, NIF, dirección fiscal, email, teléfono, logo.
- **Ajustes fiscales**: únicos. Tipo de IVA por defecto, retención activada, tipo de retención, días de validez, texto de mención para Canarias/Ceuta/Melilla.
- **Servicio**: entrada del catálogo. Nombre, descripción, unidad, precio unitario sin IVA, archivado (sí/no).
- **Cliente**: nombre o razón social, NIF/NIE o NIF-IVA, dirección, país, email, categoría, territorio, NIF-IVA verificado, archivado (sí/no), anonimizado (sí/no).
- **Presupuesto**: número, fecha de creación, fecha de emisión, fecha de validez, tipo de IVA, cliente seleccionado, líneas, notas, indicador de si se ha descargado alguna vez, y copia de los datos del emisor y de retención tomada en la primera descarga (el cliente se referencia, no se copia).
- **Línea de presupuesto**: posición, descripción, unidad (opcional), cantidad, precio unitario, importe. Copia independiente del servicio de origen.
- **Contador de numeración**: último número asignado por año; nunca disminuye.
- **Usuario**: nombre, email (único), contraseña (no legible), tipo (titular o asistente), activo (sí/no).
- **Copia de seguridad**: copia diaria de todos los datos, fecha, guardada fuera del servidor; se conservan 30 días.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con perfil, ajustes, catálogo y cliente ya configurados, un usuario crea y descarga un presupuesto de 3 líneas en menos de 5 minutos.
- **SC-002**: El 100 % de los ejemplos numéricos de esta spec (CA6–CA9, ejemplo de referencia de 2.000,00 € con 15 %, 7 % y particular, CL3, CL7) cuadran al céntimo en pantalla y en el PDF.
- **SC-003**: En el 100 % de los PDF descargados, los importes coinciden al céntimo con los mostrados en pantalla.
- **SC-004**: Tras cerrar y reabrir la herramienta, borrar los datos del navegador o entrar desde otro equipo, el 100 % de los datos guardados sigue presente con los mismos importes.
- **SC-005**: Un usuario sin conocimientos técnicos completa la configuración inicial (perfil, ajustes, 3 servicios) en menos de 10 minutos.
- **SC-006**: Un usuario encuentra y reabre un presupuesto concreto del historial en menos de 30 segundos.
- **SC-007**: Ningún PDF se genera con datos obligatorios incompletos; en todos los intentos bloqueados se indica qué falta.
- **SC-008**: Cada criterio de aceptación de esta spec puede comprobarse en la app siguiendo pasos escritos, sin leer código.
- **SC-009**: El flujo principal (elegir cliente, añadir 3 líneas, revisar totales y descargar el PDF) se completa en un móvil de 360 px de ancho, una tableta y un ordenador sin desplazamiento horizontal de la página y con los mismos importes.
- **SC-010**: Sin sesión iniciada, el 100 % de los intentos de ver datos o usar funciones (desde una ventana privada, otro navegador o con una cuenta dada de baja) muestran solo la pantalla de inicio de sesión.
- **SC-011**: Ante la pérdida total del servidor, el administrador técnico restaura los datos siguiendo los pasos escritos, perdiendo como máximo los cambios del último día.

## Assumptions

- La lista de tratamiento por tipo de cliente (RN6) y la retención en Canarias, Ceuta y Melilla deben revisarse con un asesor fiscal antes de implementar; la spec usa la regla aportada por el usuario.
- La herramienta no valida el formato del NIF/NIE/NIF-IVA ni consulta VIES; solo comprueba que el campo obligatorio no esté vacío. El usuario marca «NIF-IVA verificado» bajo su responsabilidad.
- El tipo de retención (15 % o 7 %) lo elige el usuario en Ajustes; la herramienta no calcula el periodo de inicio de actividad.
- Para aplicar datos nuevos del perfil a un presupuesto ya descargado, el usuario crea un presupuesto nuevo; los descargados conservan su copia.
- Un presupuesto creado consume número aunque se abandone; es coherente con «un número usado no se reutiliza».
- Titular y asistentes comparten los mismos datos, cada uno con su cuenta; la única diferencia es que el titular gestiona las cuentas de asistente.
- Cada autónomo tiene su propia instalación, que instala y mantiene un administrador técnico (puede ser el propio titular). La guía de instalación, alta del titular, copias y restauración forma parte de la entrega.
- La herramienta necesita conexión a internet para usarse; no hay modo sin conexión.
- La herramienta no envía emails, por eso no hay «He olvidado mi contraseña» por email (FR-039).
- Los datos de un cliente anonimizado siguen en las copias de seguridad hasta que estas caducan (30 días); restaurar una copia anterior a la anonimización obliga a repetirla.
- La conservación de las copias durante 30 días (FR-041) es una regla de operación del servidor y no se comprueba en la app: verla exigiría añadir una pantalla de estado de copias, que es alcance nuevo y va contra los principios I y III. La aplica la limpieza automática descrita en la guía de administración. Esta excepción se justifica aquí por escrito, como exige la constitución (Governance).
- Los datos ya no se pierden al borrar el navegador o estropearse el equipo; el riesgo residual es perder como máximo un día de cambios si se pierde el servidor (FR-041, SC-011).
- El autónomo es responsable del tratamiento de los datos de sus clientes; el proveedor del alojamiento actúa como encargado del tratamiento y debe tener contrato conforme al RGPD y servidores en la UE.
- No hay estados (aceptado, rechazado, emitido) ni versiones de presupuesto en v1.
- Excepciones como servicios sobre inmuebles en España (art. 70 LIVA) quedan fuera de v1.

### Fuera de alcance (v1)

- Facturas, incluida la conversión de presupuesto a factura.
- Factura electrónica, Verifactu y TicketBAI (riesgo: entrarían en juego si v2 convierte presupuestos en facturas).
- Envío por email desde la herramienta.
- Registro público de cuentas, varios autónomos en una misma instalación y roles distintos de titular/asistente.
- Recuperación de contraseña por email, verificación en dos pasos e inicio de sesión con Google u otros proveedores.
- Importar datos desde un archivo.
- Registro de accesos consultable y registro de cambios (quién hizo qué).
- Uso sin conexión a internet.
- Almacenamiento en servicios de terceros distintos del alojamiento del servidor y del destino de las copias de seguridad.
- Validación online de NIF o NIF-IVA (VIES).
- Clientes particulares fuera de España.
- Varias monedas y PDF en otros idiomas.
- Aplicaciones nativas de móvil o escritorio (v1 es solo web adaptable).
- Descuentos por línea o globales.
- Varios tipos de IVA en un mismo presupuesto.
- Estados de presupuesto, versiones, duplicado de presupuestos y filtros avanzados del historial.
