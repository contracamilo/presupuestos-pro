# Contrato: rutas HTTP de la aplicación

**Requisitos**: FR-001 a FR-042 | **Decisiones**: [research.md D1, D2, D7, D9](../research.md)

La aplicación genera páginas HTML en el servidor. Las rutas marcadas **(fragmento)** devuelven solo un trozo de HTML que HTMX sustituye en la página (D2). No hay API JSON pública salvo la exportación.

## Reglas comunes

| Regla | Detalle |
|---|---|
| Sesión obligatoria | Toda ruta excepto `GET/POST /entrar` y `/static/*` exige sesión válida (FR-034). Sin ella: página → redirección 303 a `/entrar`; fragmento → respuesta 401 con cabecera `HX-Redirect: /entrar`. |
| Solo titular | Rutas `/cuentas/*`: si el usuario es asistente → 403 (FR-035). |
| Origen | `POST`, `PUT`, `DELETE` con cabecera `Origin` distinta del dominio propio → 403 (D9). |
| Validación | Error de validación → 422 con el formulario o fragmento de nuevo, mostrando los mensajes en español junto a cada campo. |
| Cabeceras | En todas las respuestas: CSP solo propio dominio, HSTS, `frame-ancestors 'none'`, `X-Content-Type-Options: nosniff`. |
| Idioma | Todos los textos y mensajes en español de España (FR-030). |

## Sesión

| Método y ruta | Qué hace | Resultado |
|---|---|---|
| `GET /entrar` | Pantalla de inicio de sesión | HTML |
| `POST /entrar` | `email`, `contrasena`. Comprueba bloqueo y credenciales (FR-038) | Éxito → cookie de sesión + 303 a `/`. Fallo → 401 «Email o contraseña incorrectos». Bloqueado → 429 «Demasiados intentos. Vuelve a intentarlo en unos minutos.» |
| `POST /salir` | Cierra la sesión (FR-037) | Borra cookie y sesión → 303 a `/entrar` |
| `GET /mi-cuenta` · `POST /mi-cuenta/contrasena` | Cambiar la propia contraseña: `actual`, `nueva` (≥ 10) (FR-039) | Éxito → mensaje; cierra las demás sesiones del usuario |

## Presupuestos e historial

| Método y ruta | Qué hace |
|---|---|
| `GET /` | Historial: lista por fecha de emisión descendente con número, cliente, fecha y total; `?q=` filtra por número o nombre de cliente (FR-026) |
| `POST /presupuestos` | Crea presupuesto con número nuevo (D10) → 303 a su pantalla |
| `GET /presupuestos/{id}` | Pantalla de edición |
| `PUT /presupuestos/{id}` **(fragmento)** | Guarda un campo cambiado (fechas, tipo de IVA, notas, cliente) → devuelve cabecera, totales y mención recalculados |
| `POST /presupuestos/{id}/lineas` **(fragmento)** | Añade línea manual o desde `servicio_id` → devuelve líneas y totales |
| `PUT /presupuestos/{id}/lineas/{linea_id}` **(fragmento)** | Edita descripción, unidad, cantidad o precio → línea y totales |
| `POST /presupuestos/{id}/lineas/{linea_id}/mover` **(fragmento)** | `direccion=arriba|abajo` → líneas y totales |
| `DELETE /presupuestos/{id}/lineas/{linea_id}` **(fragmento)** | Elimina línea → líneas y totales |
| `GET /presupuestos/{id}/pdf` | Comprueba requisitos (FR-023). Si falta algo → 422 con la lista. Si no → congela emisor la primera vez (FR-018) y devuelve el PDF con `Content-Disposition: attachment; filename="PRE-AAAA-NNN_Cliente.pdf"`. Ver [pdf-presupuesto.md](./pdf-presupuesto.md) |
| `DELETE /presupuestos/{id}` | Borra tras confirmación en pantalla (FR-019) → 303 a `/` |

## Clientes

| Método y ruta | Qué hace |
|---|---|
| `GET /clientes` | Lista de activos, con buscador |
| `GET /clientes/buscar?q=` **(fragmento)** | Resultados por nombre o NIF, solo activos (FR-008) — usado también desde el presupuesto |
| `POST /clientes` | Alta. Con `presupuesto_id`, además lo selecciona en ese presupuesto y devuelve el fragmento del presupuesto sin perder líneas (FR-008, CA3) |
| `GET /clientes/{id}` · `PUT /clientes/{id}` | Ver y editar |
| `POST /clientes/{id}/archivar` | Archivar (CL11) |
| `POST /clientes/{id}/anonimizar` | Anonimizar tras confirmación en pantalla, irreversible (FR-043) → 303 a `/clientes`. Editar un cliente anonimizado → 409 |

## Catálogo

| Método y ruta | Qué hace |
|---|---|
| `GET /catalogo` | Lista de servicios activos |
| `POST /catalogo` · `PUT /catalogo/{id}` | Alta y edición |
| `POST /catalogo/{id}/archivar` | Archivar (CL11) |

## Perfil y ajustes

| Método y ruta | Qué hace |
|---|---|
| `GET /perfil` · `POST /perfil` | Ver y guardar perfil; valida obligatorios (FR-001) |
| `POST /perfil/logo` | Sube logo (multipart): PNG/JPG/SVG ≤ 2 MB por contenido real; si no → 422 «Formatos permitidos: PNG, JPG o SVG, hasta 2 MB» (FR-002) |
| `GET /logos/{id}` | Imagen del logo, con `Content-Security-Policy: script-src 'none'; sandbox` (D9) |
| `GET /ajustes` · `POST /ajustes` | Ver y guardar ajustes fiscales (FR-003) |

## Cuentas (solo titular)

| Método y ruta | Qué hace |
|---|---|
| `GET /cuentas` | Lista de cuentas (titular y asistentes, activos y dados de baja) |
| `POST /cuentas` | Alta de asistente: `nombre`, `email`, `contrasena` (≥ 10) (FR-035) |
| `POST /cuentas/{id}/baja` | Baja: `activo = 0` y borra sus sesiones. No permitido sobre el titular |
| `POST /cuentas/{id}/contrasena` | Asigna contraseña nueva al asistente y borra sus sesiones (FR-039) |

## Exportar

| Método y ruta | Qué hace |
|---|---|
| `GET /exportar` | Descarga el archivo de [archivo-exportacion.md](./archivo-exportacion.md) |
