# Research: PresupuestosPro v1 (servidor propio)

**Fecha**: 2026-11-14 | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

Criterio que guía todas las decisiones (constitución, principio I y petición del usuario): **la opción más simple que cumpla la spec**. Cada decisión se explica primero en lenguaje de negocio y después con el detalle técnico mínimo.

Punto de partida fijado por el usuario: **backend en Python con FastAPI y SQLite**, una instalación por autónomo.

---

## D1. Una sola aplicación que hace todo

- **Decisión**: un único programa en Python (FastAPI) que muestra las pantallas, guarda los datos, comprueba quién entra y genera el PDF. No hay una aplicación de interfaz separada.
- **En lenguaje de negocio**: una sola pieza que instalar, actualizar y vigilar. Si algo falla, solo hay un sitio donde mirar. Un único lenguaje (Python) para todo el proyecto.
- **Alternativas descartadas**:
  - *Interfaz en React + API en FastAPI*: dos proyectos, dos lenguajes, dos procesos de construcción y la regla de cálculo duplicada (o una API extra solo para calcular). Más piezas sin beneficio para el usuario.
  - *Servicios separados (PDF, autenticación…)*: complejidad sin necesidad con 1–3 usuarios.

## D2. Pantallas generadas en el servidor + HTMX para el recálculo instantáneo

- **Decisión**: las páginas se generan en el servidor con plantillas Jinja2. Para que los totales se actualicen al instante sin recargar (FR-015), se usa **HTMX**: una pequeña librería (un único archivo, servido desde nuestro propio servidor) que, al cambiar una cantidad, envía el cambio y sustituye solo el trozo de página afectado.
- **En lenguaje de negocio**:
  - Cada cambio se **guarda en el servidor al momento**, así que el guardado automático (FR-017) sale gratis.
  - El cálculo de impuestos existe **una sola vez, en el servidor**. La pantalla y el PDF usan exactamente la misma función, por lo que no pueden discrepar (FR-025, SC-003).
  - No hay que construir ni empaquetar una aplicación de JavaScript.
- **Coste aceptado**: cada cambio hace un viaje al servidor (decenas de milisegundos). Para un formulario de presupuesto es imperceptible.
- **Alternativas descartadas**: *SPA con React* (D1); *JavaScript propio para recalcular en el navegador* (duplicaría la regla fiscal en dos lenguajes).

## D3. Base de datos: un único archivo SQLite, sin ORM

- **Decisión**: SQLite, con el módulo `sqlite3` de la librería estándar de Python y SQL escrito a mano en un módulo pequeño. Los logos se guardan **dentro** de la base de datos. El esquema está en un único `schema.sql` que se aplica al arrancar.
- **En lenguaje de negocio**:
  - **Todos los datos del autónomo caben en un solo archivo.** Hacer una copia de seguridad es copiar ese archivo, y restaurarla es ponerlo en su sitio (FR-041, FR-042).
  - Con 1–3 usuarios y cientos de presupuestos, SQLite va sobrado y no necesita un servidor de base de datos aparte que mantener.
- **Detalles**: modo WAL (permite leer mientras se escribe); claves foráneas activadas; versión del esquema en `PRAGMA user_version` para futuras migraciones.
- **Alternativas descartadas**: *PostgreSQL* (otro servicio que instalar, configurar y copiar); *SQLAlchemy/Alembic* (capas y herramientas que no aportan nada con ~10 tablas y SQL sencillo).

## D4. Cálculo de importes en céntimos enteros

- **Decisión**: importes en **céntimos enteros** (750,00 € = 75000); cantidades en **centésimas enteras** (1,5 h = 150); porcentajes enteros. Redondeo "mitad hacia arriba" (RN1–RN3) en tres puntos: importe de cada línea, cuota de IVA y retención.
- **En lenguaje de negocio**: los ordenadores cometen pequeños errores al operar con decimales. Trabajar en céntimos enteros los elimina y garantiza que todos los ejemplos de la spec cuadran al céntimo (SC-002).
- **Fórmulas**: ver [data-model.md](./data-model.md#cálculo-de-totales).
- **Alternativas descartadas**: *números decimales flotantes* (errores de redondeo); *`Decimal`* (válido, pero los enteros son más simples y suficientes para EUR con 2 decimales).

## D5. Regla fiscal en una sola función

- **Decisión**: una función pura recibe categoría, territorio, «NIF-IVA verificado», si el emisor aplica retención y el texto de Canarias, y devuelve si lleva IVA, si aplica retención y qué mención mostrar. Implementa literalmente la tabla RN6.
- **En lenguaje de negocio**: la regla vive en un único sitio, fácil de revisar con el asesor fiscal (supuesto de la spec) y de corregir si cambia la normativa.

## D6. PDF generado en el servidor con WeasyPrint

- **Decisión**: WeasyPrint convierte una plantilla HTML/CSS en PDF, dentro de nuestro servidor.
- **En lenguaje de negocio**:
  - El PDF se diseña con la misma tecnología que las pantallas, así que es fácil de ajustar.
  - Resuelve de serie lo que pide la spec: varias páginas con la cabecera de la tabla repetida y los totales al final (FR-024), logos PNG, JPG y SVG, tildes, «ñ» y €.
  - Ningún dato sale a un servicio externo de PDF (FR-028).
- **Seguridad**: WeasyPrint se configura para **no descargar nada de internet** (solo usa el logo que le pasamos), y no ejecuta código que pudiera venir dentro de un SVG.
- **Alternativas descartadas**: *ReportLab* (hay que posicionar los elementos a mano y el SVG necesita otra librería); *generar el PDF en el navegador* (duplicaría plantilla y cálculo); *servicio de PDF externo* (contradice FR-028).

## D7. Inicio de sesión: sesiones guardadas en el servidor

- **Decisión**:
  - Al iniciar sesión, el servidor crea una sesión con un identificador aleatorio largo y lo envía en una cookie protegida (`HttpOnly`, `Secure`, `SameSite=Lax`). En la base de datos se guarda solo una huella (hash) de ese identificador.
  - Cada petición comprueba la sesión y actualiza su "última actividad". Tras **8 horas sin actividad** caduca (FR-037).
  - Cerrar sesión o dar de baja a un asistente **borra sus sesiones**, así que pierde el acceso en su siguiente acción (FR-035).
  - Toda ruta, salvo la pantalla de inicio de sesión y los archivos estáticos, exige sesión (FR-034).
- **En lenguaje de negocio**: es el mecanismo clásico de "entrar con usuario y contraseña" de cualquier web seria. Al guardar las sesiones en el servidor, el titular puede **cortar el acceso de un asistente en el acto**.
- **Alternativas descartadas**: *tokens JWT* (no se pueden revocar al instante sin añadir una lista de revocación, que es lo mismo que una sesión en servidor pero más complejo); *servicio de autenticación externo* (fuera de alcance y contradice FR-028).

## D8. Contraseñas y bloqueo por intentos fallidos

- **Decisión**:
  - Las contraseñas se guardan con **Argon2id** (librería `argon2-cffi`), el método recomendado hoy por OWASP. Nunca se guardan ni se registran en claro (FR-036). Mínimo 10 caracteres.
  - Una tabla registra los intentos fallidos por email: al 5.º seguido, el email queda bloqueado 15 minutos (FR-038). El mensaje siempre es «Email o contraseña incorrectos».
- **En lenguaje de negocio**: aunque alguien robara la base de datos o una copia de seguridad, no podría leer las contraseñas. El bloqueo impide probar contraseñas a ciegas.
- **Alternativas descartadas**: *`hashlib.scrypt` de la librería estándar* (evita una dependencia, pero con los parámetros recomendados consume mucha memoria por cada inicio de sesión en un servidor pequeño); *bloqueo por IP* (más complejo y la spec lo pide por email).

## D9. Protección frente a ataques web habituales

- **Decisión** (todo configuración, sin servicios extra):
  - **Falsificación de peticiones (CSRF)**: cookie `SameSite=Lax` + comprobar que las peticiones que modifican datos vienen de nuestro propio dominio (cabecera `Origin`).
  - **Inyección de código (XSS)**: Jinja2 con escapado automático activado; nunca se marca como "seguro" texto escrito por el usuario.
  - **Política de seguridad de contenido (CSP)**: solo se permite cargar scripts, estilos e imágenes de nuestro propio servidor. HTMX se sirve en local, no desde un CDN.
  - **Logo SVG**: se muestra siempre como imagen (`<img>`), y la respuesta que lo entrega prohíbe ejecutar scripts.
  - **Subida de logo**: se comprueba el tipo real del archivo (no solo la extensión) y el tamaño (≤ 2 MB).
  - **SQL**: siempre con parámetros, nunca concatenando texto.
  - **Cabeceras**: HSTS (obliga a HTTPS), prohibición de mostrar la app dentro de otra web.
- **En lenguaje de negocio**: cubre las formas más comunes de atacar una web con datos personales, sin añadir piezas nuevas.

## D10. Numeración sin duplicados (FR-010, FR-033)

- **Decisión**: crear un presupuesto ocurre en una única transacción exclusiva de SQLite (`BEGIN IMMEDIATE`): leer el contador del año, sumar uno, guardar el contador y el presupuesto. SQLite solo permite una transacción de escritura a la vez, así que dos personas que creen un presupuesto en el mismo instante obtienen números distintos. Además, el número tiene una restricción de unicidad en la base de datos como red de seguridad.
- **En lenguaje de negocio**: aunque el titular y el asistente creen presupuestos a la vez desde equipos distintos, nunca se repite un número. Borrar un presupuesto no hace bajar el contador (RN7).
- **Año**: el de la fecha de creación (aclaración de la spec).

## D11. Varias personas editando lo mismo: gana el último guardado (FR-033)

- **Decisión**: cada cambio actualiza directamente el registro. No hay bloqueo ni aviso de conflicto.
- **En lenguaje de negocio**: es exactamente lo que pide la spec; añadir detección de conflictos sería complejidad que no se ha pedido.

## D12. Congelación de datos del emisor (RN9 / FR-018)

- **Decisión**: el presupuesto guarda `emisor_congelado` vacío hasta la primera descarga correcta del PDF. En ese momento copia el perfil (incluida la referencia al logo) y los ajustes de retención. El cliente nunca se copia: el presupuesto guarda solo qué cliente es y siempre lee sus datos actuales.
- **Logos inmutables**: cada logo subido es un registro nuevo que nunca se modifica. El perfil apunta al vigente; un presupuesto congelado, al que tenía al descargarse. Así el logo no se duplica en cada presupuesto.
- **Texto de mención de Canarias**: la spec solo congela perfil y retención, así que esa mención **no se congela** (principio III). Si se quiere congelar, se registra como propuesta.

## D13. Sin conexión o servidor caído

- **Decisión**: si un cambio no llega al servidor, HTMX muestra un aviso fijo «No se ha podido guardar. Comprueba tu conexión.» y la pantalla no da el cambio por guardado.
- **En lenguaje de negocio**: el usuario nunca cree que algo está guardado cuando no lo está (caso límite de la spec).

## D14. Exportar (FR-029)

- **Decisión**: un botón descarga un archivo `.json` con todos los datos de negocio (perfil, ajustes, logos, catálogo, clientes, presupuestos y contadores). **No incluye cuentas ni contraseñas.** No hay importación (la spec la eliminó).
- **En lenguaje de negocio**: el titular puede llevarse sus datos cuando quiera en un formato abierto, sin exponer las credenciales de nadie. Formato en [contracts/archivo-exportacion.md](./contracts/archivo-exportacion.md).

## D15. Dónde se instala: un servidor pequeño en la UE con Docker y Caddy

- **Decisión**:
  - Un **servidor virtual (VPS) pequeño en la UE** (p. ej. Hetzner, OVH o Scaleway; unos 4–6 €/mes).
  - **Docker Compose** con dos contenedores: la aplicación y **Caddy**, que se encarga del HTTPS y renueva el certificado solo.
  - El archivo SQLite vive en una carpeta del servidor fuera del contenedor, para que actualizar la app no lo toque.
- **En lenguaje de negocio**:
  - Cifrado obligatorio (FR-028) sin gestionar certificados a mano.
  - Servidores en la UE, como pide el supuesto de RGPD de la spec.
  - Instalar o actualizar es "descargar la versión nueva y reiniciar", y funciona igual en el portátil del desarrollador que en el servidor (WeasyPrint necesita librerías del sistema que Docker deja preinstaladas).
- **Por qué no Vercel**: Vercel ejecuta Python sin disco permanente, así que el archivo SQLite se perdería. Necesitamos un servidor con disco.
- **Alternativas descartadas**:
  - *Railway, Fly.io o Render con volumen*: válidos, pero añaden un proveedor más con su propia configuración y no simplifican las copias.
  - *Kubernetes, balanceadores, varias réplicas*: sobredimensionado para 1–3 usuarios; SQLite además necesita una sola instancia.
  - *Nginx + Certbot*: funciona, pero Caddy hace lo mismo con una configuración de tres líneas.

## D16. Copias de seguridad diarias fuera del servidor (FR-041, FR-042)

- **Decisión**:
  1. Cada noche, una tarea programada (cron del servidor) ejecuta `python -m presupuestos copia`, que hace una **copia consistente** de la base de datos (la función de copia en caliente de SQLite, segura aunque alguien esté trabajando) en una carpeta local.
  2. Justo después, **rclone** sube esa copia a un **almacenamiento de objetos en la UE de otro servicio** (p. ej. un bucket S3 compatible) y borra las copias de más de 30 días.
  3. Las credenciales del almacenamiento están en la configuración del servidor, nunca en el código (constitución, principio V).
  4. Restaurar: descargar la copia elegida, parar la app, sustituir el archivo y arrancar. Pasos escritos en la guía de administración.
- **En lenguaje de negocio**: si el servidor desaparece, se pierde como máximo un día de trabajo (SC-011). Como todo es un único archivo, la copia y la restauración son operaciones sencillas que puede seguir cualquier administrador.
- **Alternativas descartadas**: *Litestream* (replicación continua, pérdida casi nula, pero es otro proceso permanente que vigilar; la spec pide solo copia diaria); *copias solo en el mismo servidor* (no protegen si se pierde el servidor).

## D17. Administración desde la línea de comandos

- **Decisión**: tres órdenes para el administrador técnico, sin pantallas: `crear-titular`, `restablecer-titular` y `copia`. Ver [contracts/cli-administracion.md](./contracts/cli-administracion.md).
- **En lenguaje de negocio**: las tareas que hace el administrador una vez o casi nunca no necesitan pantallas, y así no existe ninguna puerta web para crear cuentas (FR-040).

## D18. Formato español y fechas

- **Decisión**: un formateador propio de pocas líneas para `1.234,56 €` y `DD/MM/AAAA`. Fechas guardadas como texto `AAAA-MM-DD` (sin hora) y validez calculada sumando días de calendario.
- **En lenguaje de negocio**: el mismo formato en pantalla y PDF (FR-030), sin desfases por zonas horarias y sin depender de la configuración regional del servidor.

## D19. Nombre del archivo PDF (FR-022)

- **Decisión**: quitar tildes (normalización Unicode), eliminar lo que no sea letra, número, espacio o guion, cambiar espacios por guiones y unir guiones repetidos. «Peña & Cía» → `Pena-Cia`.

## D20. Comprobación de calidad

- **Decisión**:
  1. **Comprobación en la app** (obligatoria, principio IV): [quickstart.md](./quickstart.md), con pasos escritos para personas no técnicas, salvo los marcados «(Técnico)» (administración del servidor y comprobaciones que dependen del reloj del sistema), según la excepción de la constitución v1.1.0.
  2. **Tests automáticos con pytest** solo donde un error es grave y fácil de no ver: reglas de cálculo y fiscales (todos los ejemplos de la spec), y control de acceso (ninguna ruta accesible sin sesión, bloqueo, baja de asistente, numeración sin duplicados).
- **Lo que NO se añade**: tests de navegador automatizados, integración continua ni despliegue automático. La spec no los pide.

---

## Puntos pendientes

Ninguno bloquea el plan. Recordatorios de la spec: revisar la tabla RN6 (en especial la retención en Canarias/Ceuta/Melilla) con un asesor fiscal, y firmar el contrato de encargado del tratamiento con el proveedor del servidor y con el del almacenamiento de copias.
