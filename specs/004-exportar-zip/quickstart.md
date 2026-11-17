# Guía de verificación: PresupuestosPro v1.3 — Exportar en un .zip

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Contratos**: [rutas-http.md](./contracts/rutas-http.md), [archivo-exportacion.md](./contracts/archivo-exportacion.md)

Cada paso tiene un resultado observable en la app (constitución, principio IV). Los pasos técnicos van marcados **(Técnico)**.

## 0. Preparación

1. **(Técnico)** Arranca la app como en la 003 (macOS: `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`) y ejecuta `pytest`: todo en verde.
2. Entra como titular con un perfil completo (nombre, NIF, dirección, logo). Prepara estos presupuestos (cliente empresa en península con NIF, al menos una línea):
   - **P1, P2, P3**: tres presupuestos **descargados** una vez (el P1 es el de control con total **3.604,00 €**). Cliente del P2: **«Diseño/Web S.L.»**; el P3 con tildes («Estudio García»).
   - **P4**: presupuesto **sin descargar** (Borrador).
   - **P5**: presupuesto descargado cuyo cliente después **anonimizas** (Clientes → Anonimizar).
3. Anota, de cada presupuesto, su estado en el historial y el contenido de su PDF individual (descarga P1, P2 y P3 desde la app; ya están descargados, así que no cambia nada).
4. Herramientas: descompresor del sistema (Windows, macOS), un lector de PDF y un editor de texto para el archivo de datos.

## A. Exportar todo (US1, SC-301, SC-302)

| # | Paso | Resultado esperado |
|---|---|---|
| A1 | En el historial, busca el botón | «Exportar…» visible junto a «Nuevo presupuesto» y **no** hay «Exportar» en el menú lateral |
| A2 | Pulsa «Exportar…» | Se abre una ventana con «Todo» marcada y «Seleccionar qué exportar»; no se ha descargado nada |
| A3 | Lee el texto de «Todo» | «Se incluirán 3 PDF. Los 2 presupuestos sin descargar solo irán en el archivo de datos.» (P4 y P5 no tienen PDF) |
| A3b | Mira el botón «Descargar .zip» | Dice «(4 archivos)»: 3 PDF + el archivo de datos |
| A4 | Pulsa «Descargar .zip» | El botón pasa a «Preparando la copia…»; al terminar se descarga **un solo** archivo `presupuestospro-copia-AAAA-MM-DD.zip` con la fecha de hoy y la ventana se cierra |
| A5 | Descomprime con doble clic | Exactamente 4 archivos: 3 PDF y un `.json` con el mismo nombre base que el zip |
| A6 | Mira los nombres de los PDF | `PRE-… - Estudio García.pdf` (con tilde), `PRE-… - Diseño Web S.L.pdf` (sin la `/`, y la «ñ» conservada), sin errores al abrir el zip |
| A7 | Abre el PDF del P1 y compáralo con su descarga individual de la preparación | Mismo contenido, aspecto y emisor; total **3.604,00 €** |
| A8 | Cambia tu dirección en el Perfil y repite la exportación | El PDF del P1 sigue mostrando la dirección de su primera descarga |
| A9 | Cierra sesión y entra como asistente (si existe) | También ve «Exportar…» y puede exportar |

## B. Seleccionar qué exportar (US1b, SC-309)

| # | Paso | Resultado esperado |
|---|---|---|
| B1 | «Exportar…» → «Seleccionar qué exportar» | Lista con una casilla por presupuesto (número, cliente, estado), «Marcar todos» y «0 marcados» |
| B2 | Mira la lista | Solo P1, P2 y P3: **no** salen P4 (borrador) ni P5 (cliente eliminado) |
| B3 | Sin marcar nada, mira «Descargar .zip» | Desactivado, con «Marca al menos un presupuesto.» |
| B4 | Lee el aviso de la ventana | Indica que la copia es parcial y no sirve como copia de seguridad completa |
| B5 | Marca P1 y P3 → «Descargar .zip» | Se descarga `presupuestospro-seleccion-AAAA-MM-DD.zip` (no «copia») |
| B6 | Descomprime | 2 PDF (P1 y P3) y un `.json` |
| B7 | **(Técnico)** Abre el `.json` | `"alcance": "seleccion"`, solo P1 y P3 en `presupuestos` (con sus líneas) y sus clientes; `servicios` y `contadores` vacíos; `perfil` y `ajustes` en `null` |
| B8 | Marca algo, vuelve a «Todo» y descarga | Sale la copia completa (4 archivos, nombre «copia») |
| B8b | Marca y desmarca casillas | El botón pasa de «(1 archivo)» con 0 marcados a «(2 archivos)», «(3 archivos)»…, y vuelve a «(4 archivos)» al elegir «Todo» |
| B9 | «Marcar todos» | Se marcan todas las casillas de la lista y el recuento coincide |
| B10 | Cierra con «Cancelar», con Esc y con un clic fuera | La ventana se cierra, no se descarga nada; el foco vuelve al botón «Exportar…» |

## C. El archivo de datos y la solo lectura (US2, SC-302, SC-304)

| # | Paso | Resultado esperado |
|---|---|---|
| C1 | **(Técnico)** Abre el `.json` de la copia completa | `"alcance": "completo"`; los 5 presupuestos (incluidos P4 y P5) con sus líneas; catálogo, perfil con logo, ajustes y contadores; **sin** usuarios, contraseñas ni sesiones |
| C2 | Compara el historial antes y después de exportar | Mismos presupuestos, estados y numeración; P4 sigue en «Borrador» |
| C3 | Abre P4 y pulsa «Descargar PDF» | Solo ahora pasa a «Enviado» (la exportación no lo había hecho) |
| C4 | Crea un presupuesto nuevo tras exportar | Su número es el siguiente al último (la exportación no consumió numeración) |

## D. Casos límite (SC-305, SC-306)

| # | Paso | Resultado esperado |
|---|---|---|
| D1 | Instalación sin presupuestos: «Exportar…» | La ventana muestra «No hay presupuestos que exportar», sin opciones de descarga; no se descarga nada |
| D2 | Solo borradores, ninguno descargado: «Exportar…» | «Todo» avisa de «0 PDF»; «Seleccionar» aparece desactivada con «Aún no hay presupuestos descargados»; «Todo» descarga un zip con solo el `.json` |
| D3 | Cliente «Diseño/Web S.L.» | Ya comprobado en A6: el zip se abre sin errores en Windows y macOS |
| D4 | Cliente con nombre de 150 caracteres | El PDF tiene un nombre razonable (cliente recortado) y el zip se abre bien |
| D5 | Abre la ventana, y en otra pestaña anonimiza el cliente de un presupuesto marcado; pulsa «Descargar .zip» | Mensaje «La lista ha cambiado. Cierra la ventana y vuelve a abrirla.»; la ventana sigue abierta |
| D6 | Sin sesión, abre `/exportar` | Te lleva a iniciar sesión; no se descarga nada. Con sesión, abrir `/exportar` en la barra de direcciones (GET) da «página no existe» |

## E. Muchos presupuestos y espera (US3, SC-307)

| # | Paso | Resultado esperado |
|---|---|---|
| E1 | **(Técnico)** Con 50 presupuestos descargados, «Descargar .zip» y cronometra | Durante toda la preparación el botón muestra «Preparando la copia…» y está desactivado; no se puede lanzar una segunda exportación; al acabar se descarga un zip con 50 PDF. Anota el tiempo |
| E2 | **(Técnico)** Con 200 presupuestos | Se descarga un único zip completo |
| E3 | Mientras prepara, pulsa varias veces el botón | Solo hay una exportación; sigue desactivado |
| E4 | **(Técnico)** Provoca un fallo (p. ej. detén el servidor a mitad) | La ventana muestra un mensaje claro y los controles se reactivan; no queda ningún archivo parcial ni cambia ningún dato |

## F. Accesibilidad y diseño (FR-301c, FR-315, SC-310)

| # | Paso | Resultado esperado |
|---|---|---|
| F1 | Solo con teclado: Tab hasta «Exportar…», Intro, recorre la ventana, marca casillas, descarga | Todo es alcanzable; el foco no sale de la ventana; Esc la cierra y el foco vuelve al botón |
| F2 | Con lector de pantalla (VoiceOver/NVDA) | La ventana se anuncia con su título; las casillas, el recuento y los avisos se leen con su etiqueta |
| F3 | A 320, 360, 800 y 1280 px | Sin desplazamiento horizontal; la lista se desplaza dentro de la ventana; botones de al menos 44 × 44 px |
| F4 | Mira colores y tipografía | Mismos botones, campos, mensajes y tipografía que el resto de la app |

## G. Regresión

| # | Paso | Resultado esperado |
|---|---|---|
| G1 | Descarga individual de un PDF | Igual que antes: mismo nombre `PRE-…_Cliente.pdf` de la 001, mismo contenido |
| G2 | Busca en el historial con la ventana cerrada y abierta después | La búsqueda funciona y la ventana sigue ofreciendo todos los exportables |
| G3 | **(Técnico)** `python -m presupuestos copia` | Sigue generando la copia de la base de datos |
