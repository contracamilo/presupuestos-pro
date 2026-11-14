# Propuestas (fuera de alcance hasta que entren en una spec)

Lista separada que exige la constitución («Alcance y propuestas»): las ideas nuevas se registran aquí y **no se construyen** hasta incluirlas en una spec (`/speckit-specify`). Cada propuesta indica de dónde salió y qué implicaría.

| # | Propuesta | Origen | Implica | Estado |
|---|---|---|---|---|
| P1 | Marcar un presupuesto como **Aceptado** o **Rechazado** | Spec 003, sesión de aclaraciones (Q1); FR-209a dejó las etiquetas diseñadas | Guardar un dato nuevo (columna y paso de actualización de la base de datos), acción en la pantalla del presupuesto, regla de prioridad con «Caducado» | Pendiente |
| P2 | Anunciar al lector de pantalla los cambios que ocurren sin recargar (totales recalculados, cambio de estado, errores de guardado) | Checklist 003, CHK028 | Regiones `aria-live` en los fragmentos que actualiza HTMX; criterios de verificación con lector de pantalla | Pendiente |
| P3 | Indicador visual de «guardando…» mientras un guardado automático está en curso | Checklist 003, CHK002 | Estilo para el estado de petición en curso de HTMX; no requiere datos | Pendiente |
| P4 | Documentar el arranque en local en macOS (`brew install pango` y `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`) | Error al descargar el PDF en local tras la 002 | Solo documentación (`docs/` o README); no cambia la app | Pendiente |
| P5 | Etiqueta «Descargado» en lugar de «Enviado» | Checklist 003, CHK020 | Cambio de una palabra en la spec 003, `dominio/estado.py`, su test y `contracts/estados.md`; decisión de producto | Pendiente de decisión |

## Cómo usar esta lista

- Para abordar una propuesta: `/speckit-specify` con su descripción (nueva feature `00N-…`), o una enmienda a la spec que corresponda si es un ajuste menor.
- Al incorporarla a una spec, cambiar su estado a «En spec NNN» y enlazarla.
- Si se descarta, dejarla con estado «Descartada» y el motivo.
