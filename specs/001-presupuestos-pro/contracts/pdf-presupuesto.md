# Contrato: PDF del presupuesto

**Requisitos**: FR-021 a FR-025, FR-030, HU2 | **Decisión**: [research.md D6](../research.md#d6-pdf-generado-en-el-servidor-con-weasyprint)

El entregable que recibe el cliente. Se genera en el servidor (`GET /presupuestos/{id}/pdf`). Todo en español de España, importes `1.234,56 €`, fechas `DD/MM/AAAA`.

## Nombre del archivo (FR-022, D19)

`<numero>_<cliente-normalizado>.pdf` — p. ej. `PRE-2026-015_Acme-SL.pdf`; «Peña & Cía» → `PRE-2026-016_Pena-Cia.pdf`.

## Antes de generar (FR-023)

Si falta algo, **no se genera** y se muestra en la pantalla del presupuesto la lista de lo que falta:

- «Completa tu perfil: falta el NIF.»
- «Selecciona un cliente.»
- «Añade al menos una línea.»
- «Completa el NIF del cliente Acme SL.»
- «El cliente de este presupuesto fue eliminado: no se puede descargar.» (FR-043)

En la primera descarga correcta se guarda `emisor_congelado` ([data-model.md](../data-model.md#presupuestos--fr-010-a-fr-019)).

## Contenido, en orden

| # | Bloque | Contenido | Origen |
|---|---|---|---|
| 1 | Cabecera | Logo (si hay) · nombre o razón social · NIF · dirección · email · teléfono (si hay) | Emisor congelado o perfil actual |
| 2 | Título | «PRESUPUESTO» · número | Presupuesto |
| 3 | Fechas | «Fecha de emisión: DD/MM/AAAA» · «Válido hasta el DD/MM/AAAA» | Presupuesto |
| 4 | Cliente | Nombre · NIF · dirección · país · email (los que haya) | Cliente actual |
| 5 | Líneas | Tabla: Descripción · Cantidad · Unidad · Precio unitario · Importe | Líneas + cálculo |
| 6 | Desglose | Base imponible · IVA (X %) · Retención IRPF (−Y %) *solo si aplica* · **Total** | Cálculo |
| 7 | Mención legal | Si aplica (RN6) | Cálculo |
| 8 | Notas | «Notas y condiciones» + texto, si hay | Presupuesto |

```text
Base imponible                 750,00 €
IVA (21 %)                     157,50 €
Retención IRPF (−15 %)        −112,50 €
Total                          795,00 €
```

- La fila de IVA aparece **siempre** (0,00 € si no aplica); la de retención **solo** cuando aplica.
- Cantidades con hasta 2 decimales en formato español (`1,5`).

## Paginación (FR-024, CL8)

- Si las líneas no caben, el PDF continúa en páginas siguientes.
- El encabezado de la tabla de líneas se repite en cada página.
- Desglose, mención y notas aparecen tras la última línea.
- No se añade numeración de páginas: la spec no la pide (principio III).

## Coherencia y seguridad

- Los importes salen de la misma función de cálculo que la pantalla (FR-025).
- El generador no descarga nada de internet; solo usa el logo guardado (D6).
