# Guía de verificación: PresupuestosPro v1.2 — Rediseño visual

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Contratos**: [sistema-visual.md](./contracts/sistema-visual.md), [estados.md](./contracts/estados.md), [pdf-diseno.md](./contracts/pdf-diseno.md)

Cada paso tiene un resultado observable en la app (constitución, principio IV). Los pasos técnicos van marcados **(Técnico)**.

## 0. Preparación

1. **(Técnico)** Arranca la app (con Docker, o en local como en la 002, con `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` en macOS). Ejecuta `pytest`: todo en verde.
2. Entra como titular. Ten preparados:
   - **P1**: presupuesto con logo en el perfil, cliente empresa en península, 3 líneas, retención activa y notas. **Sin descargar** y con validez futura → debe verse «Borrador».
   - **P2**: otro presupuesto con validez futura, **descargado** una vez → «Enviado».
   - **P3**: presupuesto con «Válido hasta» de ayer (descargado o no) → «Caducado».
   - **P4**: presupuesto con 40 líneas, una descripción muy larga y un total ≥ 1.000.000,00 €.
3. Herramientas gratuitas: las del navegador (inspector, simulación de dispositivo, simulación de visión), un comprobador de contraste (p. ej. el del inspector de Chrome o Firefox) y un lector de pantalla (VoiceOver en Mac/iPhone, NVDA en Windows o TalkBack en Android).
4. Anchos de prueba: **320**, **360**, **800** y **1280 px**.

## A. Coherencia visual (US1, SC-201)

Recorre las 13 pantallas: Historial, Presupuesto, Clientes, Cliente, Catálogo, Perfil, Ajustes, Usuarios, Mi cuenta, Iniciar sesión, Crear la cuenta del titular (en una instalación vacía), Error (abre `/presupuestos/999999`) y el menú abierto en móvil.

| # | Paso | Resultado esperado |
|---|---|---|
| A1 | Compara el título de cada pantalla | Mismo tamaño, peso y separación en todas; es el texto más grande del contenido; un solo título principal |
| A2 | Compara Perfil, Cliente y Usuarios (formularios) | Etiquetas encima, campos del mismo alto y borde, ayudas en gris debajo, mismos botones |
| A3 | Provoca un error en un campo (p. ej. contraseña corta en Mi cuenta) | Mensaje rojo con icono debajo del campo y borde del campo en rojo; igual en todos los formularios |
| A4 | Busca botones principal, secundario y de peligro (p. ej. pantalla del presupuesto) | Tres aspectos distintos y constantes en toda la app |
| A5 | Mira el bloque de totales de P1 | «Total» más grande y en negrita, con una línea encima; base, IVA y retención en tamaño normal, alineadas a la derecha |
| A6 | Guarda el perfil, provoca un aviso y un error | Éxito (verde), aviso (ámbar) y error (rojo) con icono propio y aspecto igual en todas las pantallas |
| A7 | En 360 px, recorre todas las pantallas | Sin desplazamiento horizontal; botones y enlaces del menú de al menos 44 px de alto |
| A8 | Mira el historial y la lista de clientes en 360 y 1280 px | Tarjetas en móvil y filas en escritorio; importes alineados a la derecha, cifras en columna |
| A9 | Abre la app en dos dispositivos distintos (p. ej. Mac y móvil Android) | Misma tipografía en ambos (SC-210); tildes, «ñ», «€», «¿» bien dibujados |
| A10 | Activa el modo oscuro del sistema y recarga | La app sigue clara y legible; calendario y selectores no quedan ilegibles |

## B. PDF (US2, SC-206, SC-207)

| # | Paso | Resultado esperado |
|---|---|---|
| B1 | **(Técnico)** Antes de implementar, guarda el PDF de P1 y de P4 generados con v1.1 | Referencias para comparar |
| B2 | Descarga P1 con v1.2 y ábrelo junto al de v1.1 | Mismos bloques, textos, importes y orden (0 diferencias de contenido); cambia solo el aspecto |
| B3 | Mira la jerarquía | Se distinguen emisor, título con número, fechas, cliente, tabla y totales; el «Total» es la cifra más destacada |
| B4 | Busca el color | Azul de marca solo en el título con el número, la cabecera de la tabla y la línea del «Total»; el resto en negro y grises (Q4) |
| B5 | Revisa la tabla | Cantidad, precio e importe a la derecha y en columna; filas separadas por líneas finas |
| B6 | Descarga P4 | Varias páginas, cabecera de la tabla repetida, ninguna fila partida, desglose y notas tras la última línea, total de 1.000.000,00 € sin cortes |
| B7 | Quita el logo en Perfil, crea un presupuesto nuevo y descárgalo | Cabecera equilibrada sin hueco donde iba el logo |
| B8 | Sube un logo muy ancho (p. ej. 1000 × 100 px) y descarga | El logo no se deforma ni empuja los datos del emisor |
| B9 | Imprime P1 en blanco y negro (o «Imprimir en PDF» con escala de grises) | Todo legible; el «Total» se identifica a la primera |
| B10 | Busca la palabra «Borrador», «Enviado» o «Caducado» en el PDF | No aparece (FR-211) |
| B11 | **(Técnico)** Mide el tiempo de descarga de P4 | Menos de 3 s |
| B12 | Mira la fuente del PDF (propiedades del documento en el visor) | Inter, la misma que la app |
| B13 | Enseña a 5 personas, sin decir cuál es cuál, el PDF de v1.1 y el de v1.2 del mismo presupuesto (P1) y pregunta cuál les parece «más profesional» | Al menos 4 de 5 eligen el de v1.2 (SC-206) |

## C. Estados (US3, SC-205)

| # | Paso | Resultado esperado |
|---|---|---|
| C1 | Abre el historial | P1 «Borrador», P2 «Enviado», P3 «Caducado», cada uno con texto, icono y aspecto distintos |
| C2 | Activa la simulación de escala de grises (o de daltonismo) del navegador | Los estados se siguen distinguiendo por texto, icono y forma (Borrador con borde discontinuo, Caducado en cursiva) |
| C3 | Abre P2 | La etiqueta «Enviado» aparece junto al número, igual que en el historial |
| C4 | En P3, cambia «Válido hasta» a una fecha futura | La etiqueta cambia sin recargar a «Enviado» (si se descargó) o «Borrador» |
| C5 | En P1, pon «Válido hasta» = hoy | Sigue en «Borrador» (no caduca hasta mañana) |
| C6 | Descarga P1 y vuelve al historial | P1 pasa a «Enviado» |
| C7 | Pon «Válido hasta» de P2 en el pasado y vuelve a descargarlo | Sigue en «Caducado» |
| C8 | Muestra el historial a 5 personas y pide el estado de cada presupuesto | Aciertan todos en menos de 5 s por presupuesto, también en escala de grises |

## D. Accesibilidad (US4, SC-202 a SC-204)

| # | Paso | Resultado esperado |
|---|---|---|
| D1 | Al cargar cualquier pantalla con sesión, pulsa Tab | Aparece «Saltar al contenido»; con Intro, el foco va al contenido |
| D2 | Recorre con Tab la pantalla del presupuesto | El foco se ve siempre (contorno azul grueso) y sigue el orden visual |
| D3 | Haz solo con teclado: entrar, crear presupuesto, buscar y elegir cliente, añadir una línea, descargar el PDF | Se completa sin ratón (SC-203) |
| D4 | Mide con el comprobador el contraste de: texto, texto gris, enlaces, botones, bordes de campos, mensajes y las cinco etiquetas de estado | Texto ≥ 4,5:1; bordes, iconos y foco ≥ 3:1 (SC-202). Valores de referencia en [sistema-visual.md](./contracts/sistema-visual.md#pares-de-contraste) |
| D5 | Zoom del navegador al 200 % en 1280 px, y ventana de 320 px | Sin desplazamiento horizontal, nada cortado ni solapado (SC-204) |
| D6 | Sube el tamaño de letra por defecto del navegador a 20 px | Todo crece en proporción, sin solapes |
| D7 | Con el lector de pantalla, recorre el historial y un presupuesto | Un único título principal; encabezados en orden; estados leídos como «Estado: Borrador»; cabeceras de la tabla de totales anunciadas; cada campo con su etiqueta |
| D8 | Activa «Reducir movimiento» en el sistema y abre el menú en móvil | Se abre sin animación |
| D9 | Con el lector de pantalla configurado en otro idioma (p. ej. inglés), lee una pantalla y el PDF | Los pronuncia con voz en español: la página y el PDF declaran el español (FR-214b) |
| D10 | En 360 px, mide con el inspector el área de botones, enlaces del menú, casillas y selectores | Todos de al menos 44 × 44 px (FR-214a) |

## E. Regresión y aspectos técnicos

| # | Paso | Resultado esperado |
|---|---|---|
| E1 | **(Técnico)** `pytest` | Todo en verde, incluidos los 106 tests anteriores (SC-208) |
| E2 | **(Técnico)** Arranca con una base de datos de v1.1 | Funciona sin pasos de actualización; `PRAGMA user_version` sigue en 2 |
| E3 | **(Técnico)** Cambia `--color-marca` en `tokens.css`, recarga y descarga un PDF | Cambia en todas las pantallas y en el PDF sin tocar nada más (SC-209). Deshaz el cambio |
| E4 | **(Técnico)** Inspector → Red, recarga cualquier pantalla | Ninguna petición fuera del propio dominio (FR-218) |
| E5 | Repite las guías de la [001](../001-presupuestos-pro/quickstart.md) y la [002](../002-mejoras-ui-usuarios/quickstart.md) de forma rápida | Todo funciona igual; solo cambia el aspecto |
| E6 | Exporta los datos y compara con una exportación anterior | Misma estructura (`"version": 2`) |
| E7 | Imprime desde el navegador (Imprimir → Vista previa) el historial y un presupuesto, en v1.1 (copia previa) y en v1.2 | La versión v1.2 se lee al menos igual de bien: sin texto cortado ni ilegible (spec, casos límite: «no debe empeorar») |
