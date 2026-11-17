# Contrato: tema (modo oscuro)

**Requisitos**: FR-117 a FR-130 | **Decisiones**: [research.md R12–R18](../research.md#ampliación-2026-11-17-modo-oscuro-us7-fr-117-a-fr-130)

Qué ve y puede hacer el usuario, cómo se recuerda la elección y qué valores tiene la paleta oscura. Sirve de referencia para las plantillas, los tests y la guía de verificación.

## Selector «Tema» (FR-117 a FR-120)

- **Dónde**: menú lateral, al final del grupo «Configuración», justo antes de «Salir». En < 1024 px, dentro del menú desplegable. No aparece en pantallas sin sesión (las que no tienen menú).
- **Marcado**: formulario con un grupo «Tema» (`<fieldset>` + `<legend>Tema</legend>`) de tres botones de opción, en este orden:

  | Opción | Valor |
  |---|---|
  | Claro | `claro` |
  | Oscuro | `oscuro` |
  | Como el sistema | `sistema` |

  Marcada: la del tema actual (`sistema` si no hay elección). Debajo, botón «Aplicar» (visible solo si JavaScript no se ejecuta).
- **Teclado y lector de pantalla**: Tab entra en el grupo y las flechas cambian de opción; se anuncia «Tema», la opción y su estado. El foco es visible en los dos temas (FR-213 de la 003).

| Acción | Con JavaScript | Sin JavaScript |
|---|---|---|
| Elegir una opción | La página cambia de tema en el momento; no se recarga ni se pierde nada escrito; se guarda la elección en segundo plano | Se marca la opción |
| Pulsar «Aplicar» | (oculto) | Se guarda la elección y se recarga la misma pantalla con el tema nuevo |
| El guardado falla (sin conexión) | El tema queda aplicado en la página y aparece «No se ha podido guardar. Comprueba tu conexión.»; al recargar vuelve el tema guardado antes | El navegador muestra su error de conexión |

## Ruta

Sobre [cambios-rutas-y-pantallas.md](./cambios-rutas-y-pantallas.md) y las reglas comunes de la 001 (sesión, origen, cabeceras).

| Método y ruta | Campos | Resultado |
|---|---|---|
| `POST /tema` **(nueva)** | `tema` (`claro` \| `oscuro` \| `sistema`), `volver` (opcional) | Pone la cookie `tema`. Petición de `app.js` (cabecera `X-Tema-Fetch: 1`, ver nota) → **204**. Formulario normal → **303** a `volver` si es una ruta interna (empieza por `/` y no por `//`), si no a `/`. Valor de `tema` desconocido → **422**. Sin sesión → como el resto (303 a `/entrar`). Origen ajeno → 403 (D9) |

Nota: `app.js` envía el formulario con la cabecera `X-Tema-Fetch: 1` para distinguirlo del envío sin JS; no es una petición HTMX y no cuenta como guardado pendiente (R3).

## Cookie `tema` (FR-121, FR-122)

| Atributo | Valor |
|---|---|
| Nombre / valor | `tema` = `claro` \| `oscuro` \| `sistema` |
| Duración | 400 días (`Max-Age=34560000`) |
| Ámbito | `Path=/`, `SameSite=Lax`, `HttpOnly`, `Secure` salvo con `COOKIE_SEGURA=0` |

- No se guarda nada en la base de datos. Cerrar sesión no borra la cookie: al volver a entrar en ese dispositivo se aplica de nuevo.
- Sin cookie, con un valor desconocido o en una página **sin sesión** → se trata como `sistema` (FR-122, FR-124).

## Cómo se pinta cada página (FR-123, FR-125, FR-126)

En `base.html`, en este orden: `tokens.css`, `tokens-oscuro.css` (con `media` según la tabla), `estilos.css`.

| Tema calculado | `<link id="tokens-oscuro" media=…>` | `<meta name="color-scheme" content=…>` | Resultado |
|---|---|---|---|
| `claro` | `not all` | `light` | Siempre claro |
| `oscuro` | `all` | `dark` | Siempre oscuro, incluidos los controles del navegador |
| `sistema` | `(prefers-color-scheme: dark)` | `light dark` | Sigue al dispositivo y cambia solo si el dispositivo cambia con la app abierta |

`app.js`, al cambiar la opción, aplica la misma tabla sobre la página abierta.

El PDF no usa `base.html` ni `tokens-oscuro.css`: sale siempre con la paleta clara (FR-130).

## Paleta oscura

`static/tokens-oscuro.css`: un único bloque `:root` con `color-scheme: dark` y **todas** las variables de color de `tokens.css` excepto `--color-fondo-logo`. Nada más (ni tamaños, ni tipografía, ni separaciones).

| Variable | Claro (`tokens.css`, sin cambios) | Oscuro (`tokens-oscuro.css`) |
|---|---|---|
| `--color-texto` | `#1a1f26` | `#e6e9ee` |
| `--color-texto-suave` | `#4d5866` | `#a9b3bf` |
| `--color-marca` | `#1f4e79` | `#7fb2e5` |
| `--color-marca-hover` | `#173b5c` | `#a5c9ee` |
| `--color-marca-claro` | `#e3ecf6` | `#1d3349` |
| `--color-borde-control` | `#7b8794` | `#7d8a99` |
| `--color-borde` | `#d5dae0` | `#323b46` |
| `--color-fondo` | `#ffffff` | `#14191f` |
| `--color-fondo-2` | `#f4f6f8` | `#1c232b` |
| `--color-sobre-marca` | `#ffffff` | `#0d1620` |
| `--color-superposicion` | `rgba(26, 31, 38, .5)` | `rgba(0, 0, 0, .6)` |
| `--color-sombra` | `rgba(26, 31, 38, .08)` | `rgba(0, 0, 0, .4)` |
| `--color-exito` / `-fondo` | `#1b6e3a` / `#e6f4ec` | `#6fcf97` / `#16301f` |
| `--color-aviso` / `-fondo` | `#7a4f00` / `#fff4d6` | `#f2c46d` / `#33270f` |
| `--color-error` / `-fondo` | `#b3261e` / `#fbe9e7` | `#ff8a80` / `#3a1a18` |
| `--estado-borrador-texto` / `-fondo` | `#4d5866` / `#eef0f3` | `#b8c1cc` / `#262d36` |
| `--estado-enviado-texto` / `-fondo` | `#1f4e79` / `#e3ecf6` | `#8fbde9` / `#1d3349` |
| `--estado-caducado-texto` / `-fondo` | `#8a3d00` / `#fdeedd` | `#f5a962` / `#3a2412` |
| `--estado-aceptado-texto` / `-fondo` | `#1b6e3a` / `#e6f4ec` | `#6fcf97` / `#16301f` |
| `--estado-rechazado-texto` / `-fondo` | `#b3261e` / `#fbe9e7` | `#ff8a80` / `#3a1a18` |
| `--color-fondo-logo` **(nuevo)** | `#ffffff` | — (no se redefine: blanco en los dos temas) |

### Pares de contraste en oscuro (FR-127)

Los mismos 26 pares de [sistema-visual.md de la 003](../../003-rediseno-visual/contracts/sistema-visual.md#pares-de-contraste), más uno propio del modo oscuro. Valores calculados con la fórmula WCAG 2.1:

| Par | Mínimo | Oscuro |
|---|---|---|
| `--color-texto` sobre `--color-fondo` / `--color-fondo-2` | 4,5 | 14,52 / 13,03 |
| `--color-texto-suave` sobre `--color-fondo` / `--color-fondo-2` | 4,5 | 8,32 / 7,46 |
| `--color-marca` sobre `--color-fondo` / `--color-fondo-2` / `--color-marca-claro` | 4,5 | 7,91 / 7,10 / 5,80 |
| `--color-sobre-marca` sobre `--color-marca` / `--color-marca-hover` / `--color-error` | 4,5 | 8,16 / 10,57 / 7,98 |
| `--color-borde-control` sobre `--color-fondo` | 3 | 5,02 |
| `--color-exito` sobre `--color-fondo` / `--color-exito-fondo` | 4,5 | 9,30 / 7,48 |
| `--color-aviso` sobre `--color-aviso-fondo` | 4,5 | 8,97 |
| `--color-error` sobre `--color-fondo` / `--color-error-fondo` | 4,5 | 7,74 / 6,86 |
| `--estado-<v>-texto` sobre `--estado-<v>-fondo` (borrador, enviado, caducado, aceptado, rechazado) | 4,5 | 7,64 · 6,55 · 7,45 · 7,48 · 6,86 |
| `--estado-<v>-texto` sobre `--color-fondo` (borde de la etiqueta) | 3 | 9,71 · 8,94 · 9,03 · 9,30 · 7,74 |
| **Nuevo**: `--color-borde-control` sobre `--color-fondo-2` (campos sobre el menú lateral) | 3 | 4,50 |

## Vista previa del logo (FR-129)

`.logo-previa` en Perfil: fondo `var(--color-fondo-logo)` (blanco en los dos temas), relleno `var(--esp-2)` y radio `var(--radio-sm)`. El logo se ve igual que en el PDF.

## Textos nuevos

| Texto | Dónde |
|---|---|
| «Tema» | Título del grupo del selector |
| «Claro», «Oscuro», «Como el sistema» | Opciones |
| «Aplicar» | Botón del selector, solo sin JavaScript |
