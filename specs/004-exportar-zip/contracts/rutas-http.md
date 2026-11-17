# Contrato: rutas y ventana de exportación

**Requisitos**: FR-301 a FR-315 | **Decisiones**: [research.md](../research.md) E1–E3, E10 | **Base**: [rutas-http de la 001](../../001-presupuestos-pro/contracts/rutas-http.md)

Todas exigen sesión (titular o asistente), como el resto de la app.

## Cambios en rutas

| Antes (001) | Ahora |
|---|---|
| `GET /exportar` → archivo de datos (JSON) | **Retirada**: responde 405 («Esta acción no está permitida»), porque `/exportar` solo existe para `POST`. Sin redirección |
| — | `POST /exportar` → `.zip` |

El enlace «Exportar» del menú lateral desaparece. Se accede desde el historial.

## Historial (`GET /`)

- Botón **«Exportar…»** (secundario), junto a «Nuevo presupuesto». Abre la ventana (`<dialog>`); no descarga nada.
- La página incluye la ventana con los datos de la **lista de exportables** (orden del historial: fecha de emisión y número descendentes) y tres cifras: total de presupuestos, exportables y solo en datos.
- La búsqueda del historial no afecta a la ventana (que ofrece siempre todos los exportables).

## Ventana «Exportar»

| Estado | Contenido |
|---|---|
| **Sin presupuestos** (total = 0) | Solo el aviso «No hay presupuestos que exportar» y «Cerrar». Sin opciones ni «Descargar» (FR-309) |
| **Normal** | Botón **«Descargar .zip (N archivos)»**, con N = PDF + 1 archivo de datos, actualizado al instante («1 archivo» en singular). Opción **«Todo»** (marcada) con el texto de recuento (FR-310): «Se incluirán N PDF y el archivo de datos. Los X presupuestos sin PDF solo irán en el archivo de datos.» (la segunda frase solo si X > 0). Opción **«Seleccionar qué exportar»**. Botones «Cancelar» y «Descargar .zip» |
| **Sin exportables** (N = 0) | «Seleccionar» desactivada con el motivo «Aún no hay presupuestos descargados» |
| **«Seleccionar» elegida** | Lista con una casilla por presupuesto (número, cliente, etiqueta de estado), «Marcar todos», recuento «n marcados» y el aviso de copia parcial (FR-306b): «Esta copia solo incluye los presupuestos marcados; no sirve como copia de seguridad completa.» Con 0 marcados: «Descargar .zip» desactivado y texto «Marca al menos un presupuesto.» |
| **Preparando** | «Descargar .zip» desactivado con «Preparando la copia…» (`aria-busy`); resto de controles desactivados; la ventana no se cierra (ni «Cancelar», ni Esc, ni clic fuera) hasta terminar |
| **Error** | Mensaje en español en un `role="alert"` dentro de la ventana; la ventana sigue abierta y los controles se reactivan |

Accesibilidad (FR-301c, SC-310): foco atrapado y devuelto al botón «Exportar…», Esc y clic fuera cierran, controles con etiqueta, objetivos táctiles de 44 × 44 px, sin desplazamiento horizontal a 320 px (la lista se desplaza dentro de la ventana). Estilos solo con tokens de la 003.

## `POST /exportar`

**Cuerpo** (formulario):

| Campo | Valor |
|---|---|
| `modo` | `todo` o `seleccion` |
| `ids` | (repetido) identificadores de presupuesto; obligatorio con `seleccion`, ignorado con `todo` |

**Respuesta 200**: `Content-Type: application/zip`, `Content-Disposition: attachment; filename="…"` con el nombre de [archivo-exportacion.md](./archivo-exportacion.md). Cabecera `Cache-Control: no-store` (como el resto de páginas autenticadas).

**Errores** (JSON `{"error": "…"}`; la ventana los muestra):

| Caso | Estado | Mensaje |
|---|---|---|
| `modo` no válido | 422 | «Elige qué exportar.» |
| `seleccion` sin ids | 422 | «Marca al menos un presupuesto.» |
| algún id ya no es exportable | 409 | «La lista ha cambiado. Cierra la ventana y vuelve a abrirla.» |
| sin presupuestos | 422 | «No hay presupuestos que exportar.» |
| fallo al generar | 500 | «No se ha podido preparar la copia. Inténtalo de nuevo.» (no queda nada a medias: el zip se arma en memoria y solo se envía completo) |

**Garantías**: solo lectura (FR-305); lectura de un único instante (FR-312); un PDF por presupuesto exportable, idéntico a la descarga individual (FR-304); la exportación no fija emisor ni cambia estados.
