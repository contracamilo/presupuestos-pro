# Contrato: archivo .zip

**Requisitos**: FR-302, FR-303, FR-307, FR-308 | **Sustituye a**: [archivo-exportacion.md de la 001](../../001-presupuestos-pro/contracts/archivo-exportacion.md) (el JSON suelto ya no se descarga) | **Decisiones**: [research.md](../research.md) E5, E8, E9 (retirada por D-004-1)

> **Revisión D-004-1**: el zip lleva **solo los PDF**. El archivo de datos (JSON) con su campo `alcance` se retiró tras probar la ventana: un autónomo no técnico no lo usaría. Ver la aclaración «decisión D-004-1» de [spec.md](../spec.md).

## El zip

| | «Todo» | «Seleccionar» |
|---|---|---|
| Nombre | `presupuestospro-copia-AAAA-MM-DD.zip` | `presupuestospro-seleccion-AAAA-MM-DD.zip` |
| Fecha | día de la exportación, en España | ídem |

Contenido (sin carpetas, nada más):

```text
PRE-2026-001 - Estudio García.pdf                # uno por presupuesto exportable (o marcado)
PRE-2026-002 - Diseño Web S.L.pdf
```

- **Nombre del PDF**: `«{número} - {cliente}.pdf»`. En el cliente, `/ \ : * ? " < > |` y los caracteres de control se sustituyen por un espacio; se colapsan espacios y se quitan puntos y espacios en los extremos; se conservan tildes y «ñ»; máximo 80 caracteres; si queda vacío, «Sin cliente». Entradas en UTF-8.
- **PDF**: el mismo documento que la descarga individual (mismas reglas, mismo emisor fijado, mismos importes).
- **Orden** de las entradas: por número de presupuesto.
- **Qué entra**: solo los presupuestos *exportables* (ya descargados y con PDF generable hoy). Los borradores y los presupuestos sin PDF no se exportan.

## Lo que NO incluye (nunca)

Archivo de datos (JSON), cuentas, sesiones ni nada relacionado con contraseñas (FR-036 de la 001).

## Importación

Fuera de alcance. Si una futura spec la necesita, definirá su propio formato de datos.
