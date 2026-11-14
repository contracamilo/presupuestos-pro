# Contrato: sistema visual (tokens y componentes)

**Requisitos**: FR-201 a FR-208, FR-212 a FR-214, FR-216, US1, US4 | **Decisiones**: [research.md V1–V6, V8, V9](../research.md)

Referencia para escribir `tokens.css`, `estilos.css` y las plantillas, y para revisar la entrega con [quickstart.md](../quickstart.md).

## Regla de oro

- **Todos** los colores, tamaños de letra, separaciones, radios, sombras y anchos se definen **solo** en `presupuestos/static/tokens.css`.
- `estilos.css` y el `<style>` de `pdf.html` solo usan `var(--…)`. Excepciones permitidas: `0`, `100%`, `1px`/`2px`/`3px` de grosores de borde y foco, `transparent`, `currentColor`, `inherit`.

## Tokens

### Color

| Token | Valor |
|---|---|
| `--color-texto` | `#1a1f26` |
| `--color-texto-suave` | `#4d5866` |
| `--color-marca` | `#1f4e79` |
| `--color-marca-hover` | `#173b5c` (botón principal al pasar el ratón) |
| `--color-marca-claro` | `#e3ecf6` (fondo de la sección actual del menú y de la etiqueta Enviado) |
| `--color-borde-control` | `#7b8794` |
| `--color-borde` | `#d5dae0` |
| `--color-fondo` | `#ffffff` |
| `--color-fondo-2` | `#f4f6f8` |
| `--color-superposicion` | `rgba(26, 31, 38, .5)` (fondo del menú en móvil) |
| `--color-sobre-marca` | `#ffffff` (texto sobre el color de marca y sobre el aviso de conexión) |
| `--color-sombra` | `rgba(26, 31, 38, .08)` (base de `--sombra`) |
| `--color-exito` / `--color-exito-fondo` | `#1b6e3a` / `#e6f4ec` |
| `--color-aviso` / `--color-aviso-fondo` | `#7a4f00` / `#fff4d6` |
| `--color-error` / `--color-error-fondo` | `#b3261e` / `#fbe9e7` |
| `--estado-*-texto` / `--estado-*-fondo` | Ver [estados.md](./estados.md) |

### Tipografía

| Token | Valor |
|---|---|
| `--fuente` | `"Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` |
| `--texto-xs` … `--texto-2xl` | 0,8125 · 0,875 · 1 · 1,25 · 1,5 · 1,875 rem (research V3) |
| `--peso-normal` / `--peso-medio` / `--peso-fuerte` | 400 / 600 / 700 |
| `--interlineado` / `--interlineado-titulo` | 1,5 / 1,25 |
| `--espaciado-mayusculas` | 0,06 em (etiquetas en mayúsculas) |

### Espaciado y forma

| Token | Valor |
|---|---|
| `--esp-1` … `--esp-7` | 4 · 8 · 12 · 16 · 24 · 32 · 48 px (en `rem`: 0,25 … 3) |
| `--radio-sm` / `--radio-md` | 4 px / 8 px |
| `--sombra` | `0 1px 2px rgba(26,31,38,.08), 0 2px 8px rgba(26,31,38,.06)` |
| `--ancho-contenido` | 60 rem |
| `--ancho-menu` | 13,75 rem (220 px) |
| `--alto-control` | 2,75 rem (44 px) |
| `--transicion` | 0,2 s (apertura del menú; se anula con «reducir movimiento») |

## Espaciado

| Entre… | Token |
|---|---|
| Etiqueta y su campo | `--esp-1` |
| Campo y su ayuda o error | `--esp-1` |
| Un campo y el siguiente | `--esp-4` |
| Título de sección y su contenido | `--esp-3` |
| Una sección y la siguiente | `--esp-6` |
| Elementos de una lista | `--esp-2` |
| Relleno de tarjetas y elementos de lista | `--esp-3` (móvil) · `--esp-4` (≥ 760 px) |
| Margen lateral de la página | `--esp-4` (móvil) · `--esp-6` (≥ 1024 px) |
| Botones dentro de un grupo | `--esp-2` |

## Jerarquía (FR-204)

| Nivel | Elemento | Estilo |
|---|---|---|
| Título de pantalla | `h1` (uno por pantalla) | `--texto-xl` (móvil) / `--texto-2xl` (≥ 1024 px), 700, `--color-texto` |
| Título de sección | `h2` | `--texto-lg`, 600 |
| Subtítulo | `h3` | `--texto-base`, 600 |
| Texto | `p`, celdas | `--texto-base`, 400 |
| Secundario | `.suave`, `.ayuda` | `--texto-sm`, `--color-texto-suave` |
| Etiqueta de grupo | `.grupo-menu`, cabeceras de tabla | `--texto-xs`, 600, mayúsculas, espaciado 0,06 em, `--color-texto-suave` |

## Componentes

| Componente | Clases | Reglas |
|---|---|---|
| Botón principal | `.boton` (en `<button>` o `<a>`) | Fondo `--color-marca`, texto blanco, alto `--alto-control`, radio `--radio-md`, peso 600. Uno por grupo de acciones como norma |
| Botón secundario | `.boton.secundario` | Fondo blanco, texto `--color-marca`, borde `--color-borde-control` |
| Botón de peligro | `.boton.peligro` | Fondo blanco, texto y borde `--color-error` |
| Botón de icono | `.boton-menu` | 44 × 44 px, con `aria-label` |
| Volver | `.boton-volver` | Variante secundaria con «←» (002) |
| Campo | `input`, `select`, `textarea` | Alto `--alto-control` (salvo `textarea`), borde 1 px `--color-borde-control`, radio `--radio-sm`, ancho 100 % |
| Etiqueta | `label` | Encima del campo, `--texto-sm`, 600 |
| Ayuda | `.ayuda` | Debajo del campo, `--texto-sm`, `--color-texto-suave` |
| Error de campo | `.error-campo` + `aria-invalid="true"` en el campo | Debajo, `--texto-sm`, `--color-error`, icono de aviso; borde del campo 2 px `--color-error` |
| Mensaje | `.mensaje.exito` · `.mensaje.aviso` · `.mensaje.error` | Fondo `--color-*-fondo`, texto `--color-*`, filete izquierdo 4 px, icono + texto, `role="status"` (éxito, aviso) o `role="alert"` (error) |
| Lista | `.lista > li` | Tarjeta con borde `--color-borde`, radio `--radio-md`; desde 760 px, filas |
| Tabla | `.tabla` | Cabeceras `th scope="col"` en estilo «etiqueta de grupo», filas con separador `--color-borde`, importes a la derecha |
| Importe | `.importe` | `font-variant-numeric: tabular-nums`, alineado a la derecha, sin cortes |
| Totales | `.totales` | Filas `th scope="row"` + importe; «Total» en `--texto-lg` 700 con borde superior 2 px `--color-texto` y `--esp-2` de aire |
| Estado | `.estado.<valor>` | [estados.md](./estados.md) |
| Menú lateral | `.menu-lateral`, `.grupo-menu`, `[aria-current="page"]` | Comportamiento de la 002 sin cambios; colores y espaciado de los tokens |
| Saltar al contenido | `.saltar` | Oculto hasta el foco; al enfocarse, arriba a la izquierda, botón principal |
| Solo lectores | `.solo-lector` | Recorte accesible (no `display: none`) |

### Estados interactivos (todos los controles)

| Estado | Aspecto |
|---|---|
| Foco (`:focus-visible`) | Contorno 3 px `--color-marca` con separación de 2 px |
| Pasar el ratón | Botón principal con fondo `--color-marca-hover`; secundario con fondo `--color-fondo-2` |
| Desactivado | Sin opacidad: fondo `--color-fondo-2`, texto `--color-texto-suave` (6,7:1) y borde `--color-borde-control` (3,7:1 sobre blanco), en todas las variantes; cursor «no permitido» |

## Puntos de corte (mobile-first, FR-216)

| Desde | Cambio |
|---|---|
| 320 px | Mínimo soportado (zoom 200 %, FR-214) |
| 640 px | Rejillas de formulario a dos columnas |
| 760 px | Listas y líneas del presupuesto en filas |
| 1024 px | Menú lateral fijo (002), `h1` en `--texto-2xl`, márgenes `--esp-6` |

## Pares de contraste

Lista que comprueba `tests/test_paleta.py` (research V12) y la guía de verificación:

| Primer plano | Fondo | Mínimo |
|---|---|---|
| `--color-texto` | `--color-fondo`, `--color-fondo-2` | 4,5 |
| `--color-texto-suave` | `--color-fondo`, `--color-fondo-2` | 4,5 |
| `--color-marca` | `--color-fondo`, `--color-fondo-2`, `--color-marca-claro` | 4,5 |
| `--color-sobre-marca` | `--color-marca`, `--color-marca-hover`, `--color-error` | 4,5 |
| `--color-borde-control` | `--color-fondo` | 3 |
| `--color-exito` | `--color-fondo`, `--color-exito-fondo` | 4,5 |
| `--color-aviso` | `--color-aviso-fondo` | 4,5 |
| `--color-error` | `--color-fondo`, `--color-error-fondo` | 4,5 |
| `--estado-<v>-texto` | `--estado-<v>-fondo` (los cinco) | 4,5 |

## Textos nuevos (FR-215)

| Texto | Dónde |
|---|---|
| «Saltar al contenido» | Inicio de cada pantalla con sesión |
| «Totales del presupuesto» | Título de la tabla de totales, solo para lectores (FR-214: tablas con cabeceras) |
| «Borrador», «Enviado», «Caducado» (y «Aceptado», «Rechazado», solo diseñados) | Etiquetas de estado |
| «Estado: » | Antes de la etiqueta, solo para lectores |
| «Error: », «Aviso: », «Hecho: » | Antes de mensajes, solo para lectores (el icono lo indica visualmente) |
