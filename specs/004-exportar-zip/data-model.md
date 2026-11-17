# Modelo de datos: PresupuestosPro v1.3 — Exportar en un .zip

**Plan**: [plan.md](./plan.md) | **Base**: [data-model.md de la 001](../001-presupuestos-pro/data-model.md)

## Cambios en el esquema

**Ninguno.** `PRAGMA user_version` sigue en 2; no hay columnas ni tablas nuevas, y la exportación no escribe nada (FR-305).

## Conceptos derivados (no se guardan)

| Concepto | Definición | Uso |
|---|---|---|
| **Descargado** | `presupuestos.emisor_congelado IS NOT NULL` | Primer filtro de «exportable» |
| **Exportable (con PDF)** | Descargado **y** `requisitos_descarga(...)` vacío (la descarga individual funcionaría hoy) | Lista de «Seleccionar»; PDF de «Todo»; recuento de la ventana |
| **Solo en datos** | Presupuesto no exportable (borrador, o descargado con requisito roto, p. ej. cliente anonimizado) | Aparece únicamente en el archivo de datos de «Todo» |
| **Selección** | Conjunto de identificadores marcados en la ventana | Existe en la petición; no se guarda |

## Contenido de la copia

| Elemento | «Todo» | «Seleccionar» |
|---|---|---|
| PDF | uno por presupuesto exportable | uno por presupuesto marcado |
| `perfil`, `ajustes` | sí | `null` |
| `servicios` (catálogo) | sí | `[]` |
| `contadores` | sí | `[]` |
| `clientes` | todos | solo los de los presupuestos marcados |
| `presupuestos` (con líneas) | todos, incluidos borradores | solo los marcados |
| `logos` | todos | solo los del emisor fijado de los marcados |
| `usuarios`, `sesiones`, `intentos_acceso` | nunca | nunca |

Estructura exacta: [contracts/archivo-exportacion.md](./contracts/archivo-exportacion.md).

## Reglas

- **Solo lectura**: ningún `UPDATE`/`INSERT`/`DELETE`; los borradores conservan `emisor_congelado = NULL` y su estado (SC-304).
- **Un instante**: todas las lecturas ocurren dentro de una misma transacción de lectura (research E4).
- **Nombres**: `PRE-AAAA-NNN - cliente.pdf`, únicos por el número (research E8).
