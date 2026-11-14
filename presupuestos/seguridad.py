"""Contraseñas, sesiones y bloqueo por intentos fallidos (research.md D7, D8)."""

import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from presupuestos.db import ahora_utc

_hasher = PasswordHasher()  # Argon2id
CADUCIDAD = timedelta(hours=8)
BLOQUEO = timedelta(minutes=15)
MAX_FALLOS = 5
LONGITUD_MINIMA = 10
MENSAJE_LONGITUD = "La contraseña debe tener al menos 10 caracteres"
_HASH_FICTICIO = _hasher.hash("contraseña-ficticia-para-igualar-tiempos")


def hash_contrasena(contrasena: str) -> str:
    return _hasher.hash(contrasena)


def verificar_contrasena(hash_guardado: str | None, contrasena: str) -> bool:
    try:
        return _hasher.verify(hash_guardado or _HASH_FICTICIO, contrasena) and hash_guardado is not None
    except (VerificationError, InvalidHashError):
        return False


def validar_longitud(contrasena: str) -> str | None:
    """Devuelve el mensaje de error o None (FR-036)."""
    return MENSAJE_LONGITUD if len(contrasena or "") < LONGITUD_MINIMA else None


def validar_nueva(contrasena: str, repetir: str) -> dict[str, str]:
    """Errores por campo de una contraseña nueva y su repetición (FR-107, R5). Vacío = válida."""
    errores = {}
    if error := validar_longitud(contrasena):
        errores["contrasena"] = error + "."
    if (contrasena or "") != (repetir or ""):
        errores["repetir"] = "Las contraseñas no coinciden."
    return errores


def _huella(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------- sesiones


def crear_sesion(conn: sqlite3.Connection, usuario_id: int) -> str:
    token = secrets.token_urlsafe(32)
    ahora = ahora_utc()
    conn.execute(
        "INSERT INTO sesiones (hash_token, usuario_id, creada_en, ultima_actividad) VALUES (?, ?, ?, ?)",
        (_huella(token), usuario_id, ahora, ahora),
    )
    return token


def usuario_de_sesion(conn: sqlite3.Connection, token: str | None) -> dict | None:
    if not token:
        return None
    huella = _huella(token)
    fila = conn.execute(
        "SELECT s.ultima_actividad, u.id, u.nombre, u.email, u.tipo, u.activo "
        "FROM sesiones s JOIN usuarios u ON u.id = s.usuario_id WHERE s.hash_token = ?",
        (huella,),
    ).fetchone()
    if fila is None:
        return None
    caducada = _ahora() - datetime.fromisoformat(fila["ultima_actividad"]) >= CADUCIDAD
    if caducada or not fila["activo"]:
        conn.execute("DELETE FROM sesiones WHERE hash_token = ?", (huella,))
        return None
    conn.execute("UPDATE sesiones SET ultima_actividad = ? WHERE hash_token = ?", (ahora_utc(), huella))
    return {k: fila[k] for k in ("id", "nombre", "email", "tipo")}


def borrar_sesion(conn: sqlite3.Connection, token: str | None) -> None:
    if token:
        conn.execute("DELETE FROM sesiones WHERE hash_token = ?", (_huella(token),))


def borrar_sesiones_usuario(conn: sqlite3.Connection, usuario_id: int, excepto: str | None = None) -> None:
    if excepto:
        conn.execute(
            "DELETE FROM sesiones WHERE usuario_id = ? AND hash_token <> ?", (usuario_id, _huella(excepto))
        )
    else:
        conn.execute("DELETE FROM sesiones WHERE usuario_id = ?", (usuario_id,))


# ---------------------------------------------------------------- bloqueo (FR-038)


def esta_bloqueado(conn: sqlite3.Connection, email: str) -> bool:
    fila = conn.execute("SELECT bloqueado_hasta FROM intentos_acceso WHERE email = ?", (email,)).fetchone()
    return bool(fila and fila["bloqueado_hasta"] and datetime.fromisoformat(fila["bloqueado_hasta"]) > _ahora())


def registrar_fallo(conn: sqlite3.Connection, email: str) -> None:
    fila = conn.execute("SELECT fallos FROM intentos_acceso WHERE email = ?", (email,)).fetchone()
    fallos = (fila["fallos"] if fila else 0) + 1
    bloqueado_hasta = None
    if fallos >= MAX_FALLOS:
        bloqueado_hasta = (_ahora() + BLOQUEO).isoformat(timespec="seconds")
        fallos = 0
    conn.execute(
        "INSERT INTO intentos_acceso (email, fallos, bloqueado_hasta) VALUES (?, ?, ?) "
        "ON CONFLICT(email) DO UPDATE SET fallos = excluded.fallos, bloqueado_hasta = excluded.bloqueado_hasta",
        (email, fallos, bloqueado_hasta),
    )


def limpiar_intentos(conn: sqlite3.Connection, email: str) -> None:
    conn.execute("DELETE FROM intentos_acceso WHERE email = ?", (email,))
