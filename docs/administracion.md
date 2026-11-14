# Guía del administrador técnico — PresupuestosPro v1

Esta guía es para quien instala y mantiene el servidor de **un** autónomo. Cada autónomo tiene su propia instalación (FR-040). Todas las órdenes se ejecutan en el servidor, en la carpeta del proyecto.

## 1. Instalación

Necesitas un servidor virtual (VPS) pequeño **en la UE** (p. ej. Hetzner, OVH o Scaleway) con Linux, Docker y Docker Compose, y un dominio propio.

1. Apunta el DNS del dominio (registro `A`) a la IP del servidor.
2. Copia el proyecto al servidor (p. ej. `git clone …`) y entra en su carpeta.
3. Crea la configuración local (no se versiona):
   ```bash
   cp .env.example .env
   nano .env          # pon DOMINIO=presupuestos.tudominio.es y deja COOKIE_SEGURA=1
   ```
4. Crea las carpetas de datos y copias con el usuario sin privilegios que usa la app (uid 1000) y arranca:
   ```bash
   mkdir -p datos copias && sudo chown 1000:1000 datos copias
   docker compose up -d --build
   ```
   Caddy obtiene y renueva solo el certificado HTTPS.
5. Abre `https://tu-dominio` nada más arrancar el servidor y crea la cuenta del titular en la pantalla «Crear la cuenta del titular» (nombre, email y contraseña de al menos 10 caracteres, escrita dos veces). Al crearla, la sesión queda iniciada.

   > **Importante**: hasta que crees esa cuenta, cualquiera que conozca la dirección podría crearla. Hazlo inmediatamente después de arrancar. Si al abrir la dirección ves la pantalla de inicio de sesión en lugar de la de creación sin haberla creado tú, reinstala con los datos vacíos.
6. Pulsa «Salir» y comprueba que aparece la pantalla de inicio de sesión y que el titular puede volver a entrar.

Los datos viven en `./datos/presupuestos.db` (un único archivo, incluidos los logos).

## 2. Actualización

```bash
git pull
docker compose up -d --build
```

La carpeta `./datos` no se toca al actualizar. Si la nueva versión necesita cambios en la base de datos, la aplicación los aplica sola al arrancar, sin perder datos (p. ej. al pasar de v1 a v1.1 se añade el tipo de documento de los clientes).

## 3. Copias de seguridad diarias (FR-041)

### 3.1 Configurar rclone (una vez)

Contrata un almacenamiento de objetos compatible con S3 **en la UE y de otro proveedor** distinto del servidor (p. ej. Scaleway Object Storage, OVH Object Storage o Backblaze B2 en región UE). Crea un bucket, p. ej. `presupuestospro-copias`.

En el servidor:

```bash
sudo apt install rclone
rclone config          # crea un remoto llamado "copias" con las claves del almacenamiento
rclone lsd copias:     # debe listar el bucket
```

Las credenciales quedan **solo** en `~/.config/rclone/rclone.conf` del servidor. Nunca las pongas en el repositorio (constitución, principio V).

### 3.2 Programar la tarea diaria

Edita el cron del usuario que gestiona Docker (`crontab -e`) y añade, cambiando la ruta del proyecto:

```cron
# PresupuestosPro: copia diaria a las 03:15, subida fuera del servidor y limpieza
15 3 * * * cd /ruta/al/proyecto && docker compose exec -T app python -m presupuestos copia --destino /copias >> copias/cron.log 2>&1 && rclone copy ./copias copias:presupuestospro-copias --include "*.db" >> copias/cron.log 2>&1 && rclone delete --min-age 30d copias:presupuestospro-copias >> copias/cron.log 2>&1 && find ./copias -name "*.db" -mtime +7 -delete
```

Qué hace:

1. `copia`: copia en caliente y comprobada (`PRAGMA integrity_check`) en `./copias/presupuestospro-AAAA-MM-DD.db`.
2. `rclone copy`: la sube al almacenamiento externo.
3. `rclone delete --min-age 30d`: borra en el almacenamiento las copias de más de 30 días (se conservan 30).
4. `find … -mtime +7 -delete`: en el servidor solo se guardan 7 días de copias locales.

Revisa de vez en cuando `copias/cron.log` y `rclone ls copias:presupuestospro-copias`.

## 4. Restaurar una copia (FR-042)

Restaurar **sustituye** todos los datos por los de la copia. Lo hecho después de esa copia se pierde.

1. Lista las copias disponibles y elige una:
   ```bash
   rclone ls copias:presupuestospro-copias
   ```
2. Descárgala desde el almacenamiento externo:
   ```bash
   rclone copy copias:presupuestospro-copias/presupuestospro-2026-11-14.db ./restaurar/
   ```
3. Para la aplicación:
   ```bash
   docker compose stop app
   ```
4. Guarda aparte el archivo actual y pon la copia en su lugar:
   ```bash
   mv datos/presupuestos.db datos/presupuestos.db.antes-de-restaurar
   rm -f datos/presupuestos.db-wal datos/presupuestos.db-shm
   cp restaurar/presupuestospro-2026-11-14.db datos/presupuestos.db
   ```
5. Arranca la aplicación:
   ```bash
   docker compose start app
   ```
6. Entra en la app y comprueba el historial: deben aparecer los presupuestos hasta la fecha de la copia y no los posteriores.

> **Aviso RGPD**: si restauras una copia anterior a una anonimización de cliente («Anonimizar cliente»), ese cliente vuelve a tener sus datos. **Repite la anonimización** desde la ficha del cliente.

Si algo sale mal, vuelve al archivo guardado en el paso 4 (`presupuestos.db.antes-de-restaurar`).

## 5. Contraseña del titular olvidada (FR-039)

La herramienta no envía emails. El administrador asigna una contraseña nueva:

```bash
docker compose exec app python -m presupuestos restablecer-titular
```

Cierra todas las sesiones del titular y quita el bloqueo por intentos fallidos. Las contraseñas de los asistentes las restablece el titular desde **Usuarios**.

## 6. Recordatorios legales

- Firma un **contrato de encargado del tratamiento** (RGPD) con el proveedor del servidor y con el del almacenamiento de copias. Ambos deben tener los servidores en la UE.
- La tabla de IVA/IRPF por tipo de cliente (RN6), en especial la retención en Canarias, Ceuta y Melilla, debe revisarla un asesor fiscal antes del uso real.
