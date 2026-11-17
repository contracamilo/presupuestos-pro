# Contrato: archivo de exportación

**Requisitos**: FR-029, HU9 | **Decisión**: [research.md D14](../research.md#d14-exportar-fr-029)

Archivo que el titular o un asistente descargan con todos los datos de negocio. **No hay importación desde la app** (la spec la eliminó); la restauración se hace con las copias de seguridad ([cli-administracion.md](./cli-administracion.md)).

## Archivo

> **Sustituido por la spec 004**: la exportación ya no es un JSON suelto por `GET /exportar`, sino un `.zip` solo con PDF por `POST /exportar` (el archivo de datos se retiró, decisión D-004-1). Ver [archivo-exportacion.md de la 004](../../004-exportar-zip/contracts/archivo-exportacion.md).

- **Ruta**: `GET /exportar` (exige sesión).
- **Nombre**: `presupuestospro-copia-AAAA-MM-DD.json`.
- **Formato**: JSON, UTF-8.

## Estructura

```json
{
  "formato": "presupuestospro",
  "version": 1,
  "exportado_en": "2026-11-14T10:30:00Z",
  "datos": {
    "perfil":       { "nombre": "…", "nif": "…", "direccion": "…", "email": "…", "telefono": "…", "logo_id": 3 },
    "ajustes":      { "tipo_iva": 21, "retencion_activa": true, "tipo_retencion": 15, "dias_validez": 30, "mencion_canarias": "" },
    "logos":        [ { "id": 3, "tipo": "image/png", "datos_base64": "…" } ],
    "servicios":    [ { "id": 1, "nombre": "…", "descripcion": "…", "unidad": "hora", "precio_cent": 4500, "archivado": false } ],
    "clientes":     [ { "id": 1, "nombre": "…", "nif": "…", "direccion": "…", "pais": "…", "email": "…",
                        "categoria": "empresa", "territorio": "peninsula", "nif_iva_verificado": false, "archivado": false } ],
    "presupuestos": [ { "id": 1, "numero": "PRE-2026-001", "fecha_creacion": "2026-11-14", "fecha_emision": "2026-11-14",
                        "fecha_validez": "2026-12-14", "validez_editada_a_mano": false, "tipo_iva": 21, "cliente_id": 1,
                        "notas": "…", "emisor_congelado": null,
                        "lineas": [ { "posicion": 1, "descripcion": "…", "unidad": "hora", "cantidad_cent": 1000, "precio_cent": 4500 } ] } ],
    "contadores":   [ { "anio": 2026, "ultimo": 17 } ]
  }
}
```

Campos idénticos a [data-model.md](../data-model.md), con sí/no como `true`/`false` y logos en base64.

## Lo que NO incluye

- `usuarios`, `sesiones` e `intentos_acceso`: el archivo puede acabar en un email o un USB, así que nunca lleva cuentas ni huellas de contraseñas (FR-036).
