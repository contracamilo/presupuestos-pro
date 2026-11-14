# Implementation Plan: PresupuestosPro v1.1 — Navegación, formularios y alta de usuarios

**Branch**: `002-mejoras-ui-usuarios` | **Date**: 2026-11-14 | **Spec**: [spec.md](./spec.md)

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

## Technical Context

Sin cambios respecto a [specs/001-presupuestos-pro/plan.md](../001-presupuestos-pro/plan.md#technical-context): mismo lenguaje, dependencias, almacenamiento, pruebas, plataforma, tipo de proyecto, objetivos de rendimiento y restricciones. **No se añade ninguna dependencia** (ni de Python ni de JavaScript).

Precisiones de esta iteración:

- **Navegadores**: el calendario es el `<input type="date">` nativo; con navegadores que no lo tengan, el campo admite DD/MM/AAAA (R9).
- **Punto de corte del menú**: 1024 px (spec, Supuestos).
- **Esquema**: `PRAGMA user_version = 2` (R11).
- **Alcance**: ~12 pantallas: las 11 de la 001 (con «Cuentas» renombrada a «Usuarios») más «Crear la cuenta del titular».

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

## Project Structure

### Documentation (this feature)

```text
specs/002-mejoras-ui-usuarios/
├── plan.md              # Este archivo
├── research.md          # Fase 0: decisiones R1–R11
├── data-model.md        # Fase 1: solo cambios sobre el modelo de la 001
├── quickstart.md        # Fase 1: guía de comprobación en la app
├── contracts/
│   ├── cambios-rutas-y-pantallas.md   # Rutas nuevas/renombradas, exportación v2, órdenes
│   └── interfaz.md                    # Menú, controles de formulario, textos
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

**Structure Decision**: se mantiene el único proyecto Python de la 001. Las dos reglas nuevas con lógica (tipos de documento y países permitidos) van en **`dominio/`**, como las reglas fiscales, para probarlas con pytest y que pantalla y servidor no discrepen. El resto son plantillas, CSS y el `app.js` existente.

## Complexity Tracking

Sin violaciones de la constitución que justificar.
