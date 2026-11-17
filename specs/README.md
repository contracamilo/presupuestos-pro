# Estado del producto

Índice de las especificaciones de PresupuestosPro y de su estado. Las reglas que gobiernan todo el producto están en [`.specify/memory/constitution.md`](../.specify/memory/constitution.md).

## Especificaciones

| Spec | Nombre | Qué aporta | Rama | Estado |
|---|---|---|---|---|
| [001](001-presupuestos-pro/spec.md) | PresupuestosPro v1 | Presupuestos con IVA/IRPF según tipo de cliente, clientes, catálogo, PDF, cuentas (titular y asistentes), exportación de datos y copias de seguridad | `main` (sin rama de feature) | Implementada (68 de 69 tareas). Pendiente: T066 (pytest en Docker y recorrido completo de `quickstart.md`). **Modificada por** 002 (navegación y alta del titular), 003 (apariencia y PDF) y 004 (la exportación en JSON, FR-029, sustituida por el .zip) |
| [002](002-mejoras-ui-usuarios/spec.md) | Navegación, formularios, usuarios y modo oscuro | Menú lateral, «Volver al historial», alta del titular desde el navegador, selectores y calendarios, logo visible en Perfil; **ampliación 2026-11-17**: modo oscuro conmutable (Claro / Oscuro / Como el sistema; US7, FR-117–FR-130) | v1.1: `main` (sin rama de feature); modo oscuro: `005-modo-oscuro` (creada con la extensión git de Spec Kit; la spec sigue en `002-mejoras-ui-usuarios`) | En curso. v1.1 implementada (42 de 43 tareas); pendiente: T042 (recorrido completo de `quickstart.md` a 360, 800 y 1280 px). Modo oscuro especificado; pendiente de plan, tareas, implementación y verificación. **Modifica** 001 (menú desplegable → menú lateral; el titular ya no se crea solo por comando). **Modificada por** 004 (se retira el enlace «Exportar» del menú lateral). El modo oscuro **amplía** 003 (segunda paleta del mismo sistema visual; el PDF sigue en claro) |
| [003](003-rediseno-visual/spec.md) | Rediseño visual y accesibilidad | Tokens de diseño, tipografía incluida, etiquetas de estado, PDF rediseñado, WCAG 2.1 AA | `main` (sin rama de feature) | Implementada (38 de 39 tareas). Pendiente: T038 (recorrido completo de `quickstart.md`, pruebas con 5 personas y revisión a 320–1280 px). **Modifica** solo la apariencia de 001 y 002 (sin cambios de lógica ni de datos). La 004 reutiliza su sistema visual sin modificarlo. **Ampliada por** 002 (paleta oscura, US7) |
| [004](004-exportar-zip/spec.md) | Exportar en un .zip | Botón «Exportar…» con ventana («Todo» o «Seleccionar qué exportar») que descarga un .zip solo con los PDF de los presupuestos ya descargados; solo lectura | `feature/004-exportar-zip` ([PR #2](https://github.com/contracamilo/presupuestos-pro/pull/2), fusionada en `main`) | Implementada (31 de 31 tareas, `quickstart.md` verificado). **Sustituye** en 001 la exportación en JSON (`GET /exportar`, FR-029) y **modifica** en 002 el menú lateral (se retira «Exportar»). El archivo de datos (JSON) se retiró del .zip (decisión D-004-1): no hay exportación de datos del negocio (propuesta P6) |

Según la constitución («Verificación de cada entrega»), una spec solo se da por terminada cuando se comprueba cada criterio en la app; las tareas pendientes son esa verificación final.

## Propuestas fuera de alcance

Ideas registradas que **no se construyen** hasta entrar en una spec: ver [`propuestas.md`](propuestas.md) (P1–P6).

## Cómo mantener este archivo

Al cerrar una spec o crear una nueva, actualizar la tabla (número, nombre, qué aporta, rama y estado). Si una spec sustituye o modifica algo de una anterior, anotarlo en el estado de **las dos** («Modifica» / «Modificada por»). Cada spec contiene su `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` y `tasks.md`.
