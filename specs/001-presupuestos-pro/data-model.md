# Data Model: PresupuestosPro v1 (servidor propio)

**Fecha**: 2026-11-14 | **Plan**: [plan.md](./plan.md) | **Decisiones**: [research.md](./research.md)

Un único archivo SQLite por instalación (D3). Convenciones:

- **Importes**: céntimos enteros (`75000` = 750,00 €). **Cantidades**: centésimas enteras (`150` = 1,5). **Porcentajes**: enteros (`21`, `15`) (D4).
- **Fechas**: texto `AAAA-MM-DD`. **Marcas de tiempo**: texto ISO 8601 en UTC.
- **Identificadores**: enteros autoincrementales (no se exponen datos sensibles en ellos; toda ruta exige sesión).
- **Sí/no**: entero `0`/`1`.

## Resumen de tablas

| Tabla | Para qué | Registros |
|---|---|---|
| `perfil` | Datos del emisor | 1 fija |
| `ajustes` | Ajustes fiscales | 1 fija |
| `logos` | Imágenes de logo, inmutables (D12) | pocos |
| `servicios` | Catálogo | decenas |
| `clientes` | Clientes | decenas–cientos |
| `presupuestos` | Presupuestos | cientos |
| `lineas` | Líneas de cada presupuesto | miles |
| `contadores` | Último número por año | 1 por año |
| `usuarios` | Cuentas de titular y asistentes | 1–5 |
| `sesiones` | Sesiones abiertas | pocas |
| `intentos_acceso` | Intentos fallidos por email | pocos |

Las búsquedas (historial, clientes) usan `LIKE` sobre pocas columnas; con cientos de filas no hacen falta índices adicionales salvo los indicados.

---

## Datos de negocio

### `perfil` — FR-001 (una sola fila, `id = 1`)

| Columna | Tipo | Obligatorio | Notas |
|---|---|---|---|
| `nombre` | texto | Sí | Nombre o razón social |
| `nif` | texto | Sí | Sin validación de formato (supuesto) |
| `direccion` | texto | Sí | Multilínea |
| `email` | texto | Sí | |
| `telefono` | texto | No | |
| `logo_id` | → `logos.id` \| NULL | No | |

Validación al guardar: lista de obligatorios que faltan (HU1-1). Mientras falte alguno, el PDF no se genera (FR-023).

### `logos` — FR-002, D12

| Columna | Tipo | Notas |
|---|---|---|
| `id` | entero | |
| `tipo` | `image/png` \| `image/jpeg` \| `image/svg+xml` | Comprobado por contenido, no solo extensión (D9) |
| `datos` | BLOB | ≤ 2 MB |
| `creado_en` | marca de tiempo | |

Nunca se modifica ni se borra. Subir un logo crea una fila nueva y `perfil.logo_id` pasa a apuntarla.

### `ajustes` — FR-003 (una sola fila, `id = 1`)

| Columna | Tipo | Por defecto | Valores |
|---|---|---|---|
| `tipo_iva` | entero | 21 | 21, 10, 4, 0 |
| `retencion_activa` | 0/1 | 0 | |
| `tipo_retencion` | entero | 15 | 15, 7 |
| `dias_validez` | entero | 30 | ≥ 1 |
| `mencion_canarias` | texto | `''` | Libre |

### `servicios` — FR-004, FR-005

| Columna | Tipo | Obligatorio | Notas |
|---|---|---|---|
| `id` | entero | | |
| `nombre` | texto | Sí | |
| `descripcion` | texto | No | |
| `unidad` | `hora` \| `día` \| `proyecto` \| `unidad` | Sí | |
| `precio_cent` | entero ≥ 0 | Sí | Sin IVA; máx. 2 decimales al introducirlo |
| `archivado` | 0/1 | | 0 al crear |

"Borrar" = archivar (CL11). Archivado ⇒ no aparece en el selector de líneas. Las líneas no dependen del servicio.

### `clientes` — FR-006 a FR-009

| Columna | Tipo | Obligatorio | Notas |
|---|---|---|---|
| `id` | entero | | |
| `nombre` | texto | Sí | |
| `nif` | texto | Ver regla | NIF/NIE o NIF-IVA |
| `direccion`, `pais`, `email` | texto | No | |
| `categoria` | `empresa` \| `particular` | Sí | |
| `territorio` | `peninsula` \| `canarias` \| `ue` \| `fuera_ue` | Sí | |
| `nif_iva_verificado` | 0/1 | | Solo puede ser 1 si `territorio = 'ue'` |
| `archivado` | 0/1 | | 0 al crear |
| `anonimizado` | 0/1 | | 0 al crear; irreversible (FR-043) |

Reglas:
- **Anonimizar** (FR-043), tras confirmación: `nombre = 'Cliente eliminado'`, `nif`, `direccion`, `pais`, `email` vacíos, `anonimizado = 1`, `archivado = 1`. Se conservan `categoria`, `territorio` y `nif_iva_verificado` para que los importes no cambien. Un cliente anonimizado no se puede editar ni seleccionar.
- `particular` ⇒ `territorio ∈ {peninsula, canarias}` (FR-007); el formulario solo ofrece esos dos y el servidor lo vuelve a comprobar.
- NIF vacío permitido al guardar, pero si `empresa` y `territorio ∈ {peninsula, canarias}` bloquea el PDF (FR-023, CL13).
- Archivado ⇒ fuera de buscadores y listas; los presupuestos lo siguen mostrando (CL11).

### `presupuestos` — FR-010 a FR-019

| Columna | Tipo | Notas |
|---|---|---|
| `id` | entero | |
| `numero` | texto `PRE-AAAA-NNN`, **único** | Asignado al crear; nunca cambia (D10) |
| `fecha_creacion` | fecha | Año del número |
| `fecha_emision` | fecha | Hoy por defecto |
| `fecha_validez` | fecha | Emisión + `dias_validez` por defecto |
| `validez_editada_a_mano` | 0/1 | Si 0, cambiar la emisión recalcula la validez (FR-011) |
| `tipo_iva` | entero | 21, 10, 4, 0; inicial desde ajustes (FR-014) |
| `cliente_id` | → `clientes.id` \| NULL | Referencia, no copia (FR-018) |
| `notas` | texto | Opcional (FR-016) |
| `emisor_congelado` | texto JSON \| NULL | NULL = nunca descargado (D12) |
| `actualizado_en` | marca de tiempo | Gana el último guardado (D11) |

**`emisor_congelado`** (JSON), se rellena en la primera descarga correcta y no vuelve a cambiar:

```json
{ "nombre": "…", "nif": "…", "direccion": "…", "email": "…", "telefono": "…",
  "logo_id": 3, "retencion_activa": true, "tipo_retencion": 15 }
```

**Validación**: `fecha_validez ≥ fecha_emision` (FR-011). El presupuesto se guarda en cualquier estado (sin cliente, sin líneas…).

**Requisitos para descargar** (FR-023) — se comprueban todos y se listan los que fallan:
1. Perfil efectivo (congelado o actual) con nombre, NIF, dirección y email.
2. Cliente seleccionado.
3. Al menos una línea.
4. Cliente empresa en `peninsula` o `canarias` ⇒ NIF no vacío.
5. Cliente no anonimizado (FR-043).

**Transición** (no hay estados de negocio):

```text
[nunca descargado: emisor_congelado = NULL] --primera descarga correcta--> [descargado: emisor_congelado fijo]
```

Ambos permiten editar todo lo demás y volver a descargar con el mismo número (FR-017).

**Borrado** (FR-019): tras confirmar, se borra el presupuesto y sus líneas. El contador no cambia.

### `lineas` — FR-012, FR-013

| Columna | Tipo | Notas |
|---|---|---|
| `id` | entero | |
| `presupuesto_id` | → `presupuestos.id` | Borrado en cascada |
| `posicion` | entero | Orden de presentación |
| `descripcion` | texto | Obligatoria |
| `unidad` | texto \| NULL | Opcional en líneas manuales |
| `cantidad_cent` | entero > 0 | `1000` = 10; `150` = 1,5 |
| `precio_cent` | entero ≥ 0 | |

- El **importe no se guarda**: se calcula siempre (D4).
- Una línea del catálogo copia nombre del servicio, unidad y precio; no guarda vínculo con el servicio (CA4, CA15).
- Validación (FR-013): cantidad > 0, precio ≥ 0, máximo 2 decimales; si no, mensaje y no se guarda.

### `contadores` — FR-010, RN7

| Columna | Tipo | Notas |
|---|---|---|
| `anio` | entero, clave | |
| `ultimo` | entero | Solo aumenta |

**Asignación** en una transacción `BEGIN IMMEDIATE` (D10): `ultimo = (fila.ultimo o 0) + 1` → guardar contador → insertar presupuesto con `PRE-{anio}-{ultimo:03d}`.

> Si un año supera 999 presupuestos, el número sigue creciendo con más dígitos (`PRE-2026-1000`). La spec no contempla ese caso; no se añade lógica extra.

---

## Cuentas y acceso

### `usuarios` — FR-034 a FR-040

| Columna | Tipo | Notas |
|---|---|---|
| `id` | entero | |
| `nombre` | texto | |
| `email` | texto, **único** (sin distinguir mayúsculas) | Se guarda en minúsculas |
| `hash_contrasena` | texto | Argon2id; nunca la contraseña (FR-036) |
| `tipo` | `titular` \| `asistente` | |
| `activo` | 0/1 | 0 = dado de baja |
| `creado_en` | marca de tiempo | |

Reglas:
- Exactamente **un** titular (lo crea `crear-titular`, FR-040); el titular no puede darse de baja.
- Solo el titular da de alta, da de baja y asigna contraseña a asistentes (FR-035, FR-039).
- Contraseña de al menos 10 caracteres (FR-036).
- Email repetido ⇒ rechazo con mensaje.
- Dar de baja ⇒ `activo = 0` y se borran sus `sesiones`. Sus presupuestos se conservan (no hay autoría guardada; la spec no la pide).
- Cambiar o restablecer contraseña ⇒ se borran las demás sesiones de ese usuario.

### `sesiones` — FR-037, D7

| Columna | Tipo | Notas |
|---|---|---|
| `hash_token` | texto, clave | SHA-256 del identificador de la cookie |
| `usuario_id` | → `usuarios.id` | Borrado en cascada |
| `creada_en` | marca de tiempo | |
| `ultima_actividad` | marca de tiempo | Se actualiza en cada petición |

Válida si existe, su usuario está activo y `ahora − ultima_actividad < 8 h`. Cerrar sesión o caducar ⇒ se borra.

### `intentos_acceso` — FR-038

| Columna | Tipo | Notas |
|---|---|---|
| `email` | texto, clave | En minúsculas; también para emails que no existen |
| `fallos` | entero | Fallos seguidos |
| `bloqueado_hasta` | marca de tiempo \| NULL | |

Al fallar: `fallos + 1`; si llega a 5 ⇒ `bloqueado_hasta = ahora + 15 min` y `fallos = 0`. Mientras esté bloqueado se rechaza incluso con la contraseña correcta. Al entrar con éxito se borra la fila.

---

## Cálculo de totales

Función pura única, usada por la pantalla y por el PDF (D4, FR-025).

**Entradas**: líneas, `tipo_iva` del presupuesto, cliente actual, ajustes de retención efectivos (congelados si existen, si no los actuales) y `mencion_canarias` actual.

**Tratamiento por tipo de cliente** (RN6, D5):

| `categoria` | `territorio` | `nif_iva_verificado` | lleva IVA | admite retención | mención |
|---|---|---|---|---|---|
| empresa | peninsula | — | sí | sí | — |
| particular | peninsula / canarias | — | sí | no | — |
| empresa | ue | 1 | no | no | «Inversión del sujeto pasivo» |
| empresa | ue | 0 | sí | no | — |
| empresa | fuera_ue | — | no | no | «Operación no sujeta — Art. 69.Uno.1.º Ley 37/1992» |
| empresa | canarias | — | no | sí | `mencion_canarias` (ninguna si vacía) |

`aplica_retencion = admite_retencion and retencion_activa`. Sin cliente seleccionado (FR-044): se calcula como empresa en `peninsula` (IVA del presupuesto y retención si el emisor la aplica), sin mención, y la pantalla muestra «Totales provisionales: elige un cliente». El PDF igualmente exige cliente.

**Cálculo** (`redondeo` = mitad hacia arriba, en enteros):

```text
importe(línea) = redondeo(cantidad_cent × precio_cent / 100)
base           = Σ importe(línea)
iva            = lleva_iva        ? redondeo(base × tipo_iva / 100)        : 0
retencion      = aplica_retencion ? redondeo(base × tipo_retencion / 100)  : 0
total          = base + iva − retencion
```

**Ejemplos obligatorios** (SC-002), con retención activa al 15 % e IVA 21 %:

| Caso | Líneas | Base | IVA | Retención | Total |
|---|---|---|---|---|---|
| CA6 empresa península | 10×45,00 + 1×300,00 | 750,00 | 157,50 | −112,50 | 795,00 |
| CA7 particular | ídem | 750,00 | 157,50 | — | 907,50 |
| CA8 UE verificado | ídem | 750,00 | 0,00 | — | 750,00 |
| CL3 fuera UE | ídem | 750,00 | 0,00 | — | 750,00 |
| CL4 Canarias empresa | ídem | 750,00 | 0,00 | −112,50 | 637,50 |
| CA9 cantidad 12 | 12×45,00 + 1×300,00 | 840,00 | 176,40 | −126,00 | 890,40 |
| Ref. 15 % | 1.500,00 + 500,00 | 2.000,00 | 420,00 | −300,00 | 2.120,00 |
| Ref. 7 % | ídem | 2.000,00 | 420,00 | −140,00 | 2.280,00 |
| Ref. particular | ídem | 2.000,00 | 420,00 | — | 2.420,00 |
| CL7 decimal | 1,5×45,00 | 67,50 | — | — | — |
