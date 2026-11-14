# Contrato: estados del presupuesto (etiquetas)

**Requisitos**: FR-209, FR-209a, FR-210, FR-211, US3 | **Decisiones**: [research.md V5, V7, V8](../research.md) | **Regla**: [data-model.md](../data-model.md#estado-del-presupuesto--dato-deducido-no-guardado-fr-209-v7)

## Etiquetas

| Valor | Texto visible | Se muestra en v1.2 | Icono | Forma | Texto / fondo | Contraste |
|---|---|---|---|---|---|---|
| `borrador` | Borrador | Sí | lápiz | Borde discontinuo | `#4d5866` / `#eef0f3` | 6,3:1 |
| `enviado` | Enviado | Sí | avión de papel | Borde continuo | `#1f4e79` / `#e3ecf6` | 7,3:1 |
| `caducado` | Caducado | Sí | reloj | Borde continuo y texto en cursiva | `#8a3d00` / `#fdeedd` | 6,7:1 |
| `aceptado` | Aceptado | No (solo diseño) | check | Borde continuo | `#1b6e3a` / `#e6f4ec` | 5,6:1 |
| `rechazado` | Rechazado | No (solo diseño) | círculo con aspa | Borde continuo | `#b3261e` / `#fbe9e7` | 5,6:1 |

- Tokens en `tokens.css`: `--estado-<valor>-texto`, `--estado-<valor>-fondo`.
- El borde usa el color del texto (contraste ≥ 3:1 frente al fondo de la página: todos ≥ 5,5:1).
- Distinguibles sin color por **texto**, **icono** y, en Borrador y Caducado, **forma** (discontinuo, cursiva).

## Marcado

```html
<span class="estado enviado"><span class="solo-lector">Estado: </span>{icono}Enviado</span>
```

- El icono lleva `aria-hidden="true"`; el lector anuncia «Estado: Enviado».
- Tamaño `--texto-xs`, peso 600, radio `--radio-sm`, alto mínimo 24 px (no es interactiva).

## Dónde aparece

| Lugar | Posición | Actualización |
|---|---|---|
| Historial (`_historial_lista.html`) | En cada elemento, junto al número | Al cargar y al buscar (el fragmento ya se rehace) |
| Pantalla del presupuesto | Junto al número, en el `h1` o justo debajo, dentro de `#estado-presupuesto` | Al cargar; fuera de banda en la respuesta de cambios de cabecera (fechas) |
| PDF | **Nunca** (FR-211) | — |
