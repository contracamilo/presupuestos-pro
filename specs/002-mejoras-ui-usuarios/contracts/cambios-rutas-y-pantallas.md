# Contrato: cambios en rutas y archivo de exportación

**Requisitos**: FR-105 a FR-116 | **Decisiones**: [research.md R2, R4–R10](../research.md)

Contrato base: [rutas-http.md de la 001](../../001-presupuestos-pro/contracts/rutas-http.md). Las reglas comunes (sesión obligatoria, solo titular, origen, 422 con errores junto a cada campo, cabeceras, idioma) **no cambian**, salvo la lista de rutas públicas. Aquí solo figuran rutas nuevas, renombradas o con cambios.

## Reglas comunes — cambio

| Regla | Antes (001) | Ahora |
|---|---|---|
| Rutas sin sesión | `GET/POST /entrar`, `/static/*` | Además `GET/POST /crear-titular` (FR-108) |
| Solo titular | `/cuentas/*` | `/usuarios/*` |

## Sesión y primera puesta en marcha

| Método y ruta | Qué hace | Resultado |
|---|---|---|
| `GET /entrar` | **Cambia**: si no existe titular → 303 a `/crear-titular`. Con `?aviso=titular-existe` muestra «La cuenta del titular ya existe. Inicia sesión.» | HTML |
| `GET /crear-titular` **(nueva)** | Formulario: nombre, email, contraseña, repetir contraseña. Si ya existe titular → 303 a `/entrar` | HTML, sin menú ni datos del autónomo |
| `POST /crear-titular` **(nueva)** | Valida (nombre y email obligatorios, contraseña ≥ 10, repetición igual). Crea el titular y abre sesión | Éxito → cookie + 303 a `/`. Error de validación → 422 con mensajes por campo. Ya existe titular (antes o por envío simultáneo) → 303 a `/entrar?aviso=titular-existe` |
| `POST /mi-cuenta/contrasena` | **Cambia**: añade `repetir` | Si no coincide → 422 «Las contraseñas no coinciden.» junto al campo |

## Usuarios (solo titular) — antes «Cuentas»

| Método y ruta | Antes | Qué hace |
|---|---|---|
| `GET /usuarios` | `GET /cuentas` | Lista (nombre, email, tipo, Activa / Dada de baja) + bloque desplegable «Añadir usuario» |
| `POST /usuarios` | `POST /cuentas` | Alta de asistente: `nombre`, `email`, `contrasena`, `repetir`. Error → 422 con el bloque «Añadir usuario» abierto y mensajes por campo |
| `POST /usuarios/{id}/baja` | `POST /cuentas/{id}/baja` | Sin cambios de comportamiento (FR-035) |
| `POST /usuarios/{id}/contrasena` | `POST /cuentas/{id}/contrasena` | Añade `repetir`. Botón visible: «Restablecer contraseña» (FR-039) |

Las rutas `/cuentas*` desaparecen (404).

## Presupuestos e historial

| Método y ruta | Cambio |
|---|---|
| `GET /` (y su fragmento de búsqueda) | Los enlaces de cada presupuesto llevan `?volver=<q>` cuando hay búsqueda activa (R2) |
| `GET /presupuestos/{id}` | Acepta `?volver=<q>` opcional. Pinta «← Volver al historial» con `href="/?q=<q>"` o `href="/"` (FR-105) |
| `PUT /presupuestos/{id}` **(fragmento)** | `fecha_emision` y `fecha_validez` se aceptan como `AAAA-MM-DD` (calendario) o `DD/MM/AAAA` (respaldo). El fragmento de fechas devuelto incluye `min` actualizado en la validez (R9) |

## Clientes

| Método y ruta | Cambio |
|---|---|
| `POST /clientes` · `PUT /clientes/{id}` | Nuevo campo `tipo_documento` (`''`, `nif`, `cif`, `nie`, `nif_iva_ue`, `extranjero`). Tipo no permitido para categoría y territorio → 422 «Tipo de documento no válido para este cliente.» `pais` debe ser de la lista permitida para el territorio o igual al valor ya guardado → si no, 422 «Elige un país de la lista.» (R7, R8) |
| `POST /clientes/{id}/anonimizar` | También vacía `tipo_documento` |

## Perfil

| Método y ruta | Cambio |
|---|---|
| `POST /perfil/logo/quitar` **(nueva)** | Tras confirmación (`hx-confirm`): `perfil.logo_id = NULL` → vuelve a `/perfil` con «Logo quitado.» (FR-116, R10) |

## Tema (ampliación 2026-11-17)

| Método y ruta | Cambio |
|---|---|
| `POST /tema` **(nueva)** | Guarda la preferencia de tema en la cookie `tema`. Requiere sesión y origen propio. 204 si la envía `app.js`; 303 a la pantalla de origen sin JS; 422 con un valor desconocido. Detalle en [tema.md](./tema.md#ruta) (FR-117 a FR-122, R12, R15) |
| Todas las páginas completas (`base.html`) | Cargan `/static/tokens-oscuro.css` con `media` según el tema y ajustan `<meta name="color-scheme">` ([tema.md](./tema.md#cómo-se-pinta-cada-página-fr-123-fr-125-fr-126)) |

## Archivo de exportación

Sobre [archivo-exportacion.md de la 001](../../001-presupuestos-pro/contracts/archivo-exportacion.md):

- `"version": 2`.
- Cada elemento de `clientes` añade `"tipo_documento": "nif"` (o `""` si está sin indicar).
- El resto no cambia; sigue sin incluir cuentas.

## Órdenes de administración

Sobre [cli-administracion.md de la 001](../../001-presupuestos-pro/contracts/cli-administracion.md):

- **Se elimina** `python -m presupuestos crear-titular` (sustituida por `/crear-titular`).
- `restablecer-titular` y `copia` no cambian.
- `docs/administracion.md`: el paso de alta del titular pasa a ser «abre `https://tu-dominio` nada más arrancar y crea la cuenta del titular», con la advertencia del riesgo aceptado (spec, Supuestos).
