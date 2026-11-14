# Contrato: órdenes de administración

**Requisitos**: FR-039, FR-040, FR-041, FR-042 | **Decisiones**: [research.md D15–D17](../research.md)

Órdenes para el administrador técnico, ejecutadas en el servidor dentro del contenedor de la aplicación:

```bash
docker compose exec app python -m presupuestos <orden> [opciones]
```

Todas escriben mensajes en español y terminan con código 0 si van bien y distinto de 0 si fallan. Nunca muestran contraseñas.

## `crear-titular` — FR-040

```bash
python -m presupuestos crear-titular --nombre "Laura Gómez" --email laura@ejemplo.es
```

- Pide la contraseña por teclado dos veces, sin mostrarla (≥ 10 caracteres).
- Falla si ya existe un titular: «Ya existe una cuenta de titular».

## `restablecer-titular` — FR-039

```bash
python -m presupuestos restablecer-titular
```

- Pide la contraseña nueva dos veces, sin mostrarla.
- Cierra todas las sesiones del titular y borra su bloqueo por intentos fallidos.

## `copia` — FR-041

```bash
python -m presupuestos copia --destino /copias
```

- Crea `/copias/presupuestospro-AAAA-MM-DD.db` con la copia en caliente de SQLite (consistente aunque haya gente trabajando).
- Comprueba la copia (`PRAGMA integrity_check`) y falla si no es correcta.

### Tarea diaria (cron del servidor)

Ejecuta, cada noche:
1. `copia` (orden anterior), en una carpeta del servidor montada en el contenedor.
2. `rclone copy` de esa carpeta al almacenamiento de objetos en la UE.
3. `rclone delete --min-age 30d` en el destino y limpieza de copias locales de más de 7 días.

Las credenciales de rclone están en su archivo de configuración del servidor, fuera del repositorio (constitución, principio V). El contenido exacto del cron queda en la guía de administración (`docs/administracion.md`).

## Restaurar una copia — FR-042

Procedimiento manual (no hay orden, a propósito: sustituir datos debe ser una decisión consciente):

1. Descargar la copia elegida del almacenamiento con `rclone copy`.
2. `docker compose stop app`.
3. Guardar aparte el archivo actual y sustituirlo por la copia.
4. `docker compose start app`.
5. Entrar en la app y comprobar el último presupuesto.

Pasos detallados en `docs/administracion.md`.
