# Estado del producto

Índice de las especificaciones de PresupuestosPro y de su estado. Las reglas que gobiernan todo el producto están en [`.specify/memory/constitution.md`](../.specify/memory/constitution.md).

## Especificaciones

| Spec | Alcance | Implementación | Pendiente para cerrar |
|---|---|---|---|
| [001 — PresupuestosPro v1](001-presupuestos-pro/spec.md) | Presupuestos, clientes, catálogo, reglas fiscales (IVA/IRPF), PDF, cuentas, exportación y copias | Implementada (67 de 69 tareas) | T063 (revisión responsive a 360 px / tableta / ordenador) y T066 (pytest en Docker y recorrido completo de `quickstart.md`) |
| [002 — Navegación, formularios y usuarios](002-mejoras-ui-usuarios/spec.md) | Menú lateral, «Volver al historial», alta del titular desde el navegador, selectores, calendarios, logo | Implementada (42 de 43 tareas) | T042 (recorrido completo de `quickstart.md` a 360, 800 y 1280 px) |
| [003 — Rediseño visual y accesibilidad](003-rediseno-visual/spec.md) | Tokens de diseño, tipografía incluida, etiquetas de estado, PDF rediseñado, WCAG 2.1 AA | Implementada (38 de 39 tareas) | T038 (recorrido completo de `quickstart.md`, pruebas con 5 personas y revisión a 320–1280 px) |
| [004 — Exportar en un .zip](004-exportar-zip/spec.md) | Ventana «Exportar…» (todo / selección), un .zip solo con los PDF (sin archivo de datos, decisión D-004-1), solo lectura | Implementada (31 de 31 tareas) | — |

Según la constitución («Verificación de cada entrega»), una spec solo se da por terminada cuando se comprueba cada criterio en la app; las tareas pendientes son esa verificación final.

## Propuestas fuera de alcance

Ideas registradas que **no se construyen** hasta entrar en una spec: ver [`propuestas.md`](propuestas.md) (P1–P5).

## Cómo mantener este archivo

Al cerrar una spec o crear una nueva, actualizar la tabla. Cada spec contiene su `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` y `tasks.md`.
