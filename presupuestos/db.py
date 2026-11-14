"""Conexión a SQLite, esquema, transacciones y numeración (research.md D3, D10)."""

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from presupuestos.dominio import calculo, fechas

ESQUEMA = Path(__file__).with_name("schema.sql")


def ruta_bd() -> str:
    return os.environ.get("RUTA_BD", "presupuestos.db")


def conectar(ruta: str | None = None) -> sqlite3.Connection:
    # isolation_level=None: modo autocommit; las transacciones se abren a mano.
    conn = sqlite3.connect(ruta or ruta_bd(), isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


# Paso de v1 a v1.1 (research R11). Es una sola columna con valor por defecto: no justifica una
# herramienta de migraciones (constitución, principio I). Los datos existentes no cambian (SC-106).
_V1_A_V2 = (
    "ALTER TABLE clientes ADD COLUMN tipo_documento TEXT NOT NULL DEFAULT '' "
    "CHECK (tipo_documento IN ('', 'nif', 'cif', 'nie', 'nif_iva_ue', 'extranjero'))"
)


def inicializar(ruta: str | None = None) -> None:
    """Base de datos nueva → esquema completo (versión 2). Instalación de v1 → añade tipo_documento."""
    conn = conectar(ruta)
    try:
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        if version == 0:
            conn.executescript(ESQUEMA.read_text(encoding="utf-8"))
        elif version == 1:
            with transaccion_exclusiva(conn):
                conn.execute(_V1_A_V2)
                conn.execute("PRAGMA user_version = 2")
    finally:
        conn.close()


@contextmanager
def transaccion_exclusiva(conn: sqlite3.Connection):
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")


def get_db():
    """Dependencia de FastAPI: una conexión por petición."""
    conn = conectar()
    try:
        yield conn
    finally:
        conn.close()


def ahora_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- presupuestos


def crear_presupuesto(conn: sqlite3.Connection, hoy: str) -> int:
    """Asigna PRE-AAAA-NNN con el año de creación, sin duplicados (FR-010, D10)."""
    anio = int(hoy[:4])
    with transaccion_exclusiva(conn):
        fila = conn.execute("SELECT ultimo FROM contadores WHERE anio = ?", (anio,)).fetchone()
        n = (fila["ultimo"] if fila else 0) + 1
        conn.execute(
            "INSERT INTO contadores (anio, ultimo) VALUES (?, ?) "
            "ON CONFLICT(anio) DO UPDATE SET ultimo = excluded.ultimo",
            (anio, n),
        )
        ajustes = conn.execute("SELECT tipo_iva, dias_validez FROM ajustes WHERE id = 1").fetchone()
        cur = conn.execute(
            "INSERT INTO presupuestos (numero, fecha_creacion, fecha_emision, fecha_validez, "
            "validez_editada_a_mano, tipo_iva, actualizado_en) VALUES (?, ?, ?, ?, 0, ?, ?)",
            (
                f"PRE-{anio}-{n:03d}",
                hoy,
                hoy,
                fechas.sumar_dias(hoy, ajustes["dias_validez"]),
                ajustes["tipo_iva"],
                ahora_utc(),
            ),
        )
        return cur.lastrowid


def leer_perfil(conn: sqlite3.Connection) -> dict:
    return dict(conn.execute("SELECT * FROM perfil WHERE id = 1").fetchone())


def leer_ajustes(conn: sqlite3.Connection) -> dict:
    return dict(conn.execute("SELECT * FROM ajustes WHERE id = 1").fetchone())


def valores_efectivos(presupuesto: dict, perfil: dict, ajustes: dict) -> tuple[dict, bool, int]:
    """Perfil y retención congelados si existen; si no, los actuales (FR-018)."""
    if presupuesto["emisor_congelado"]:
        c = json.loads(presupuesto["emisor_congelado"])
        perfil_ef = {k: c.get(k, "") for k in ("nombre", "nif", "direccion", "email", "telefono")}
        perfil_ef["logo_id"] = c.get("logo_id")
        return perfil_ef, bool(c["retencion_activa"]), int(c["tipo_retencion"])
    return perfil, bool(ajustes["retencion_activa"]), int(ajustes["tipo_retencion"])


def calcular_presupuesto(presupuesto: dict, lineas: list, cliente: dict | None, perfil: dict, ajustes: dict):
    _, retencion_activa, tipo_retencion = valores_efectivos(presupuesto, perfil, ajustes)
    return calculo.calcular(
        lineas,
        presupuesto["tipo_iva"],
        cliente,
        retencion_activa,
        tipo_retencion,
        ajustes["mencion_canarias"],
    )


def cargar_presupuesto(conn: sqlite3.Connection, id_: int) -> dict | None:
    fila = conn.execute("SELECT * FROM presupuestos WHERE id = ?", (id_,)).fetchone()
    if fila is None:
        return None
    presupuesto = dict(fila)
    lineas = [
        dict(l)
        for l in conn.execute(
            "SELECT * FROM lineas WHERE presupuesto_id = ? ORDER BY posicion, id", (id_,)
        )
    ]
    cliente = None
    if presupuesto["cliente_id"] is not None:
        c = conn.execute("SELECT * FROM clientes WHERE id = ?", (presupuesto["cliente_id"],)).fetchone()
        cliente = dict(c) if c else None
    perfil = leer_perfil(conn)
    ajustes = leer_ajustes(conn)
    perfil_ef, retencion_activa, tipo_retencion = valores_efectivos(presupuesto, perfil, ajustes)
    return {
        "presupuesto": presupuesto,
        "lineas": lineas,
        "cliente": cliente,
        "perfil": perfil,
        "ajustes": ajustes,
        "perfil_efectivo": perfil_ef,
        "retencion_activa": retencion_activa,
        "tipo_retencion": tipo_retencion,
        "calculo": calcular_presupuesto(presupuesto, lineas, cliente, perfil, ajustes),
    }
