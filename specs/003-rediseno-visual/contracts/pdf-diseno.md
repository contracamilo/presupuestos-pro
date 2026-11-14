# Contrato: diseño del PDF del presupuesto

**Requisitos**: FR-208, FR-211, FR-217, US2 | **Decisión**: [research.md V10](../research.md#v10-pdf-con-el-mismo-sistema-visual--fr-217-fr-211-us2-clarifications-q4)

**El contenido no cambia.** Bloques, textos, orden, formato de importes y fechas, paginación y nombre de archivo: los del [contrato del PDF de la 001](../../001-presupuestos-pro/contracts/pdf-presupuesto.md). Este documento solo fija el aspecto.

## Página

- A4, márgenes 18 mm laterales y 16 mm arriba y abajo.
- Tipografía Inter (la de la app), texto base 9,5 pt, interlineado 1,4, color `--color-texto`.
- Sin numeración de páginas (sigue sin pedirse).

## Bloques

| # | Bloque | Aspecto |
|---|---|---|
| 1 | Cabecera | Dos columnas: logo a la izquierda en caja máx. 60 × 25 mm (`object-fit: contain`); datos del emisor a la derecha, nombre en 11 pt 600 y el resto en 8,5 pt `--color-texto-suave`. Sin logo: el emisor ocupa la cabecera alineado a la derecha, sin hueco. Separador inferior gris de 0,5 pt. |
| 2 | Título | «PRESUPUESTO» + número en 18 pt 700, **color de marca**, espaciado de letras 0,04 em. |
| 3 | Fechas | 9 pt `--color-texto-suave`, en una línea bajo el título. |
| 4 | Cliente | Etiqueta «Cliente» en 7,5 pt mayúsculas 600 `--color-texto-suave`; nombre en 10,5 pt 600; resto en 9 pt. Sin recuadro ni fondo de color: filete izquierdo gris de 1 pt (`--color-borde-control`) y relleno izquierdo de 3 mm. |
| 5 | Líneas | Cabecera en 7,5 pt mayúsculas 600, **color de marca**, filete inferior de 1 pt de marca; repetida en cada página. Filas con separador gris de 0,3 pt (sin fondo alterno). Columnas Cantidad, Precio unitario e Importe a la derecha con cifras tabulares. Ninguna fila se parte entre páginas. |
| 6 | Desglose | Alineado a la derecha, ancho ~45 %. Filas normales en 9,5 pt; «Total» en 13 pt 700, separado por un **filete superior de 1,5 pt de color de marca** y 2 mm de aire. No se parte entre páginas. |
| 7 | Mención legal | 8,5 pt cursiva `--color-texto-suave`. |
| 8 | Notas | Título «Notas y condiciones» en 9 pt 600; texto en 9 pt; respeta saltos de línea. |

## Color

- Color de marca **solo** en: título con el número, cabecera de la tabla de líneas (texto y filete) y filete del «Total» (Clarifications Q4).
- Todo lo demás en `--color-texto`, `--color-texto-suave` y grises de separación. El logo del autónomo conserva sus colores.
- Impreso en blanco y negro: la jerarquía se mantiene por tamaño y peso (SC-207).
- Ninguna etiqueta de estado (FR-211).

## Fuentes en el generador

- Las cuatro fuentes WOFF2 se insertan como `data:` en el CSS común (research V10). El generador sigue aceptando solo `data:` (D6 de la 001).
