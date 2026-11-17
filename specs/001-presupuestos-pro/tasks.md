---

description: "Lista de tareas de implementación de PresupuestosPro v1"
---

# Tasks: PresupuestosPro v1

**Input**: Design documents from `/specs/001-presupuestos-pro/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: el plan (research.md D20) fija tests automáticos con pytest **solo** para reglas de cálculo y fiscales y para control de acceso, numeración y copia. El resto se verifica en la app con [quickstart.md](./quickstart.md) (constitución, principio IV).

**Organization**: tareas agrupadas por historia de usuario. Las fases siguen la prioridad de la spec, con un ajuste por dependencias: la Historia 3 (perfil y ajustes, P2) va antes que la Historia 2 (PDF, P1) porque el PDF exige un perfil completo.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede hacer en paralelo (archivos distintos, sin depender de tareas pendientes)
- **[Story]**: historia de usuario de la spec (US1…US9)

## Path Conventions

Proyecto Python único en la raíz del repositorio: `presupuestos/` (aplicación), `tests/`, `docs/`. Ver la estructura en [plan.md](./plan.md#source-code-repository-root).

## Reglas para todas las tareas

- Todos los textos visibles (pantallas, mensajes, PDF, órdenes de administración) en **español de España** (FR-030).
- Importes en **céntimos enteros**, cantidades en **centésimas enteras**, porcentajes enteros (research.md D4). Nunca `float` para dinero.
- SQL **siempre con parámetros**, nunca concatenando texto (D9).
- Jinja2 con **escapado automático**; prohibido `|safe` o `Markup` sobre texto del usuario (D9).
- Sin scripts ni estilos en línea ni recursos externos (CSP de D9): todo JS en `presupuestos/static/`.
- Nada que no esté en la spec (constitución, principio III).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: crear el proyecto y la infraestructura de ejecución

- [X] T001 Crear la estructura de carpetas del plan: `presupuestos/` con `dominio/`, `rutas/`, `templates/`, `templates/fragmentos/`, `static/`; `tests/dominio/`; `docs/`; con `__init__.py` vacíos en `presupuestos/`, `presupuestos/dominio/` y `presupuestos/rutas/`
- [X] T002 Crear `pyproject.toml`: Python `>=3.12`; dependencias `fastapi`, `uvicorn[standard]`, `jinja2`, `weasyprint`, `argon2-cffi`, `python-multipart`; dependencias de desarrollo `pytest` y `httpx`; configuración de pytest con `testpaths = ["tests"]`
- [X] T003 [P] Crear `Dockerfile`: imagen `python:3.12-slim`; instalar las librerías del sistema que necesita WeasyPrint (`libpango-1.0-0`, `libpangoft2-1.0-0`, `libharfbuzz0b`, `libffi8`, `shared-mime-info`) y la fuente `fonts-dejavu-core` (tildes, «ñ» y €); instalar el proyecto con sus dependencias de desarrollo; usuario sin privilegios; `CMD uvicorn presupuestos.app:app --host 0.0.0.0 --port 8000 --workers 1 --proxy-headers` (una sola instancia por SQLite, D15)
- [X] T004 [P] Crear `docker-compose.yml` con dos servicios: `app` (build local, `env_file: .env`, volúmenes `./datos:/datos` y `./copias:/copias`, `restart: unless-stopped`, sin publicar puertos) y `caddy` (imagen `caddy:2`, puertos `80` y `443`, monta `./Caddyfile` y un volumen `caddy_data`, `restart: unless-stopped`)
- [X] T005 [P] Crear `Caddyfile`: sitio `{$DOMINIO}` con `reverse_proxy app:8000`. Con `DOMINIO=localhost`, Caddy usa su certificado local (quickstart §1)
- [X] T006 [P] Crear `.env.example` con `DOMINIO=localhost`, `RUTA_BD=/datos/presupuestos.db`, `COOKIE_SEGURA=1` y comentarios en español; crear `.gitignore` con `.env`, `datos/`, `copias/`, `__pycache__/`, `.pytest_cache/` (constitución, principio V)
- [X] T007 [P] Descargar HTMX 2.0.4 (`htmx.min.js`) y guardarlo en `presupuestos/static/htmx.min.js` (se sirve desde nuestro dominio, nunca desde un CDN; FR-028, D9)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: base de datos, reglas de negocio puras, sesión y esqueleto web que necesitan todas las historias

**⚠️ CRITICAL**: ninguna historia puede empezar hasta terminar esta fase

### Base de datos

- [X] T008 Crear `presupuestos/schema.sql` con todas las tablas de [data-model.md](./data-model.md), usando `CREATE TABLE IF NOT EXISTS`:
  - `perfil` (`id INTEGER PRIMARY KEY CHECK (id = 1)`, `nombre`, `nif`, `direccion`, `email`, `telefono`, `logo_id` → `logos.id`);
  - `logos` (`id`, `tipo CHECK (tipo IN ('image/png','image/jpeg','image/svg+xml'))`, `datos BLOB NOT NULL`, `creado_en`);
  - `ajustes` (`id CHECK (id = 1)`, `tipo_iva INTEGER NOT NULL DEFAULT 21 CHECK (tipo_iva IN (21,10,4,0))`, `retencion_activa INTEGER NOT NULL DEFAULT 0`, `tipo_retencion INTEGER NOT NULL DEFAULT 15 CHECK (tipo_retencion IN (15,7))`, `dias_validez INTEGER NOT NULL DEFAULT 30 CHECK (dias_validez >= 1)`, `mencion_canarias TEXT NOT NULL DEFAULT ''`) más `INSERT OR IGNORE` de la fila `id = 1`;
  - `servicios` (`unidad CHECK (unidad IN ('hora','día','proyecto','unidad'))`, `precio_cent INTEGER NOT NULL CHECK (precio_cent >= 0)`, `archivado INTEGER NOT NULL DEFAULT 0`);
  - `clientes` (`categoria CHECK (categoria IN ('empresa','particular'))`, `territorio CHECK (territorio IN ('peninsula','canarias','ue','fuera_ue'))`, `nif_iva_verificado`, `archivado`, `anonimizado`, todos `INTEGER NOT NULL DEFAULT 0`; `CHECK (categoria = 'empresa' OR territorio IN ('peninsula','canarias'))`; `CHECK (nif_iva_verificado = 0 OR territorio = 'ue')`);
  - `presupuestos` (`numero TEXT NOT NULL UNIQUE`, fechas `TEXT` `AAAA-MM-DD`, `validez_editada_a_mano`, `tipo_iva CHECK (tipo_iva IN (21,10,4,0))`, `cliente_id` → `clientes.id` NULL, `notas TEXT NOT NULL DEFAULT ''`, `emisor_congelado TEXT` NULL, `actualizado_en`, `CHECK (fecha_validez >= fecha_emision)`);
  - `lineas` (`presupuesto_id` → `presupuestos.id ON DELETE CASCADE`, `posicion`, `descripcion TEXT NOT NULL`, `unidad` NULL, `cantidad_cent INTEGER NOT NULL CHECK (cantidad_cent > 0)`, `precio_cent INTEGER NOT NULL CHECK (precio_cent >= 0)`);
  - `contadores` (`anio INTEGER PRIMARY KEY`, `ultimo INTEGER NOT NULL`);
  - `usuarios` (`email TEXT NOT NULL UNIQUE COLLATE NOCASE`, `hash_contrasena`, `tipo CHECK (tipo IN ('titular','asistente'))`, `activo INTEGER NOT NULL DEFAULT 1`, `creado_en`) más el índice único parcial `CREATE UNIQUE INDEX ... ON usuarios(tipo) WHERE tipo = 'titular'` (exactamente un titular);
  - `sesiones` (`hash_token TEXT PRIMARY KEY`, `usuario_id` → `usuarios.id ON DELETE CASCADE`, `creada_en`, `ultima_actividad`);
  - `intentos_acceso` (`email TEXT PRIMARY KEY`, `fallos INTEGER NOT NULL DEFAULT 0`, `bloqueado_hasta` NULL);
  - al final, `PRAGMA user_version = 1`.
- [X] T009 Crear `presupuestos/db.py`:
  - `conectar()` lee `RUTA_BD` del entorno y activa `PRAGMA journal_mode=WAL`, `PRAGMA foreign_keys=ON`, `busy_timeout=5000` y `row_factory=sqlite3.Row`;
  - `inicializar()` ejecuta `schema.sql` si `user_version = 0`;
  - context manager `transaccion_exclusiva(conn)` con `BEGIN IMMEDIATE` / `COMMIT` / `ROLLBACK`;
  - dependencia de FastAPI `get_db()` (una conexión por petición, cerrada al terminar);
  - `ahora_utc()` devuelve texto ISO 8601 en UTC.

### Reglas de negocio puras (`presupuestos/dominio/`)

- [X] T010 [P] Crear `presupuestos/dominio/formato.py`:
  - `euros(cent)`: `1.234,56 €` con separador de miles siempre (también con 4 cifras, D18) y signo «−» (U+2212) para negativos;
  - `cantidad(cent_centesimas)`: `10`, `1,5`, `1,25` (sin ceros decimales sobrantes);
  - `porcentaje(n)`: `21 %`;
  - `leer_importe(texto)`: acepta `1500`, `1500,5`, `1.500,50` (punto = miles, coma = decimal) y devuelve céntimos o lanza `ValueError` con mensaje en español si hay más de 2 decimales, signo negativo o texto no numérico;
  - `leer_cantidad(texto)`: igual que `leer_importe`, pero devuelve centésimas.
- [X] T011 [P] Crear `presupuestos/dominio/fechas.py`: `hoy()` en zona `Europe/Madrid` (`zoneinfo`); `sumar_dias(fecha_iso, dias)`; `a_dmy("2026-12-13") → "13/12/2026"`; `de_iso`/`a_iso`. Fechas sin hora (RN8, D18)
- [X] T012 [P] Crear `presupuestos/dominio/nombre_archivo.py`: `nombre_pdf(numero, nombre_cliente)` normaliza con NFD, quita tildes, elimina todo lo que no sea `[A-Za-z0-9 -]`, cambia espacios por guiones, une guiones repetidos y quita guiones de los extremos. Ejemplos: «Acme SL» → `PRE-2026-015_Acme-SL.pdf`, «Peña & Cía» → `…_Pena-Cia.pdf` (FR-022, D19)
- [X] T013 [P] Crear `presupuestos/dominio/tratamiento.py`: `tratamiento(categoria, territorio, nif_iva_verificado, retencion_activa, mencion_canarias) -> (lleva_iva, aplica_retencion, mencion)`, que implementa literalmente la tabla RN6 de [data-model.md](./data-model.md#cálculo-de-totales), con los textos exactos «Inversión del sujeto pasivo» y «Operación no sujeta — Art. 69.Uno.1.º Ley 37/1992». Para Canarias con `mencion_canarias` vacía, `mencion = None`
- [X] T014 [P] Crear `presupuestos/dominio/calculo.py`:
  - `redondeo(numerador, denominador)` mitad hacia arriba con enteros;
  - `calcular(lineas, tipo_iva, cliente|None, retencion_activa, tipo_retencion, mencion_canarias)` devuelve un objeto con `importes_linea`, `base`, `tipo_iva`, `iva`, `aplica_retencion`, `tipo_retencion`, `retencion`, `total`, `mencion` y `provisional`;
  - fórmulas exactas de data-model.md;
  - sin cliente, calcula como `empresa`/`peninsula`, sin mención y con `provisional=True` (FR-044).
- [X] T015 [P] Crear `presupuestos/dominio/validacion.py`:
  - `faltan_perfil(perfil) -> list[str]` (nombre, NIF, dirección, email obligatorios; FR-001);
  - `requisitos_descarga(perfil_efectivo, cliente, lineas) -> list[str]`, con los mensajes exactos de [contracts/pdf-presupuesto.md](./contracts/pdf-presupuesto.md): perfil incompleto (nombra el campo), sin cliente, sin líneas, empresa en `peninsula`/`canarias` sin NIF y cliente anonimizado (FR-023, FR-043);
  - `validar_cliente(datos) -> list[str]` (nombre obligatorio; `particular` solo en `peninsula`/`canarias`, FR-007; `nif_iva_verificado` solo si `ue`).
- [X] T016 [P] Crear `tests/dominio/test_calculo.py` con **todas** las filas de la tabla «Ejemplos obligatorios» de data-model.md (CA6, CA7, CA8, CL3, CL4, CA9, referencia 15 %, 7 % y particular, CL7), más CL6 (línea a 0,00 €), CL5 (IVA 10 %: 75,00 / 712,50) y FR-044 (sin cliente: 795,00, `provisional=True`)
- [X] T017 [P] Crear `tests/dominio/test_tratamiento.py` con las 6 filas de RN6, más UE sin verificar (CL1) y Canarias con y sin texto de mención
- [X] T018 [P] Crear `tests/dominio/test_formato_fechas_nombre.py`: `euros(123456) == "1.234,56 €"`, `euros(75000) == "750,00 €"`, `euros(-11250) == "−112,50 €"`; `leer_importe` válido e inválido (`10,555`, `-1`, `abc`); `sumar_dias("2026-11-13", 30) == "2026-12-13"`; `a_dmy`; los dos ejemplos de nombre de PDF
- [X] T019 [P] Crear `tests/dominio/test_validacion.py`: cada mensaje de `requisitos_descarga` (CA2, CA13, CL13, cliente anonimizado) y las reglas de `validar_cliente`

### Sesión, seguridad y esqueleto web

- [X] T020 Crear `presupuestos/seguridad.py`:
  - `hash_contrasena`/`verificar_contrasena` con `argon2.PasswordHasher()` (Argon2id);
  - `validar_longitud(contrasena)`: mínimo 10 caracteres, mensaje «La contraseña debe tener al menos 10 caracteres» (FR-036);
  - `crear_sesion(conn, usuario_id) -> token` con `secrets.token_urlsafe(32)`, guardando solo `sha256(token)`;
  - `usuario_de_sesion(conn, token)`: `None` si no existe, el usuario está inactivo o `ahora − ultima_actividad ≥ 8 h` (borra la sesión caducada); si es válida, actualiza `ultima_actividad` (FR-037);
  - `borrar_sesion(conn, token)` y `borrar_sesiones_usuario(conn, usuario_id, excepto=None)`.
- [X] T021 Crear `presupuestos/app.py`:
  - crea la app FastAPI, monta `/static`, configura `Jinja2Templates` sobre `presupuestos/templates` con autoescape, registra filtros `euros`, `cantidad`, `fecha` (de `dominio/`) y llama a `db.inicializar()` al arrancar;
  - middleware de cabeceras en todas las respuestas: `Content-Security-Policy: default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'`, `Strict-Transport-Security: max-age=31536000`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`;
  - `Cache-Control: no-store` en todas las respuestas salvo `/static/` (FR-037, US8 AS8: tras cerrar sesión, «Atrás» no muestra datos);
  - middleware de origen: `POST/PUT/DELETE` con `Origin` presente y distinto del host → 403 (D9);
  - dependencia `usuario_actual` que lee la cookie `sesion`: sin sesión válida → 303 a `/entrar`, o 401 con cabecera `HX-Redirect: /entrar` si la petición trae `HX-Request` (FR-034);
  - dependencia `solo_titular` → 403;
  - páginas de error 403/404/422 en español;
  - registra los routers de `presupuestos/rutas/`.
- [X] T022 [P] Crear `presupuestos/templates/base.html`:
  - `<meta name="viewport">`, `<meta name="htmx-config" content='{"includeIndicatorStyles": false}'>` (compatible con la CSP), `htmx.min.js`, `app.js` y `estilos.css`;
  - menú: Historial, Clientes, Catálogo, Perfil, Ajustes, Mi cuenta, Cuentas (solo si `usuario.tipo == 'titular'`), Exportar y botón Salir (formulario POST);
  - zona `#aviso-conexion` oculta.
- [X] T023 [P] Crear `presupuestos/static/app.js`: escucha `htmx:sendError` y `htmx:responseError` (estado ≥ 500 o 0) y muestra en `#aviso-conexion` «No se ha podido guardar. Comprueba tu conexión.»; lo oculta en el siguiente `htmx:afterRequest` correcto (D13). Sin dependencias
- [X] T024 [P] Crear `presupuestos/static/estilos.css`: estilos base adaptables desde 360 px, sin desplazamiento horizontal (`max-width: 100%`, tablas de líneas que en móvil pasan a tarjetas, menú plegable con `<details>`), formularios a una columna en móvil (FR-031)
- [X] T025 Crear `presupuestos/rutas/sesion.py` y `presupuestos/templates/entrar.html`:
  - `GET /entrar`;
  - `POST /entrar` (`email` en minúsculas, `contrasena`): si es correcto, crea sesión, pone la cookie `sesion` (`HttpOnly`, `SameSite=Lax`, `Secure` si `COOKIE_SEGURA=1`, `Path=/`) y redirige 303 a `/`; si falla, 401 con «Email o contraseña incorrectos»;
  - `POST /salir` borra la sesión y la cookie y redirige 303 a `/entrar`;
  - según [contracts/rutas-http.md](./contracts/rutas-http.md#sesión). El bloqueo por intentos llega en US8.
- [X] T026 Crear `presupuestos/__main__.py` con `argparse` y la orden `crear-titular --nombre --email`: pide la contraseña dos veces con `getpass`, valida 10 caracteres y que coincidan, y falla con «Ya existe una cuenta de titular» si ya hay uno ([contracts/cli-administracion.md](./contracts/cli-administracion.md#crear-titular--fr-040)). Nunca imprime la contraseña
- [X] T027 Crear `tests/conftest.py`: fixture que apunta `RUTA_BD` a un archivo temporal, inicializa la BD y crea un `TestClient`; helpers `crear_usuario(tipo, email, contrasena)` y `entrar(cliente, email, contrasena)`
- [X] T028 Crear `tests/test_acceso.py` con el test base de FR-034/SC-010: recorre `app.routes` y comprueba que toda ruta, salvo `/entrar` y `/static`, responde 303 a `/entrar` sin cookie, y 401 con `HX-Redirect` si lleva `HX-Request`

**Checkpoint**: la app arranca con `docker compose up`, se crea el titular, se entra (de momento `/` puede ser una página vacía con el menú; T035b la completa) y se sale; los tests de dominio y acceso pasan

---

## Phase 3: User Story 1 - Crear un presupuesto con cálculo correcto de impuestos (Priority: P1) 🎯 MVP

**Goal**: crear un presupuesto, elegir o dar de alta un cliente, añadir y editar líneas, y ver base, IVA, retención, mención y total recalculados al instante.

**Independent Test**: quickstart C0–C17 y D1–D3. Con ajustes por defecto, activar la retención al 15 % directamente en la fila `ajustes` si aún no existe la pantalla de Ajustes (US3). Los totales deben cuadrar con la tabla de ejemplos de data-model.md.

- [X] T029 [US1] Añadir a `presupuestos/db.py` la función `crear_presupuesto(conn, hoy)`, dentro de `transaccion_exclusiva`:
  - leer `contadores` del año de `hoy` y calcular `ultimo + 1` (o 1);
  - guardar el contador;
  - insertar el presupuesto con `numero = f"PRE-{anio}-{n:03d}"`, `fecha_creacion = fecha_emision = hoy`, `fecha_validez = hoy + ajustes.dias_validez`, `tipo_iva = ajustes.tipo_iva`, `validez_editada_a_mano = 0`;
  - devolver el id.
  
  (FR-010, D10)
- [X] T030 [US1] Añadir a `presupuestos/db.py` la función `cargar_presupuesto(conn, id)`, que devuelve presupuesto, líneas ordenadas por `posicion`, cliente (aunque esté archivado o anonimizado), ajustes, perfil actual y los **valores efectivos**: perfil y retención de `emisor_congelado` si no es NULL, si no los actuales; `mencion_canarias` siempre la actual (FR-018). Incluye el resultado de `dominio.calculo.calcular`
- [X] T031 [US1] Crear `presupuestos/rutas/presupuestos.py`:
  - `POST /presupuestos` → `crear_presupuesto` → 303 a `/presupuestos/{id}`;
  - `GET /presupuestos/{id}` → pantalla de edición;
  - `PUT /presupuestos/{id}` (fragmento) para un campo cada vez:
    - `fecha_emision`: si `validez_editada_a_mano = 0`, recalcula la validez;
    - `fecha_validez`: pone `validez_editada_a_mano = 1`; si es anterior a la emisión → 422 «La fecha de validez no puede ser anterior a la de emisión»;
    - `tipo_iva` ∈ {21, 10, 4, 0};
    - `notas`;
    - `cliente_id`: solo clientes con `archivado = 0` y `anonimizado = 0`;
  - actualiza `actualizado_en` y devuelve cabecera, totales y mención recalculados (FR-011, FR-014, FR-015, FR-016, FR-017).
- [X] T032 [US1] Añadir a `presupuestos/rutas/presupuestos.py` las rutas de líneas, todas como fragmento que devuelve líneas y totales:
  - `POST /presupuestos/{id}/lineas`: línea manual (`descripcion` obligatoria, `unidad` opcional, `cantidad`, `precio`) o con `servicio_id`, que copia nombre, unidad y precio del servicio sin guardar vínculo (CA4, CA5);
  - `PUT /presupuestos/{id}/lineas/{linea_id}`;
  - `POST /presupuestos/{id}/lineas/{linea_id}/mover` (`direccion=arriba|abajo`, intercambia `posicion`);
  - `DELETE /presupuestos/{id}/lineas/{linea_id}`;
  - validación con `leer_cantidad`/`leer_importe`: «cantidad > 0, precio ≥ 0, máx. 2 decimales» → 422 con el mensaje junto al campo (FR-012, FR-013, RF8).
- [X] T033 [P] [US1] Crear `presupuestos/templates/presupuesto.html` y los fragmentos `presupuestos/templates/fragmentos/_cabecera.html`, `_lineas.html`, `_totales.html`:
  - `_cabecera.html`: número, fechas, selector de tipo de IVA, cliente y notas;
  - `_lineas.html`: descripción, cantidad, unidad, precio unitario e importe por línea, botones subir/bajar/eliminar y formulario de línea nueva, con selector de servicios activos (vacío hasta US5);
  - `_totales.html`: fila IVA **siempre**, fila «Retención IRPF (−Y %)» **solo** si aplica, mención si existe y aviso «Totales provisionales: elige un cliente» si `provisional`;
  - campos con `hx-put`/`hx-post`, `hx-trigger="change"` y `hx-target` en los fragmentos; campos numéricos `type="text" inputmode="decimal"`.
- [X] T034 [US1] Crear `presupuestos/rutas/clientes.py` con el selector de cliente del presupuesto:
  - `GET /clientes/buscar?q=` (fragmento): `LIKE` sobre `nombre` o `nif`, solo `archivado = 0 AND anonimizado = 0`, máximo 20 resultados;
  - `POST /clientes`, que valida con `validar_cliente` (FR-006, FR-007). Con `presupuesto_id`, además asigna el cliente a ese presupuesto y devuelve el fragmento del presupuesto sin tocar sus líneas (FR-008, CA3).
- [X] T035 [P] [US1] Crear `presupuestos/templates/fragmentos/_selector_cliente.html` y `_cliente_form.html`:
  - buscador con `hx-get` y `hx-trigger="keyup changed delay:300ms"`, y botón «Nuevo cliente»;
  - formulario con nombre, NIF/NIE o NIF-IVA, dirección, país, email, categoría (Empresa/autónomo, Particular) y territorio (Península y Baleares; Canarias, Ceuta o Melilla; Otro país UE; Fuera de la UE);
  - si la categoría es Particular, solo ofrece los dos territorios de España (P3), y la casilla «NIF-IVA verificado» solo se muestra con «Otro país UE». Lo hace `app.js`, sin JS en línea; el servidor lo vuelve a validar.
- [X] T035b [US1] Añadir a `presupuestos/rutas/presupuestos.py` un `GET /` mínimo y crear `presupuestos/templates/historial.html` con el botón «Nuevo presupuesto» (formulario POST a `/presupuestos`) y la lista de presupuestos (número y enlace), ordenada por `fecha_emision DESC, numero DESC`. US6 la completa con cliente, fecha, total y búsqueda (FR-026)

**Checkpoint**: la Historia 1 funciona sola: se crea un presupuesto, se elige o crea un cliente y todos los totales de la spec cuadran

---

## Phase 4: User Story 3 - Configurar perfil del emisor y ajustes fiscales (Priority: P2)

**Goal**: guardar perfil, logo y ajustes fiscales por defecto. Va antes de la Historia 2 porque el PDF los necesita.

**Independent Test**: quickstart B1–B4: rellenar perfil y ajustes, cerrar el navegador, volver a entrar y comprobar que se conservan y se usan en un presupuesto nuevo.

- [X] T036 [US3] Crear `presupuestos/rutas/perfil.py` con:
  - `GET /perfil` y `POST /perfil`: valida con `faltan_perfil` y, si falta algo, responde 422 con la lista «Faltan: nombre, NIF…»; si no, hace `INSERT INTO perfil (id, nombre, nif, direccion, email, telefono) VALUES (1, …) ON CONFLICT(id) DO UPDATE SET nombre = excluded.nombre, …, telefono = excluded.telefono`. `logo_id` no se toca. No usar `INSERT OR REPLACE`: borra la fila y perdería el logo (FR-001).
  - `GET /ajustes` y `POST /ajustes`, con `tipo_iva` ∈ {21, 10, 4, 0}, `retencion_activa` sí/no, `tipo_retencion` ∈ {15, 7}, `dias_validez` entero ≥ 1 y `mencion_canarias` texto libre (FR-003).
- [X] T037 [US3] Añadir a `presupuestos/rutas/perfil.py`:
  - `POST /perfil/logo` (multipart): rechaza si supera `2 * 1024 * 1024` bytes. Detecta el tipo **por contenido**: PNG empieza por `\x89PNG\r\n\x1a\n`, JPEG por `\xFF\xD8\xFF`, y SVG es UTF-8 que tras un prólogo XML o comentarios opcionales empieza por `<svg`. Si no encaja, responde 422 «Formatos permitidos: PNG, JPG o SVG, hasta 2 MB». Si encaja, inserta en `logos` y actualiza `perfil.logo_id` (FR-002, CL9, D12).
  - `GET /logos/{id}` devuelve la imagen con su tipo y con las cabeceras `Content-Security-Policy: script-src 'none'; sandbox` y `X-Content-Type-Options: nosniff` (D9).
- [X] T038 [P] [US3] Crear `presupuestos/templates/perfil.html` (formulario con vista previa del logo mediante `<img src="/logos/{id}">`, nunca SVG en línea) y `presupuestos/templates/ajustes.html`

**Checkpoint**: perfil, logo y ajustes se guardan y los presupuestos nuevos toman IVA y validez de Ajustes

---

## Phase 5: User Story 2 - Descargar el presupuesto en PDF con imagen corporativa (Priority: P1)

**Goal**: descargar el PDF con logo, datos, desglose, mención y notas, con nombre de archivo correcto y congelando el emisor en la primera descarga.

**Independent Test**: quickstart E1–E10.

- [X] T039 [US2] Crear `presupuestos/pdf.py`: `generar_pdf(html) -> bytes` con `weasyprint.HTML(string=html, url_fetcher=solo_data)`. `solo_data` solo acepta URIs `data:` y lanza un error para cualquier otra URL, así no se descarga nada de internet (D6)
- [X] T040 [P] [US2] Crear `presupuestos/templates/pdf.html` siguiendo [contracts/pdf-presupuesto.md](./contracts/pdf-presupuesto.md):
  - bloques 1–8 en orden, con el logo como `data:` URI (base64 desde `logos.datos`);
  - CSS `@page { size: A4; margin: 15mm }`, `thead { display: table-header-group }` (cabecera repetida en cada página, FR-024) y `tr { break-inside: avoid }`;
  - desglose con los filtros `euros` y `porcentaje`: fila IVA siempre, retención solo si aplica, como «Retención IRPF (−15 %)»;
  - «Válido hasta el DD/MM/AAAA»;
  - sin numeración de páginas.
- [X] T041 [US2] Añadir `GET /presupuestos/{id}/pdf` a `presupuestos/rutas/presupuestos.py`:
  - si `requisitos_descarga` devuelve fallos, responde 422 con la pantalla del presupuesto y la lista de lo que falta (FR-023);
  - si no, y `emisor_congelado` es NULL, lo rellena en una transacción con el JSON `{nombre, nif, direccion, email, telefono, logo_id, retencion_activa, tipo_retencion}` del perfil y ajustes actuales (FR-018, RN9);
  - genera el PDF con los mismos valores calculados que la pantalla (FR-025);
  - responde con `Content-Type: application/pdf` y `Content-Disposition: attachment; filename="<nombre_pdf(...)>"` (FR-022).
- [X] T042 [US2] Añadir el botón «Descargar PDF» (enlace normal, no HTMX) a `presupuestos/templates/presupuesto.html` y la zona donde se muestra la lista de requisitos que faltan
- [X] T042b [US2] Añadir a `presupuestos/rutas/clientes.py` `GET /clientes/{id}` y `PUT /clientes/{id}` (valida con `validar_cliente`) y crear `presupuestos/templates/cliente.html` reutilizando `_cliente_form.html`. Enlazar desde la cabecera del presupuesto («Editar cliente») para poder completar el NIF que falta (US2 AS6, CL13)

**Checkpoint**: el PDF se descarga, coincide al céntimo con la pantalla y conserva el emisor de la primera descarga

---

## Phase 6: User Story 8 - Acceso con cuenta propia (Priority: P1)

**Goal**: bloqueo por intentos fallidos, gestión de asistentes por el titular, cambio y restablecimiento de contraseñas.

**Independent Test**: quickstart A1–A12.

- [X] T043 [US8] Añadir a `presupuestos/seguridad.py` `esta_bloqueado(conn, email)`, `registrar_fallo(conn, email)` (al 5.º fallo seguido: `bloqueado_hasta = ahora + 15 min` y `fallos = 0`) y `limpiar_intentos(conn, email)`, aplicados también a emails que no existen. Integrarlo en `POST /entrar` de `presupuestos/rutas/sesion.py`: si está bloqueado, 429 «Demasiados intentos. Vuelve a intentarlo en unos minutos.» aunque la contraseña sea correcta; el mensaje de fallo siempre es «Email o contraseña incorrectos» (FR-038)
- [X] T044 [US8] Crear `presupuestos/rutas/cuentas.py` con `GET /mi-cuenta` y `POST /mi-cuenta/contrasena` (`actual`, `nueva`): verifica la actual, valida 10 caracteres, guarda el hash y borra las demás sesiones del usuario (FR-039)
- [X] T045 [US8] Añadir a `presupuestos/rutas/cuentas.py` las rutas con dependencia `solo_titular`:
  - `GET /cuentas`;
  - `POST /cuentas`: alta de asistente con `nombre`, `email` (en minúsculas; si se repite → 422 «Ya existe una cuenta con ese email») y `contrasena` de al menos 10 caracteres;
  - `POST /cuentas/{id}/baja`: si es el titular → 422 «El titular no puede darse de baja»; si no, `activo = 0` y borra sus sesiones;
  - `POST /cuentas/{id}/contrasena`: solo sobre asistentes; nuevo hash y borra sus sesiones.
  
  (FR-035, FR-039)
- [X] T046 [P] [US8] Crear `presupuestos/templates/mi_cuenta.html` y `presupuestos/templates/cuentas.html` (lista con nombre, email, tipo y estado; formularios de alta, baja con `hx-confirm` y nueva contraseña)
- [X] T047 [US8] Añadir a `presupuestos/__main__.py` la orden `restablecer-titular`: pide la nueva contraseña dos veces, valida 10 caracteres, guarda el hash, borra las sesiones del titular y su fila en `intentos_acceso` ([contracts/cli-administracion.md](./contracts/cli-administracion.md#restablecer-titular--fr-039))
- [X] T048 [US8] Ampliar `tests/test_acceso.py` con:
  - credenciales incorrectas → 401 con mensaje genérico;
  - 5 fallos → 429 incluso con la contraseña correcta, y acceso de nuevo al mover `bloqueado_hasta` al pasado;
  - un asistente recibe 403 en `/cuentas`;
  - tras la baja, la siguiente petición del asistente → 303 a `/entrar`;
  - cambiar la contraseña invalida las otras sesiones;
  - una sesión con `ultima_actividad` de hace 9 h → 303 a `/entrar`;
  - un `POST` con `Origin` ajeno → 403;
  - el titular no puede darse de baja;
  - toda respuesta autenticada (p. ej. `GET /`, `GET /presupuestos/{id}`, `GET /exportar`) lleva `Cache-Control: no-store`.

**Checkpoint**: solo entra quien el titular autoriza y el acceso se corta al instante

---

## Phase 7: User Story 4 - Gestionar clientes (Priority: P2)

**Goal**: pantalla de clientes con edición, archivo y anonimización (RGPD).

**Independent Test**: quickstart D1–D6.

- [X] T049 [US4] Añadir a `presupuestos/rutas/clientes.py`:
  - `GET /clientes`: lista de `archivado = 0`, con buscador por nombre o NIF;
  - en `PUT /clientes/{id}` (creado en T042b): si `anonimizado = 1` → 409 «Este cliente fue eliminado y no se puede editar»;
  - `POST /clientes/{id}/archivar`: `archivado = 1` (CL11, FR-009);
  - `POST /clientes/{id}/anonimizar`, según la regla de data-model.md: `nombre = 'Cliente eliminado'`; `nif`, `direccion`, `pais` y `email` vacíos; `anonimizado = 1` y `archivado = 1`; se conservan `categoria`, `territorio` y `nif_iva_verificado` (FR-043).
- [X] T050 [P] [US4] Crear `presupuestos/templates/clientes.html` y añadir a `presupuestos/templates/cliente.html` (de T042b) los botones «Archivar» y «Anonimizar cliente». «Archivar» y «Anonimizar cliente» llevan `hx-confirm`. El de anonimizar dice: «Se borrarán definitivamente el nombre, NIF, dirección, país y email de este cliente. Sus presupuestos se conservarán, pero no podrán descargarse. ¿Continuar?»
- [X] T051 [US4] En `presupuestos/templates/fragmentos/_cabecera.html`, mostrar «Cliente eliminado» y el motivo del bloqueo de descarga cuando el cliente del presupuesto está anonimizado; y «(archivado)» junto al nombre si está archivado

**Checkpoint**: clientes completos, incluido el derecho de supresión

---

## Phase 8: User Story 7 - Numeración automática (Priority: P2)

**Goal**: garantizar la serie PRE-AAAA-NNN sin duplicados, también con creaciones simultáneas y en el cambio de año. La lógica ya existe (T029); esta fase la verifica.

**Independent Test**: quickstart F1–F3 y F8.

- [X] T052 [US7] Crear `tests/test_numeracion.py`:
  - dos creaciones seguidas → `PRE-2026-015`/`PRE-2026-016` con el contador en 14 (CA10);
  - `crear_presupuesto(conn, hoy="2027-01-02")` tras `PRE-2026-120` → `PRE-2027-001` (CL10);
  - borrar el último y crear otro → no se reutiliza el número;
  - 10 hilos con conexiones distintas creando a la vez → 10 números distintos y consecutivos (FR-033).
- [X] T053 [US7] Revisar que `crear_presupuesto` en `presupuestos/db.py` toma el año de `fecha_creacion` (no de `fecha_emision`) y que ningún otro código modifica `presupuestos.numero` ni hace bajar `contadores.ultimo`. Corregir si hace falta

**Checkpoint**: numeración verificada automáticamente

---

## Phase 9: User Story 9 - Datos a salvo y exportación (Priority: P2)

**Goal**: exportar todos los datos de negocio y copia diaria fuera del servidor con restauración documentada.

**Independent Test**: quickstart G1–G4.

- [X] T054 [P] [US9] Crear `presupuestos/rutas/exportar.py` con `GET /exportar`, que devuelve el JSON exacto de [contracts/archivo-exportacion.md](./contracts/archivo-exportacion.md):
  - `formato: "presupuestospro"`, `version: 1`, `exportado_en`;
  - `datos` con perfil, ajustes, logos (`datos_base64`), servicios, clientes, presupuestos con sus líneas anidadas, y contadores;
  - sí/no como `true`/`false`;
  - **sin** `usuarios`, `sesiones` ni `intentos_acceso`;
  - `Content-Disposition: attachment; filename="presupuestospro-copia-AAAA-MM-DD.json"`.
  
  Disponible para titular y asistentes (FR-029).
- [X] T055 [P] [US9] Añadir a `presupuestos/__main__.py` la orden `copia --destino DIR`:
  - usa `sqlite3.Connection.backup` hacia `DIR/presupuestospro-AAAA-MM-DD.db`;
  - comprueba la copia con `PRAGMA integrity_check`; si no es `ok`, termina con código ≠ 0;
  - escribe en español la ruta y el tamaño de la copia.
  
  (FR-041, [contracts/cli-administracion.md](./contracts/cli-administracion.md#copia--fr-041))
- [X] T056 [US9] Crear `docs/administracion.md` para el administrador técnico:
  - **instalación**: VPS en la UE, Docker, copiar `.env.example` a `.env`, apuntar el DNS a `DOMINIO`, `docker compose up -d --build`, `crear-titular`;
  - **actualización**: `git pull` y `docker compose up -d --build`;
  - **configuración de rclone** con un almacenamiento de objetos en la UE de otro proveedor (credenciales solo en `~/.config/rclone/rclone.conf` del servidor);
  - **líneas exactas del cron diario**: `copia`, `rclone copy ./copias remoto:bucket`, `rclone delete --min-age 30d remoto:bucket`, y `find ./copias -mtime +7 -delete`;
  - **restauración** paso a paso (FR-042);
  - **contraseña del titular olvidada**: `restablecer-titular`;
  - **aviso**: tras restaurar una copia anterior a una anonimización, hay que repetirla;
  - **recordatorio**: contratos de encargado del tratamiento con ambos proveedores.
- [X] T057 [US9] Crear `tests/test_exportar_copia.py`: la exportación tiene todas las claves del contrato, no contiene `hash_contrasena` ni emails de cuentas, y la incluye un asistente; la orden `copia` genera un archivo que se abre y contiene los mismos presupuestos

**Checkpoint**: los datos sobreviven a perder navegador, equipo o servidor (máx. un día)

---

## Phase 10: User Story 5 - Mantener el catálogo de servicios (Priority: P3)

**Goal**: catálogo de servicios para añadir líneas sin buscar precios.

**Independent Test**: quickstart B4, C15 y la Historia 5 de la spec: crear un servicio, usarlo, cambiar su precio y comprobar que el presupuesto no cambia.

- [X] T058 [US5] Crear `presupuestos/rutas/catalogo.py`:
  - `GET /catalogo`: servicios con `archivado = 0`;
  - `POST /catalogo` y `PUT /catalogo/{id}`: `nombre` obligatorio, `descripcion` opcional, `unidad` ∈ {hora, día, proyecto, unidad}, precio con `leer_importe` y «precio ≥ 0, máx. 2 decimales»;
  - `POST /catalogo/{id}/archivar`.
  
  (FR-004, FR-005)
- [X] T059 [P] [US5] Crear `presupuestos/templates/catalogo.html` y rellenar en `presupuestos/templates/fragmentos/_lineas.html` el selector «Añadir desde el catálogo» con los servicios con `archivado = 0` (envía `servicio_id` a `POST /presupuestos/{id}/lineas`)

**Checkpoint**: las líneas se añaden desde el catálogo como copias independientes

---

## Phase 11: User Story 6 - Consultar y reabrir presupuestos anteriores (Priority: P3)

**Goal**: historial con búsqueda, reabrir y borrar.

**Independent Test**: quickstart F2 y F5–F7.

- [X] T060 [US6] Ampliar `GET /` en `presupuestos/rutas/presupuestos.py` (creado en T035b): lista ordenada por `fecha_emision DESC, numero DESC` con número, nombre del cliente («—» si no hay), fecha de emisión (DD/MM/AAAA) y total calculado con `dominio.calculo.calcular` y los valores efectivos de cada presupuesto. `?q=` filtra con `LIKE` por `numero` o `clientes.nombre` (FR-026)
- [X] T061 [US6] Añadir `DELETE /presupuestos/{id}` a `presupuestos/rutas/presupuestos.py`: borra el presupuesto (las líneas caen en cascada) sin tocar `contadores` y responde con `HX-Redirect: /` (FR-019)
- [X] T062 [P] [US6] Ampliar `presupuestos/templates/historial.html` (de T035b) con el buscador (`hx-get`, `hx-trigger="keyup changed delay:300ms"`) y las columnas cliente, fecha y total; y añadir a `presupuesto.html` el botón «Borrar presupuesto» con `hx-delete` y `hx-confirm="¿Borrar este presupuesto? Su número no se volverá a usar."`

**Checkpoint**: todas las historias funcionan por separado

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: revisión transversal antes de dar la entrega por terminada

- [X] T063 [P] Revisar todas las plantillas de `presupuestos/templates/` a 360 px, en tableta y en ordenador: sin desplazamiento horizontal y todas las funciones usables (FR-031, SC-009). Ajustar `presupuestos/static/estilos.css`
  - *Evidencia (2026-11-15, durante la 003)*: las 12 pantallas medidas en Chrome a 320, 360, 800 y 1280 px sin desplazamiento horizontal, un único `h1`, controles ≥ 44 px y todas las acciones disponibles (ver la verificación de T019 y T034 en `specs/003-rediseno-visual/tasks.md`).
- [X] T064 [P] Revisar todos los textos visibles de `presupuestos/templates/`, `presupuestos/rutas/` y `presupuestos/__main__.py`: español de España, importes con `euros` y fechas con `fecha` (FR-030)
- [X] T065 [P] Comprobar la seguridad en el repositorio:
  - ninguna URL externa en `presupuestos/templates/` ni en `presupuestos/static/`;
  - ningún `|safe` ni `Markup` sobre datos del usuario;
  - ninguna consulta SQL construida con f-strings;
  - ningún secreto versionado (`.env` en `.gitignore`).
  
  (D9, constitución, principio V)
- [ ] T066 Ejecutar `docker compose exec app pytest` y recorrer [quickstart.md](./quickstart.md) completo (A–H) en la app, anotando cualquier fallo. Corregir antes de cerrar (constitución, «Verificación de cada entrega»)
- [X] T067 Revisar la entrega contra los principios I–V de `.specify/memory/constitution.md` y anotar en una lista de propuestas separada cualquier idea surgida que no esté en la spec

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sin dependencias.
- **Foundational (Fase 2)**: depende de Setup y **bloquea todas las historias**.
- **US1 (Fase 3)**: solo depende de Foundational. Es el MVP.
- **US3 (Fase 4)**: solo depende de Foundational.
- **US2 (Fase 5)**: depende de US1 (presupuesto y cliente) y de US3 (perfil completo para poder descargar).
- **US8 (Fase 6)**: solo depende de Foundational (el inicio de sesión básico ya existe). Puede ir en paralelo con US1, US3 y US2.
- **US4 (Fase 7)**: depende de US1 (`rutas/clientes.py` y `_cliente_form.html`).
- **US7 (Fase 8)**: depende de US1 (T029).
- **US9 (Fase 9)**: solo depende de Foundational. Es más útil tras US1–US3, cuando ya hay datos.
- **US5 (Fase 10)**: depende de US1 (`_lineas.html`).
- **US6 (Fase 11)**: depende de US1.
- **Polish (Fase 12)**: tras todas las historias.

### Orden de terminación recomendado

```text
Setup → Foundational → US1 → US3 → US2 → US8 → US4 → US7 → US9 → US5 → US6 → Polish
                         └──────── US8 y US9 pueden avanzar en paralelo desde Foundational ────────┘
```

### Within Each User Story

- Funciones de `db.py` antes que las rutas que las usan.
- Las rutas antes que los botones que las llaman; las plantillas marcadas [P] pueden hacerse a la vez que las rutas.
- Tareas sobre el mismo archivo (`rutas/presupuestos.py`, `rutas/clientes.py`, `rutas/cuentas.py`, `__main__.py`, `db.py`) en orden, nunca en paralelo.

---

## Parallel Example: Foundational

```bash
# Reglas de negocio puras y sus tests, todas en archivos distintos:
Task: "T010 formato.py"        Task: "T011 fechas.py"        Task: "T012 nombre_archivo.py"
Task: "T013 tratamiento.py"    Task: "T014 calculo.py"       Task: "T015 validacion.py"
Task: "T016 test_calculo.py"   Task: "T017 test_tratamiento.py"
Task: "T018 test_formato_fechas_nombre.py"   Task: "T019 test_validacion.py"
# Esqueleto web en paralelo:
Task: "T022 base.html"   Task: "T023 app.js"   Task: "T024 estilos.css"
```

## Parallel Example: User Story 1

```bash
# Tras T029–T032 (db.py y rutas/presupuestos.py, en orden):
Task: "T033 presupuesto.html + _cabecera/_lineas/_totales"
Task: "T035 _selector_cliente.html + _cliente_form.html"
```

## Parallel Example: entre historias

```bash
# Con Foundational terminado, tres personas o agentes:
Persona A: US1 (T029–T035b) → US3 (T036–T038) → US2 (T039–T042b)
Persona B: US8 (T043–T048)
Persona C: US9 (T054–T057)
```

---

## Implementation Strategy

### MVP First

1. Fase 1 (Setup) y Fase 2 (Foundational): la app arranca, hay inicio de sesión y las reglas fiscales están probadas.
2. Fase 3 (US1): **parar y validar** con quickstart C0–C17. Ya aporta el valor principal: presupuestos con cálculo correcto, protegidos con inicio de sesión.
3. Fases 4–5 (US3 + US2): perfil y PDF. Con esto el autónomo ya puede **enviar presupuestos reales**.
4. Fase 6 (US8): asistentes y bloqueo. **Imprescindible antes de publicar el servidor en internet con datos reales.**

### Incremental Delivery

- **Entrega 1** (uso real en producción): Setup + Foundational + US1 + US3 + US2 + US8 + US9 (copias). No se ponen datos reales en internet sin control de acceso completo (US8) y sin copias (US9).
- **Entrega 2**: US4 (clientes completos y anonimización) + US7 (numeración verificada).
- **Entrega 3**: US5 (catálogo) + US6 (historial) + Polish.

Cada entrega se verifica con las secciones correspondientes de [quickstart.md](./quickstart.md) antes de darla por terminada.

---

## Notes

- [P] = archivos distintos y sin dependencias pendientes.
- Cada tarea cita el requisito de la spec que cubre (constitución, «Alcance y propuestas»).
- Hacer commit tras cada tarea o grupo lógico.
- No añadir nada que no esté en la spec; las ideas nuevas van a la lista de propuestas (T067).
