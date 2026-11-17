# Implementation Plan: PresupuestosPro v1.1 — Navegación, formularios, alta de usuarios y modo oscuro

**Branch**: `002-mejoras-ui-usuarios` (ampliación de modo oscuro: `005-modo-oscuro`) | **Date**: 2026-11-14, ampliado 2026-11-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-mejoras-ui-usuarios/spec.md`

## Summary

Iteración sobre la aplicación de la 001, ya implementada: menú lateral con botón de hamburguesa en móvil, «Volver al historial» que conserva la búsqueda, sección «Usuarios» con formularios claros, creación del titular desde el navegador (sin comandos), selectores para tipo de documento y país, calendario para las fechas y un apartado de logo más claro en el Perfil.

**Enfoque, en una frase**: casi todo es capa de presentación (plantillas Jinja2, `estilos.css` y `app.js`) sobre el stack, las convenciones y la estructura de [specs/001-presupuestos-pro/plan.md](../001-presupuestos-pro/plan.md), que se respetan sin cambios ni dependencias nuevas.

**Lo que no es solo presentación** (lo mínimo que exige la spec, cada punto ligado a un requisito):

| Cambio | Por qué | Requisito |
|---|---|---|
| Columna `clientes.tipo_documento` + paso de actualización automático (`user_version` 1 → 2) | El tipo de documento es un dato nuevo que hay que guardar | FR-112, FR-114, SC-106 |
| Rutas públicas `GET/POST /crear-titular` y retirada de la orden `crear-titular` | Crear el titular sin comandos | FR-108, FR-109, FR-110 |
| Validación en el servidor de tipo de documento, país, repetición de contraseña y fechas ISO | El servidor tiene la última palabra (como en la 001) | FR-107, FR-112, FR-113, FR-115 |
| `POST /perfil/logo/quitar` | Quitar el logo, que v1 no permitía | FR-116 |
| `/cuentas*` → `/usuarios*` | Nombre visible y URL coherentes | FR-106 |

Detalle y alternativas descartadas en [research.md](./research.md) (R1–R11).

### Ampliación 2026-11-17: modo oscuro (US7, FR-117 a FR-130)

Selector «Tema» (Claro / Oscuro / Como el sistema) en el menú lateral, cambio inmediato sin perder datos, elección recordada por dispositivo, sin destello al cargar y PDF siempre en claro.

**Enfoque, en una frase**: una segunda hoja de colores (`tokens-oscuro.css`) que `base.html` carga con un `media` distinto según la cookie `tema`; el servidor pinta cada página ya con el tema correcto y el navegador se encarga de seguir al sistema. Sin dependencias, sin cambios en la base de datos y sin tocar el PDF.

| Cambio | Por qué | Requisito |
|---|---|---|
| `static/tokens-oscuro.css` (nuevo): todas las variables de color con valores oscuros y `color-scheme: dark` | Paleta oscura en un único lugar, que el PDF nunca lee | FR-125, FR-127, FR-128, FR-130 (R13, R16) |
| `base.html`: `<link id="tokens-oscuro" media=…>` y `<meta name="color-scheme">` según el tema | Sin destello; «Como el sistema» lo resuelve el navegador; controles nativos en oscuro | FR-123, FR-125, FR-126 (R14) |
| `POST /tema` (nueva) y cookie `tema` | Recordar la elección por dispositivo, también sin JS | FR-120, FR-121, FR-122 (R12, R15) |
| Selector en el menú + unas líneas en `app.js` | Cambio inmediato sin recargar | FR-117, FR-118, FR-119 (R15) |
| Token `--color-fondo-logo` y fondo de `.logo-previa` | Logos oscuros visibles | FR-129 (R17) |
| `tests/test_paleta.py` ampliado y `tests/test_tema.py` (nuevo) | Contrastes en los dos temas, paleta completa, ruta y cookie | SC-110 (R16) |

Detalle y alternativas en [research.md](./research.md#ampliación-2026-11-17-modo-oscuro-us7-fr-117-a-fr-130) (R12–R18) y [contracts/tema.md](./contracts/tema.md).

## Technical Context

Sin cambios respecto a [specs/001-presupuestos-pro/plan.md](../001-presupuestos-pro/plan.md#technical-context): mismo lenguaje, dependencias, almacenamiento, pruebas, plataforma, tipo de proyecto, objetivos de rendimiento y restricciones. **No se añade ninguna dependencia** (ni de Python ni de JavaScript).

Precisiones de esta iteración:

- **Navegadores**: el calendario es el `<input type="date">` nativo; con navegadores que no lo tengan, el campo admite DD/MM/AAAA (R9).
- **Punto de corte del menú**: 1024 px (spec, Supuestos).
- **Esquema**: `PRAGMA user_version = 2` (R11).
- **Alcance**: ~12 pantallas: las 11 de la 001 (con «Cuentas» renombrada a «Usuarios») más «Crear la cuenta del titular».

Precisiones de la ampliación de modo oscuro (2026-11-17):

- **Dependencias**: ninguna nueva. Solo CSS (`media` en `<link>`, `prefers-color-scheme`, `color-scheme`), una cookie y `fetch` en el `app.js` existente.
- **Navegadores**: `prefers-color-scheme` y `color-scheme` los soportan todos los navegadores actuales; uno que no informe de preferencia se queda en claro (FR-122).
- **Esquema**: sin cambios; `user_version` sigue en 2.
- **CSP**: sin cambios (`script-src 'self'; style-src 'self'`); no se añade ningún script ni estilo en línea.
- **PDF**: sin cambios; `pdf.estilos_comunes()` sigue leyendo solo `tokens.css`.
- **Base visual**: tokens, contrastes y etiquetas de [specs/003-rediseno-visual](../003-rediseno-visual/contracts/sistema-visual.md); la 004 (ventana «Exportar…») reutiliza los mismos tokens, así que hereda el modo oscuro.

No queda ningún «NEEDS CLARIFICATION».

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo lo cumple el plan | Estado |
|---|---|---|
| **I. Simplicidad ante todo** | Sin dependencias nuevas: calendario nativo, menú con CSS y unas decenas de líneas en el `app.js` existente, «Añadir usuario» con `<details>`, búsqueda conservada con un parámetro en la URL. Una columna nueva con `ALTER TABLE` en lugar de herramienta de migraciones. Se elimina un camino duplicado (orden `crear-titular`). | ✅ |
| **II. Idioma y mercado** | Textos nuevos en español de España; lista de países en español; fechas mostradas en DD/MM/AAAA (en el calendario nativo, con navegador en español, R9). | ✅ |
| **III. Cero alcance fantasma** | Solo lo de la spec: sin logo de cliente, sin pestañas, sin selector de rangos, sin redirección de `/cuentas`. Los títulos de grupo del menú están en la spec (sesión de aclaraciones). | ✅ |
| **IV. Verificable sin leer código** | [quickstart.md](./quickstart.md) cubre cada escenario de aceptación y criterio de éxito con pasos y resultado observable. Solo la instalación y la actualización del servidor (1a, 1b, E1) son técnicas, dentro de la excepción de la constitución. | ✅ |
| **V. Datos del usuario con respeto** | Un único dato nuevo (tipo de documento), opcional; se borra al anonimizar. La creación del titular no introduce secretos en código ni en configuración. Contraseñas con las mismas reglas (Argon2id, ≥ 10). | ✅ |

**Re-evaluación tras el diseño (Fase 1)**: ✅ sin cambios. Riesgo asumido y documentado en la spec (Supuestos): mientras no existe titular, `/crear-titular` está abierta (decisión de la sesión de aclaraciones, principio I). No hay violaciones que justificar.

### Ampliación 2026-11-17: modo oscuro

| Principio | Cómo lo cumple el plan | Estado |
|---|---|---|
| **I. Simplicidad ante todo** | Una hoja CSS más y un `media` en `<link>`: el navegador hace el trabajo de «Como el sistema» y de los controles nativos. Por dispositivo (cookie), sin columna nueva ni cambio de esquema. Una ruta (`POST /tema`) y unas líneas en `app.js`. Sin dependencias. Descartados `light-dark()`, bloques duplicados y `localStorage` (R13, R14, R12). | ✅ |
| **II. Idioma y mercado** | Textos nuevos en español de España: «Tema», «Claro», «Oscuro», «Como el sistema», «Aplicar». | ✅ |
| **III. Cero alcance fantasma** | Solo US7/FR-117–FR-130: sin temas extra, sin PDF oscuro, sin programación horaria, sin selector en pantallas sin sesión, sin guardar el tema en la cuenta (fuera de alcance de la spec). | ✅ |
| **IV. Verificable sin leer código** | [quickstart.md](./quickstart.md#f-modo-oscuro-us7-ampliación-2026-11-17) sección F cubre los 12 escenarios de US7, los casos límite y SC-108–SC-112 con pasos y resultado visible. Solo F17 (tests de contraste) es técnico; SC-110 también se comprueba con cualquier comprobador de contraste sobre la tabla de [tema.md](./contracts/tema.md#pares-de-contraste-en-oscuro-fr-127). | ✅ |
| **V. Datos del usuario con respeto** | No se pide ningún dato nuevo. La cookie `tema` solo guarda una de tres palabras, no identifica a nadie y no se guarda en el servidor. Sin secretos. | ✅ |

**Re-evaluación tras el diseño (Fase 1)**: ✅ sin violaciones. Seguridad: `POST /tema` exige sesión y origen propio (D9) y solo redirige a rutas internas (`volver`), para no abrir una redirección a sitios ajenos.

## Project Structure

### Documentation (this feature)

```text
specs/002-mejoras-ui-usuarios/
├── plan.md              # Este archivo
├── research.md          # Fase 0: decisiones R1–R11
├── data-model.md        # Fase 1: solo cambios sobre el modelo de la 001
├── quickstart.md        # Fase 1: guía de comprobación en la app
├── contracts/
│   ├── cambios-rutas-y-pantallas.md   # Rutas nuevas/renombradas, exportación v2, órdenes, POST /tema
│   ├── interfaz.md                    # Menú, controles de formulario, textos
│   └── tema.md                        # Ampliación: selector, ruta, cookie, paleta oscura y contrastes
└── tasks.md             # Fase 2 (/speckit-tasks; no lo crea este comando)
```

### Source Code (repository root)

Estructura de la 001 sin cambios. Archivos que esta iteración toca (**nuevo**, *modificado*, ~~eliminado~~):

```text
docs/administracion.md                 # modificado: alta del titular desde el navegador
presupuestos/
├── __main__.py                        # modificado: se elimina la orden crear-titular
├── db.py                              # modificado: paso de user_version 1 → 2 (R11)
├── schema.sql                         # modificado: tipo_documento; user_version = 2
├── seguridad.py                       # modificado: validar_nueva(contrasena, repetir) (R5)
├── dominio/
│   ├── documento.py                   # NUEVO: tipos permitidos y preselección (R7)
│   ├── paises.py                      # NUEVO: PAISES, PAISES_UE y opciones por territorio (R8)
│   └── fechas.py                      # modificado: leer_fecha() acepta AAAA-MM-DD y DD/MM/AAAA (R9)
├── rutas/
│   ├── sesion.py                      # modificado: /crear-titular; /entrar redirige si no hay titular (R4)
│   ├── cuentas.py                     # modificado: rutas /usuarios*, repetir contraseña (R5, R6)
│   ├── clientes.py                    # modificado: tipo_documento y país validados; anonimizar vacía el tipo
│   ├── presupuestos.py                # modificado: ?volver=, fechas con leer_fecha()
│   ├── perfil.py                      # modificado: POST /perfil/logo/quitar (R10)
│   └── exportar.py                    # modificado: version 2 y tipo_documento
├── templates/
│   ├── base.html                      # modificado: menú lateral y botón ☰ (R1)
│   ├── crear_titular.html             # NUEVO
│   ├── usuarios.html                  # renombrado desde cuentas.html (R6)
│   ├── mi_cuenta.html, entrar.html    # modificados: repetir contraseña; aviso titular existente
│   ├── presupuesto.html, perfil.html  # modificados (historial.html no cambia: los enlaces están en el fragmento)
│   └── fragmentos/
│       ├── _historial_lista.html      # modificado: enlaces con ?volver=
│       ├── _cliente_form.html, _ficha_cliente.html     # modificados: selectores de tipo de documento y país
│       └── _fechas.html               # modificado: type="date" y min (R9)
└── static/
    ├── app.js                         # modificado: menú, espera de guardados (R3), filtros de tipo y país
    └── estilos.css                    # modificado: menú lateral, superposición móvil, estado activo
tests/
├── dominio/test_documento.py          # NUEVO
├── dominio/test_paises.py             # NUEVO
├── dominio/test_formato_fechas_nombre.py  # modificado: lectura ISO y DD/MM/AAAA
├── test_clientes.py                   # NUEVO: validación de tipo de documento y país en el servidor, anonimización
├── test_exportar_copia.py             # modificado: version 2 y tipo_documento
├── test_acceso.py                     # modificado: /crear-titular (solo sin titular, un único titular), /usuarios solo titular
└── test_actualizacion.py              # NUEVO: base de datos v1 → v2 conserva datos (SC-106)
```

Archivos que toca la **ampliación de modo oscuro** (2026-11-17):

```text
presupuestos/
├── rutas/
│   ├── __init__.py                    # modificado: tema_actual(request) como global de plantillas (R12, R14)
│   └── sesion.py                      # modificado: POST /tema y cookie «tema», junto a la cookie de sesión (R12, R15)
├── templates/
│   └── base.html                      # modificado: <link id="tokens-oscuro" media=…>, meta color-scheme, selector «Tema» en el menú (R14, R15)
└── static/
    ├── tokens.css                     # modificado: solo el token nuevo --color-fondo-logo (R13, R17)
    ├── tokens-oscuro.css              # NUEVO: paleta oscura completa + color-scheme: dark (R13, R16)
    ├── estilos.css                    # modificado: selector «Tema» en el menú, .logo-previa con fondo (R15, R17)
    └── app.js                         # modificado: aplicar el tema al momento y guardarlo con fetch; ocultar «Aplicar» (R15)
tests/
├── test_paleta.py                     # modificado: pares en los dos temas, paleta oscura completa y solo de color (R16)
└── test_tema.py                       # NUEVO: POST /tema (cookie, 204/303/422, volver interno, sesión), base.html según cookie, páginas sin sesión en «sistema», PDF sin hoja oscura (FR-120 a FR-126, FR-130)
```

No cambian: `pdf.py`, `pdf.html`, `db.py`, `schema.sql`, `app.py` (la ruta se registra con el router de `sesion.py`, que ya está incluido) ni ninguna otra plantilla.

**Structure Decision**: se mantiene el único proyecto Python de la 001. Las dos reglas nuevas con lógica (tipos de documento y países permitidos) van en **`dominio/`**, como las reglas fiscales, para probarlas con pytest y que pantalla y servidor no discrepen. El resto son plantillas, CSS y el `app.js` existente.

La ampliación de modo oscuro no añade lógica de dominio (no hay reglas de negocio nuevas): es presentación (CSS, plantilla, `app.js`) más una ruta mínima.

## Fases de la ampliación de modo oscuro

Orden previsto para `/speckit-tasks` (cada fase se puede comprobar con la sección F de [quickstart.md](./quickstart.md#f-modo-oscuro-us7-ampliación-2026-11-17)):

1. **Paleta**: `tokens-oscuro.css` con los valores de [contracts/tema.md](./contracts/tema.md#paleta-oscura), `--color-fondo-logo` en `tokens.css` y `test_paleta.py` ampliado (FR-127, FR-128; F17).
2. **Pintar el tema desde el servidor**: `tema_actual(request)` y `base.html` con `<link media>` y `meta color-scheme`; páginas sin sesión en `sistema` (FR-122 a FR-126; F4–F7, F14).
3. **Recordar la elección**: `POST /tema`, cookie, `volver` interno y tests de la ruta (FR-120, FR-121; F13, F15).
4. **Selector y cambio inmediato**: selector «Tema» en el menú, estilos y `app.js` (FR-117 a FR-119; F1–F3, F11, F16).
5. **Detalles y repaso visual**: vista previa del logo (FR-129; F12) y repaso en oscuro de todas las pantallas, la ventana «Exportar…» de la 004, los mensajes, las etiquetas de estado y los controles nativos, a 360 y 1280 px (FR-125; F8–F10).
6. **Cierre**:
   - Recorrer la sección F completa de `quickstart.md` y la regresión de la sección E (constitución, «Verificación de cada entrega»).
   - Actualizar `specs/README.md` (estado de la 002 y de la 003).
   - Actualizar `CLAUDE.md` con las decisiones de diseño y convenciones nuevas de esta feature, una línea por decisión, con referencia a la spec (p. ej. «[002] …»). No incluir entradas por incluir: solo información transversal y relevante para el proyecto que puedan aprovechar futuras features.

## Complexity Tracking

Sin violaciones de la constitución que justificar.
