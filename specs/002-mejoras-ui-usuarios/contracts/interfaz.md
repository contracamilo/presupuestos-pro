# Contrato: interfaz (menú, controles de formulario)

**Requisitos**: FR-101 a FR-105, FR-111 a FR-116 | **Decisiones**: [research.md R1–R3, R7–R10](../research.md)

Describe lo que el usuario ve y puede hacer; sirve de referencia para las plantillas y para la guía de verificación.

## Menú lateral (FR-101 a FR-104)

### Estructura

| Grupo | Entrada | Destino | Visible para | Resaltada cuando la ruta es |
|---|---|---|---|---|
| **Trabajo** | Presupuestos | `/` | Todos | `/`, `/presupuestos/*` |
| | Clientes | `/clientes` | Todos | `/clientes*` |
| | Catálogo | `/catalogo` | Todos | `/catalogo*` |
| **Configuración** | Perfil | `/perfil` | Todos | `/perfil*` |
| | Ajustes | `/ajustes` | Todos | `/ajustes` |
| | Usuarios | `/usuarios` | Solo titular | `/usuarios*` |
| | Mi cuenta | `/mi-cuenta` | Todos | `/mi-cuenta*` |
| | Exportar | `/exportar` | Todos | — (descarga) |
| | **Tema** *(ampliación 2026-11-17)* | `POST /tema` | Todos | — (selector, no enlace) |
| — | Salir | `POST /salir` | Todos | — |

- «Exportar» lo retiró después del menú la spec 004 (pasó a un botón «Exportar…» con ventana); se mantiene aquí como registro de la v1.1.
- El selector «Tema» (Claro / Oscuro / Como el sistema) va al final de «Configuración», antes de «Salir». Comportamiento, ruta, cookie y paleta: [tema.md](./tema.md).
- No se muestra en `/entrar`, `/crear-titular` ni en páginas de error sin sesión.
- La entrada resaltada lleva `aria-current="page"` y un estilo visible distinto (no solo color).

### Comportamiento por ancho

| Ancho | Menú | Cabecera |
|---|---|---|
| ≥ 1024 px | Fijo a la izquierda, siempre visible; el contenido ocupa el resto | Marca «PresupuestosPro» |
| < 1024 px (móvil y tableta) | Oculto; al abrirse se superpone al contenido con fondo oscurecido | Marca + botón de menú (icono ☰) |

### Botón de menú (< 1024 px)

| Acción | Resultado |
|---|---|
| Pulsar el botón (o Intro/Espacio con foco) | Abre el menú; `aria-expanded="true"`; etiqueta «Cerrar menú»; el foco pasa a la primera entrada; el fondo no se desplaza |
| Pulsar de nuevo el botón, pulsar fuera del menú o Escape | Cierra; `aria-expanded="false"`; etiqueta «Abrir menú»; el foco vuelve al botón |
| Elegir una entrada | Navega y el menú queda cerrado en la página nueva |

## Pantalla de presupuesto — volver (FR-105)

- Primer elemento del contenido: enlace con aspecto de botón «← Volver al historial».
- Si hay guardados en curso, espera a que terminen antes de navegar; si alguno falla, muestra el aviso «No se ha podido guardar. Comprueba tu conexión.» y no navega (R3). Lo mismo para las entradas del menú desde esta pantalla.

## Formulario de cliente (FR-111 a FR-114)

Orden de campos: Nombre · Categoría · Territorio · [NIF-IVA verificado, solo UE] · Tipo de documento · Número de documento · País · Dirección · Email.

| Campo | Control | Opciones |
|---|---|---|
| Categoría | Selector | Empresa/autónomo · Particular (sin cambios) |
| Territorio | Selector | Sin cambios (Particular solo España) |
| Tipo de documento | Selector | Según [data-model.md](../data-model.md#tipos-de-documento-permitidos--dominiodocumentopy-r7); primera opción «Sin indicar» |
| Número de documento | Texto | Sin cambios (antes «NIF/NIE o NIF-IVA») |
| País | Selector | Según territorio ([data-model.md](../data-model.md#países-permitidos--dominiopaisespy-r8)); en España, fijo y desactivado; valor de v1 fuera de la lista → opción «Revisar país: <texto>» seleccionada |

Al cambiar categoría o territorio, el selector de tipo de documento y el de país se rehacen al instante (sin recargar) y el número de documento se conserva.

## Fechas del presupuesto (FR-115)

| Campo | Control | Restricción |
|---|---|---|
| Fecha de emisión | Calendario del navegador | — |
| Válido hasta | Calendario del navegador | No permite días anteriores a la emisión (`min`) |

Navegador sin calendario: campo de texto que acepta DD/MM/AAAA con los mensajes de la 001.

## Usuarios (FR-106, FR-107)

- Tabla/lista: Nombre · Email · Tipo (Titular/Asistente) · Estado (Activa/Dada de baja) · Acciones (solo asistentes activos: «Restablecer contraseña», «Dar de baja»).
- Botón «Añadir usuario» que despliega: Nombre · Email · Contraseña · Repetir contraseña · «Dar de alta».
- Cada error aparece debajo de su campo, enlazado con `aria-describedby`.

## Crear la cuenta del titular (FR-108)

- Título «Crear la cuenta del titular» y texto breve: «Esta cuenta tendrá acceso a todos los datos y podrá dar de alta a otros usuarios.»
- Campos: Nombre · Email · Contraseña (mínimo 10 caracteres) · Repetir contraseña · «Crear cuenta».

## Perfil — logo (FR-116)

| Estado | Se muestra |
|---|---|
| Sin logo | Título «Logo (aparece en tus PDF)», texto «PNG, JPG o SVG, hasta 2 MB», botón «Subir logo» |
| Con logo | Título, vista previa, «Cambiar logo» y «Quitar logo» (pide confirmación: «¿Quitar el logo? Los presupuestos ya descargados lo conservan.») |

La vista previa se muestra siempre sobre fondo blanco, también en el tema oscuro (FR-129, [tema.md](./tema.md#vista-previa-del-logo-fr-129)).
