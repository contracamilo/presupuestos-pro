# Data Model: PresupuestosPro v1.2 — Rediseño visual

**Fecha**: 2026-11-14 | **Plan**: [plan.md](./plan.md) | **Decisiones**: [research.md](./research.md)

## Resumen: ningún cambio en los datos guardados

| Elemento | Cambio |
|---|---|
| Tablas, columnas, restricciones, índices | **Ninguno** (FR-215) |
| `PRAGMA user_version` | Sigue en **2** (002). No hay paso de actualización: una base de datos de v1.1 funciona tal cual (SC-208) |
| Archivo de exportación | Sin cambios (`"version": 2`) |
| Datos congelados del PDF (`emisor_congelado`) | Sin cambios; solo se **lee** para deducir el estado |

Modelo vigente: [001](../001-presupuestos-pro/data-model.md) + diferencias de la [002](../002-mejoras-ui-usuarios/data-model.md).

---

## Estado del presupuesto — dato deducido, no guardado (FR-209, V7)

Se calcula al mostrar cada presupuesto con `dominio/estado.py`. No existe como columna ni se escribe nunca.

### Entradas

| Entrada | Origen | Notas |
|---|---|---|
| `emisor_congelado` | `presupuestos.emisor_congelado` | No nulo ⇔ el PDF se descargó correctamente al menos una vez (FR-018 de la 001) |
| `fecha_validez` | `presupuestos.fecha_validez` | `AAAA-MM-DD`, siempre presente |
| `hoy` | `fechas.hoy()` | Fecha de hoy en Europe/Madrid (D18 de la 001) |

### Regla (en este orden; el primero que se cumple gana — Clarifications Q2)

| # | Condición | Estado |
|---|---|---|
| 1 | `fecha_validez < hoy` | `caducado` |
| 2 | `emisor_congelado` no es nulo | `enviado` |
| 3 | En cualquier otro caso | `borrador` |

- Validez = hoy → **no** caducado (pasa a estarlo mañana).
- Cada presupuesto tiene exactamente **un** estado.

### Transiciones (consecuencia de la regla, sin acciones nuevas)

```text
             primera descarga del PDF
  Borrador ───────────────────────────────▶ Enviado
     │                                         │
     │  pasa la fecha «Válido hasta»           │  pasa la fecha «Válido hasta»
     ▼                                         ▼
  Caducado ◀───────────────────────────────────┘
     │
     │  se cambia «Válido hasta» a hoy o una fecha futura
     ▼
  Enviado (si se descargó alguna vez) · Borrador (si no)
```

- Volver a descargar un presupuesto caducado **no** cambia su estado mostrado.
- Nada devuelve un presupuesto de Enviado a Borrador (la congelación no se deshace).

### Estados solo diseñados (FR-209a)

| Estado | En esta versión |
|---|---|
| `aceptado` | Etiqueta definida en el sistema visual; ninguna regla la devuelve |
| `rechazado` | Ídem |

Etiquetas, colores e iconos: [contracts/estados.md](./contracts/estados.md).
