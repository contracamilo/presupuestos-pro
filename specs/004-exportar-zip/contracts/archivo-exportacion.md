# Contrato: archivo .zip y archivo de datos

**Requisitos**: FR-302, FR-303, FR-306, FR-306a, FR-307, FR-308 | **Sustituye a**: [archivo-exportacion.md de la 001](../../001-presupuestos-pro/contracts/archivo-exportacion.md) (el JSON suelto ya no se descarga) | **Decisiones**: [research.md](../research.md) E5, E8, E9

## El zip

| | «Todo» | «Seleccionar» |
|---|---|---|
| Nombre | `presupuestospro-copia-AAAA-MM-DD.zip` | `presupuestospro-seleccion-AAAA-MM-DD.zip` |
| Fecha | día de la exportación, en España | ídem |

Contenido (sin carpetas, nada más):

```text
presupuestospro-copia-2026-03-15.json            # archivo de datos (mismo nombre base que el zip)
PRE-2026-001 - Estudio García.pdf                # uno por presupuesto exportable (o marcado)
PRE-2026-002 - Diseño Web S.L.pdf
```

- **Nombre del PDF**: `«{número} - {cliente}.pdf»`. En el cliente, `/ \ : * ? " < > |` y los caracteres de control se sustituyen por un espacio; se colapsan espacios y se quitan puntos y espacios en los extremos; se conservan tildes y «ñ»; máximo 80 caracteres; si queda vacío, «Sin cliente». Entradas en UTF-8.
- **PDF**: el mismo documento que la descarga individual (mismas reglas, mismo emisor fijado, mismos importes).

## El archivo de datos

JSON, UTF-8, `formato: "presupuestospro"`, `version: 2`. Mismas claves que la exportación actual más `alcance`.

```json
{
  "formato": "presupuestospro",
  "version": 2,
  "alcance": "completo",
  "exportado_en": "2026-03-15T10:30:00Z",
  "datos": {
    "perfil": { "…": "…" },  "ajustes": { "…": "…" },
    "logos": [], "servicios": [], "clientes": [], "presupuestos": [], "contadores": []
  }
}
```

| Clave | `alcance: "completo"` | `alcance: "seleccion"` |
|---|---|---|
| `perfil`, `ajustes` | objetos | `null` |
| `servicios`, `contadores` | todos | `[]` |
| `clientes` | todos | solo los de los presupuestos marcados |
| `presupuestos` (con `lineas` y `emisor_congelado`) | todos, incluidos borradores | solo los marcados |
| `logos` | todos | solo los referenciados por el emisor fijado de los marcados |

Campos de cada elemento: idénticos a [data-model.md de la 001](../../001-presupuestos-pro/data-model.md) y a la exportación actual (`tipo_documento`, `anonimizado`, etc.), sí/no como `true`/`false` y logos en base64.

## Lo que NO incluye (nunca)

`usuarios`, `sesiones`, `intentos_acceso`: nada de cuentas ni huellas de contraseñas (FR-306, FR-036 de la 001).

## Importación

Fuera de alcance. El campo `alcance` permitirá a la futura spec de importación distinguir una copia completa de una parcial.
