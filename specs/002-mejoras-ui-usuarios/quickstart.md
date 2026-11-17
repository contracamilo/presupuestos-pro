# Quickstart: comprobar PresupuestosPro v1.1

**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md) | **Guía base**: [quickstart de la 001](../001-presupuestos-pro/quickstart.md)

Guía para comprobar en la app esta iteración (constitución, principio IV). El arranque lo hace una persona técnica; los escenarios están escritos para personas no técnicas. Los escenarios de la 001 siguen siendo válidos y deben repetirse como regresión (sección E), salvo el paso de alta del titular, que cambia.

## 1. Arrancar

### 1a. Instalación nueva (persona técnica)

```bash
docker compose up -d --build
docker compose exec app pytest          # incluye regla de tipos de documento, países, fechas y creación del titular
```

**No** se ejecuta `crear-titular` (ya no existe). Abrir `https://localhost` y seguir el escenario B1.

### 1b. Actualización de una instalación de v1 (persona técnica)

Partir de una instalación v1 con los datos de prueba de la 001 (clientes, presupuestos, numeración) y anotar el total de 3 presupuestos del historial. Después:

```bash
docker compose up -d --build            # al arrancar, la app añade el tipo de documento a los clientes
```

Seguir el escenario E1.

## 2. Datos de prueba

Los de la [001](../001-presupuestos-pro/quickstart.md#2-datos-de-prueba), más:

| Qué | Valor |
|---|---|
| Titular (instalación nueva) | «Laura Gómez», laura@ejemplo.es, creada en B1 |
| Cliente de v1 con país libre | «Müller GmbH» con país escrito a mano «Alemania (Berlín)» antes de actualizar |
| Navegador | En español (para que el calendario muestre DD/MM/AAAA) |

## 3. Escenarios de validación

Rutas en [contracts/cambios-rutas-y-pantallas.md](./contracts/cambios-rutas-y-pantallas.md); pantallas en [contracts/interfaz.md](./contracts/interfaz.md).

### A. Menú lateral (US1)

| # | Pasos | Resultado esperado |
|---|---|---|
| A1 | En un ordenador (ventana ≥ 1024 px), entrar como titular y abrir cada sección del menú | Menú fijo a la izquierda con «Trabajo» y «Configuración»; la sección abierta aparece resaltada; dentro de un presupuesto se resalta «Presupuestos» (FR-101, FR-102) |
| A2 | Estrechar la ventana o abrir en un móvil de 360 px | El menú desaparece y aparece el botón ☰ en la cabecera; no hay desplazamiento horizontal (FR-103, SC-105) |
| A3 | En el móvil: pulsar ☰, luego pulsar fuera; volver a abrir y pulsar ☰; volver a abrir y elegir «Clientes» | Se abre por encima del contenido y se cierra en los tres casos; en el tercero se abre Clientes con el menú cerrado (US1 AS3) |
| A4 | Con el menú abierto en el móvil, intentar desplazar la página de fondo | El fondo no se mueve |
| A5 | En una tableta (768–1023 px) | Mismo comportamiento que el móvil (botón ☰) |
| A6 | Entrar como asistente | No aparece «Usuarios» (US1 AS4) |
| A7 | Cerrar sesión | La pantalla de inicio de sesión no muestra menú (US1 AS5) |
| A8 | Solo con teclado (Tab, Intro, Escape) en móvil y en ordenador: abrir el menú, llegar a «Ajustes», cerrar con Escape | Todo se puede hacer sin ratón; con un lector de pantalla el botón se anuncia como «Abrir menú» / «Cerrar menú» (FR-104) |

### B. Usuarios sin comandos (US3)

| # | Pasos | Resultado esperado |
|---|---|---|
| B1 | Instalación nueva: abrir `https://localhost` | Aparece «Crear la cuenta del titular», sin pedir código (US3 AS1) |
| B2 | Enviar con contraseña de 8 caracteres; luego con contraseñas distintas | Mensaje junto al campo en cada caso; no se crea la cuenta (FR-107) |
| B3 | Rellenar Laura Gómez, laura@ejemplo.es y una contraseña de 12 caracteres dos veces | Entra directamente en el historial (US3 AS2). Cronometrar B1–B3 + B6: menos de 3 minutos (SC-102) |
| B4 | Cerrar sesión y escribir en la barra `/crear-titular` | Se muestra el inicio de sesión (US3 AS3, FR-109) |
| B5 | Como titular, abrir «Usuarios» | Lista con Laura (Titular, Activa) y botón «Añadir usuario» (US3 AS4) |
| B6 | «Añadir usuario»: Pablo, pablo@ejemplo.es, contraseña de 10+ caracteres dos veces | Pablo aparece en la lista; en otra ventana privada entra con esos datos (US3 AS5) |
| B7 | Intentar dar de alta otra vez pablo@ejemplo.es; luego una contraseña corta; luego contraseñas distintas | En cada caso, mensaje junto al campo y no se crea (US3 AS6) |
| B8 | «Restablecer contraseña» de Pablo (con repetición) | Pablo entra con la nueva; la anterior falla (US3 AS8) |
| B9 | «Dar de baja» a Pablo y confirmar | Pablo no puede entrar; si tenía la sesión abierta, la pierde en su siguiente acción (US3 AS7) |
| B10 | En «Mi cuenta», cambiar la contraseña con repetición distinta | «Las contraseñas no coinciden.» junto al campo |
| B11 | Instalación nueva: abrir la app en dos equipos (o dos navegadores), rellenar «Crear la cuenta del titular» en ambos con emails distintos y pulsar «Crear cuenta» casi a la vez | Solo uno entra; el otro ve «La cuenta del titular ya existe. Inicia sesión.». En «Usuarios» hay un único titular |

### C. Volver al historial (US2)

| # | Pasos | Resultado esperado |
|---|---|---|
| C1 | Desde el historial, abrir un presupuesto | Arriba aparece «← Volver al historial» (US2 AS1) |
| C2 | Cambiar una cantidad e inmediatamente pulsar «Volver al historial»; volver a abrir el presupuesto | El cambio está guardado y el total del historial lo refleja (US2 AS2) |
| C3 | Buscar «Acme» en el historial, abrir un resultado y pulsar «Volver al historial» | La lista sigue filtrada por «Acme» (US2 AS3) |
| C4 | Pulsar «Nuevo presupuesto» y luego «Volver al historial» | El presupuesto nuevo aparece en la lista (US2 AS4) |
| C5 | Copiar la dirección de un presupuesto, abrirla en otra pestaña y pulsar «Volver al historial» | Historial sin filtros |
| C6 | Desconectar la red (modo avión), cambiar una cantidad y pulsar «Volver al historial» | Aparece «No se ha podido guardar. Comprueba tu conexión.» y no se sale del presupuesto |
| C7 | Prueba de navegación con una persona que no conoce la app: 5 tareas (ir a Clientes, volver a un presupuesto concreto, ir a Ajustes, volver al historial desde un presupuesto, ir a Mi cuenta) | Las 5 sin usar «atrás» del navegador (SC-101) |
| C8 | Escribir 0 en la cantidad de una línea e inmediatamente pulsar «Volver al historial» | Aparece «La cantidad debe ser mayor que 0.» junto a la línea y no se sale del presupuesto; al pulsar de nuevo «Volver al historial» sí se sale y la línea conserva su cantidad anterior (caso límite «Volver con cambios aún guardándose») |

### D. Selectores, fechas y logo (US4, US5, US6)

| # | Pasos | Resultado esperado |
|---|---|---|
| D1 | Nuevo cliente, Empresa/autónomo, Península: abrir «Tipo de documento» | Sin indicar, NIF, CIF, NIE; el país está fijado en «España» (US4 AS1, FR-113) |
| D2 | Elegir CIF, escribir B12345678 y cambiar categoría a «Particular» | El tipo se vacía y solo ofrece NIF y NIE; el número B12345678 sigue escrito (US4 AS2, FR-112) |
| D3 | Empresa, territorio «Otro país UE» | Tipo preseleccionado «NIF-IVA UE»; el país ofrece solo países de la UE sin España (US4 AS3, AS4) |
| D4 | Empresa, territorio «Fuera de la UE» | Tipo preseleccionado «Otro documento extranjero»; el país no ofrece países de la UE |
| D5 | Recorrer los formularios de cliente, servicio, línea manual y ajustes | Tipo de documento, categoría, territorio, país, unidad, IVA y retención son selectores; ninguno admite texto libre (SC-103, US4 AS5) |
| D6 | Abrir un presupuesto y pulsar la fecha de emisión; elegir otro día | Se abre un calendario; la fecha queda en DD/MM/AAAA y la validez se recalcula (emisión 20/11/2026 → validez 20/12/2026 con 30 días) (US5 AS1, AS2). Cronometrar: < 10 s (SC-104) |
| D7 | Abrir el calendario de «Válido hasta» | Los días anteriores a la emisión no se pueden elegir (US5 AS3) |
| D8 | En un móvil, pulsar una fecha | Se abre el calendario del móvil, no el teclado (US5 AS4). Cronometrar: < 10 s (SC-104) |
| D9 | Perfil sin logo | «Logo (aparece en tus PDF)», formatos y tamaño, botón «Subir logo» (US6 AS1) |
| D10 | Subir un PNG < 2 MB; descargar un presupuesto nunca descargado | Vista previa con «Cambiar logo» y «Quitar logo»; el PDF lleva el logo en la cabecera (US6 AS2, AS3) |
| D11 | «Quitar logo» y confirmar; descargar otro presupuesto nunca descargado y volver a descargar el de D10 | El nuevo sale sin logo; el de D10 conserva el logo (US6 AS4) |
| D12 | Subir un archivo de 3 MB o un PDF como logo | Se rechaza con «Formatos permitidos: PNG, JPG o SVG, hasta 2 MB» (regla de la 001) |

### E. Actualización y regresión

| # | Pasos | Resultado esperado |
|---|---|---|
| E1 | **(Técnico)** Tras 1b, entrar con la cuenta de titular de v1 | Mismos clientes, presupuestos, números y los 3 totales anotados, al céntimo (SC-106) |
| E2 | Abrir la ficha de un cliente de v1 | «Tipo de documento: Sin indicar»; el número de documento se conserva; se puede elegir el tipo y guardar (US4 AS6, FR-114) |
| E3 | Abrir «Müller GmbH» (país «Alemania (Berlín)») | El país muestra «Revisar país: Alemania (Berlín)»; se puede guardar sin cambiarlo y, al elegir «Alemania», desaparece el aviso |
| E4 | Exportar | El archivo tiene `"version": 2` y cada cliente lleva `tipo_documento` |
| E5 | Anonimizar un cliente con tipo de documento | El tipo queda «Sin indicar» junto con el resto de datos borrados |
| E6 | Repetir los escenarios de la [guía de la 001](../001-presupuestos-pro/quickstart.md), sustituyendo «Cuentas» por «Usuarios» y el alta del titular por B1–B3 | Mismos resultados (sin regresiones en cálculo, PDF, numeración y acceso) |

### F. Modo oscuro (US7, ampliación 2026-11-17)

Selector, ruta, cookie y paleta en [contracts/tema.md](./contracts/tema.md).

**Preparación**: sesión de titular; un presupuesto en borrador con dos líneas y cliente «Acme SL»; en el historial, presupuestos en estado Borrador, Enviado y Caducado; un logo PNG negro con fondo transparente. Para cambiar el modo del dispositivo: en macOS, *Ajustes del Sistema → Apariencia*; en Windows, *Configuración → Personalización → Colores*; en Android/iOS, el ajuste «Modo oscuro».

| # | Pasos | Resultado esperado |
|---|---|---|
| F1 | Abrir el menú lateral y localizar el selector | Al final de «Configuración», antes de «Salir», un grupo «Tema» con «Claro», «Oscuro» y «Como el sistema»; si nunca se eligió, está marcado «Como el sistema» (FR-117, US7 AS6) |
| F2 | Con la app en claro, elegir «Oscuro» | Toda la pantalla pasa a oscuro al momento, sin recargar (US7 AS1). Cronometrar: un toque, < 5 s (SC-108) |
| F3 | Abrir el presupuesto, empezar a escribir una línea nueva sin salir del campo y cambiar de tema dos veces | La línea y lo escrito siguen ahí; los totales no cambian; al salir del campo se guarda con normalidad (US7 AS2, FR-118) |
| F4 | Con «Oscuro»: recargar; ir a Clientes; cerrar el navegador por completo, volver a abrirlo y entrar | La app sigue en oscuro en los tres casos (US7 AS3, SC-112) |
| F5 | Con «Oscuro», recargar varias veces seguidas Presupuestos, Clientes y Perfil | En ningún momento se ve un destello blanco (US7 AS11, FR-126) |
| F6 | Elegir «Como el sistema» con el dispositivo en claro; sin tocar la app, poner el dispositivo en oscuro y luego otra vez en claro | La app cambia a oscuro y vuelve a claro sola (US7 AS4, FR-123) |
| F7 | Con el dispositivo en oscuro, elegir «Claro» en la app y recargar | La app se ve en claro y sigue en claro tras recargar (US7 AS5, FR-124) |
| F8 | Con la app en oscuro, descargar el PDF del presupuesto; poner la app en claro y descargarlo otra vez | Los dos PDF tienen fondo blanco y se ven iguales (US7 AS7, SC-111, FR-130) |
| F9 | En oscuro, a 360 px y a 1280 px: recorrer todas las pantallas del menú, abrir el menú en móvil, provocar un error de formulario (cantidad 0), abrir la ventana «Exportar…», el aviso de confirmación de «Quitar logo» y mirar el historial con Borrador, Enviado y Caducado | Todo se lee bien; no queda ningún fondo blanco suelto ni texto oscuro sobre fondo oscuro; las tres etiquetas de estado se distinguen entre sí por texto, icono y forma (US7 AS8, FR-125, SC-109) |
| F10 | En oscuro: abrir el calendario de «Fecha de emisión» y el selector «Categoría» de un cliente | Se muestran en oscuro y legibles (US7 AS9, FR-125) |
| F11 | Solo con teclado (y con lector de pantalla si es posible): llegar al selector con Tab, cambiar de opción con las flechas | El foco se ve en los dos temas; el lector anuncia «Tema», la opción y que está seleccionada; el tema cambia al moverse (US7 AS10, FR-119) |
| F12 | En oscuro, subir en Perfil el logo negro transparente | La vista previa se ve con claridad sobre fondo blanco (US7 AS12, FR-129) |
| F13 | Desactivar JavaScript en el navegador, recargar, elegir «Claro» y pulsar «Aplicar» | Se recarga la misma pantalla en claro; tras volver a activar JavaScript el botón «Aplicar» no se ve (FR-120) |
| F14 | Cerrar sesión con «Oscuro» elegido y el dispositivo en claro | La pantalla de inicio de sesión se ve en claro y sin selector; al entrar de nuevo la app vuelve a oscuro (FR-124, caso límite «Cerrar sesión») |
| F15 | Abrir la app en una ventana privada y entrar | Tema «Como el sistema» (caso límite «Navegador que borra sus datos o ventana privada») |
| F16 | Con «Oscuro», desconectar la red (modo avión) y elegir «Claro» | La página cambia a claro y aparece «No se ha podido guardar. Comprueba tu conexión.»; al reconectar y recargar vuelve a oscuro ([tema.md](./contracts/tema.md#selector-tema-fr-117-a-fr-120)) |
| F18 | Con JavaScript desactivado: en «Mi cuenta», cambiar la contraseña con una repetición distinta (aparece el error); después elegir «Claro» y pulsar «Aplicar» | Se abre el historial en claro, sin página de error (FR-120) |
| F19 | Con «Oscuro» elegido y el dispositivo en claro, escribir en la barra una dirección que no existe (p. ej. `/no-existe`) | La página de error se ve en claro, sin menú (caso límite «Páginas de error que se muestran sin comprobar la sesión») |
| F17 | **(Técnico)** `docker compose exec app pytest tests/test_paleta.py tests/test_tema.py` | Pasan: contrastes de los dos temas, paleta oscura completa, PDF sin hoja oscura, ruta `/tema` y cookie (SC-110) |

## 4. Comprobación de los criterios de éxito

| Criterio | Escenarios |
|---|---|
| SC-101 | C7 |
| SC-102 | B1–B3, B6 |
| SC-103 | D5 |
| SC-104 | D6, D8 |
| SC-105 | A2, A3 |
| SC-106 | E1 |
| SC-107 | Toda esta guía (solo 1a, 1b, E1 y F17 son técnicos: instalación, actualización del servidor y comprobación automática de contrastes) |
| SC-108 | F2 |
| SC-109 | F9 |
| SC-110 | F17 (además, cualquier comprobador de contraste sobre la tabla de [tema.md](./contracts/tema.md#pares-de-contraste-en-oscuro-fr-127)) |
| SC-111 | F8 |
| SC-112 | F4, F5 |
