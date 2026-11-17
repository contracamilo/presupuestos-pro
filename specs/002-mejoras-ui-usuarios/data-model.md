# Data Model: PresupuestosPro v1.1 — cambios sobre v1

**Fecha**: 2026-11-14 | **Plan**: [plan.md](./plan.md) | **Decisiones**: [research.md](./research.md)

Modelo base y convenciones: [specs/001-presupuestos-pro/data-model.md](../001-presupuestos-pro/data-model.md). Este documento recoge **solo las diferencias**. Todas las demás tablas, reglas y el cálculo de totales quedan igual.

## Resumen de cambios

| Tabla | Cambio | Requisito |
|---|---|---|
| `clientes` | Nueva columna `tipo_documento` | FR-112, FR-114 |
| `clientes` | `pais` sigue siendo texto; cambian las reglas de qué valores acepta | FR-113, FR-114 |
| `perfil` | Sin cambio de columnas; nueva acción que pone `logo_id = NULL` | FR-116 |
| `usuarios` | Sin cambio de columnas; el titular se crea desde la web | FR-108, FR-109 |
| Base de datos | `user_version` pasa de 1 a 2 | SC-106 (R11) |

---

## `clientes` — cambios

| Columna | Tipo | Obligatorio | Notas |
|---|---|---|---|
| `tipo_documento` **(nueva)** | `''` \| `nif` \| `cif` \| `nie` \| `nif_iva_ue` \| `extranjero` | No | `''` = «Sin indicar». Por defecto `''` (clientes de v1 y altas sin elegir) |
| `nif` | texto | Ver regla 001 | Sin cambios en la columna; en pantalla se llama «Número de documento» |
| `pais` | texto | No | Sin cambios en la columna; ver reglas de país |

### Tipos de documento permitidos — `dominio/documento.py` (R7)

| `categoria` | `territorio` | Tipos permitidos (además de `''`) | Preseleccionado si está vacío o deja de ser válido |
|---|---|---|---|
| particular | peninsula / canarias | `nif`, `nie` | — (queda «Sin indicar») |
| empresa | peninsula / canarias | `nif`, `cif`, `nie` | — (queda «Sin indicar») |
| empresa | ue | `nif_iva_ue`, `extranjero` | `nif_iva_ue` |
| empresa | fuera_ue | `extranjero` | `extranjero` |

Etiquetas en pantalla: `nif` «NIF», `cif` «CIF», `nie` «NIE», `nif_iva_ue` «NIF-IVA UE», `extranjero` «Otro documento extranjero», `''` «Sin indicar».

Reglas:
- Al guardar, el servidor rechaza (422, mensaje junto al campo) un tipo fuera de los permitidos para la categoría y el territorio enviados.
- Si un cambio de categoría o territorio deja el tipo fuera de los permitidos, la pantalla vacía el selector (o aplica el preseleccionado) y el número escrito se conserva.
- `tipo_documento` no interviene en el tratamiento fiscal (RN6) ni en los requisitos de descarga (FR-023).
- **Anonimizar** (FR-043): además de lo que define la 001, `tipo_documento = ''`.

### Países permitidos — `dominio/paises.py` (R8)

| `territorio` | Valores aceptados en `pais` |
|---|---|
| peninsula / canarias | Solo `España` (se guarda siempre así) |
| ue | Un país de `PAISES_UE` distinto de España |
| fuera_ue | Un país de `PAISES` que no esté en `PAISES_UE` |

- Además, el servidor acepta el valor que el cliente **ya tenía guardado** aunque no esté en la lista (clientes de v1). En pantalla se muestra como «Revisar país: <texto>».
- Al cambiar el territorio, si el país guardado no es válido para el nuevo territorio, el selector se vacía (o pasa a `España` en territorios de España).

---

## `perfil` — acción nueva

- **Quitar logo** (FR-116): `logo_id = NULL`. La fila de `logos` se conserva (D12): los presupuestos ya descargados que la tienen en `emisor_congelado.logo_id` siguen mostrándola.

## `usuarios` — creación del titular

- El titular se crea con `POST /crear-titular` solo si no existe ninguno. El índice único `un_solo_titular` (ya existente) garantiza que nunca haya dos aunque lleguen dos envíos a la vez; el segundo recibe un error de integridad y se redirige a `/entrar`.
- Reglas de contraseña sin cambios (≥ 10, Argon2id). Se añade la comprobación de repetición, que no se guarda.

---

## Versión del esquema (R11)

| `user_version` | Situación | Acción al arrancar |
|---|---|---|
| 0 | Base de datos nueva | Aplica `schema.sql` completo (ya con `tipo_documento`) y deja `user_version = 2` |
| 1 | Instalación de v1 | En una transacción: `ALTER TABLE clientes ADD COLUMN tipo_documento …` y `user_version = 2` |
| 2 | Al día | Nada |

Ningún otro dato cambia: clientes, presupuestos, líneas, numeración y cuentas siguen igual (SC-106).

## Exportación

El archivo de exportación ([archivo-exportacion.md de la 001](../001-presupuestos-pro/contracts/archivo-exportacion.md)) añade el campo `tipo_documento` a cada cliente. Ver [contracts/cambios-rutas-y-pantallas.md](./contracts/cambios-rutas-y-pantallas.md). *(Nota: la spec 004 sustituyó después esta exportación en JSON por el .zip de PDF.)*

---

## Ampliación 2026-11-17: preferencia de tema (FR-121, R12)

**No cambia la base de datos**: ni tablas, ni columnas, ni `user_version` (sigue en 2). La preferencia vive solo en el navegador.

| Entidad | Dónde | Valores | Por defecto | Notas |
|---|---|---|---|---|
| Preferencia de tema | Cookie `tema` del navegador (por dispositivo) | `claro` \| `oscuro` \| `sistema` | `sistema` (sin cookie o valor desconocido) | 400 días; la escribe solo `POST /tema`. Detalle en [contracts/tema.md](./contracts/tema.md#cookie-tema-fr-121-fr-122) |

Reglas:
- **Tema calculado** de cada página = valor de la cookie si hay sesión y es válido; si no, `sistema` (FR-122, FR-124).
- **Prioridad** (FR-124): `claro` u `oscuro` mandan sobre la preferencia del dispositivo; `sistema` la sigue.
- No forma parte de presupuestos, clientes, catálogo, perfil, ajustes ni cuentas; no aparece en copias de seguridad ni en el .zip de la 004.
- Cerrar sesión no la borra; borrar los datos del navegador o usar una ventana privada sí (vuelve a `sistema`).
