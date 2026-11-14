"""Actualización automática de una instalación v1 a v1.1 sin perder datos (SC-106, R11)."""

import sqlite3

import pytest

from presupuestos import db

# Tabla clientes tal como era en v1 (sin tipo_documento).
CLIENTES_V1 = """
CREATE TABLE clientes (
    id                 INTEGER PRIMARY KEY,
    nombre             TEXT NOT NULL,
    nif                TEXT NOT NULL DEFAULT '',
    direccion          TEXT NOT NULL DEFAULT '',
    pais               TEXT NOT NULL DEFAULT '',
    email              TEXT NOT NULL DEFAULT '',
    categoria          TEXT NOT NULL CHECK (categoria IN ('empresa', 'particular')),
    territorio         TEXT NOT NULL CHECK (territorio IN ('peninsula', 'canarias', 'ue', 'fuera_ue')),
    nif_iva_verificado INTEGER NOT NULL DEFAULT 0,
    archivado          INTEGER NOT NULL DEFAULT 0,
    anonimizado        INTEGER NOT NULL DEFAULT 0,
    CHECK (categoria = 'empresa' OR territorio IN ('peninsula', 'canarias')),
    CHECK (nif_iva_verificado = 0 OR territorio = 'ue')
);
"""


def _crear_bd_v1(ruta: str) -> None:
    """Esquema actual con la tabla clientes de v1 y user_version = 1, con datos."""
    esquema = db.ESQUEMA.read_text(encoding="utf-8")
    inicio = esquema.index("CREATE TABLE IF NOT EXISTS clientes")
    fin = esquema.index(");", inicio) + 2
    esquema_v1 = esquema[:inicio] + CLIENTES_V1 + esquema[fin:]
    esquema_v1 = esquema_v1.replace("PRAGMA user_version = 2;", "PRAGMA user_version = 1;")
    c = sqlite3.connect(ruta)
    try:
        c.executescript(esquema_v1)
        c.execute(
            "INSERT INTO clientes (id, nombre, nif, direccion, pais, email, categoria, territorio, nif_iva_verificado) "
            "VALUES (1, 'Acme GmbH', 'DE123456789', 'Hauptstraße 1', 'Alemania (Berlín)', 'a@acme.de', "
            "'empresa', 'ue', 1)"
        )
        c.execute(
            "INSERT INTO presupuestos (id, numero, fecha_creacion, fecha_emision, fecha_validez, tipo_iva, "
            "cliente_id, notas, actualizado_en) VALUES (1, 'PRE-2026-001', '2026-11-01', '2026-11-01', "
            "'2026-12-01', 21, 1, 'Pago a 30 días', '2026-11-01T10:00:00+00:00')"
        )
        c.execute("INSERT INTO lineas (presupuesto_id, posicion, descripcion, unidad, cantidad_cent, precio_cent) "
                  "VALUES (1, 1, 'Desarrollo', 'hora', 1000, 4500)")
        c.execute("INSERT INTO contadores (anio, ultimo) VALUES (2026, 1)")
        c.commit()
    finally:
        c.close()


def _volcar(ruta: str, tabla: str) -> list[tuple]:
    c = sqlite3.connect(ruta)
    try:
        return c.execute(f"SELECT * FROM {tabla} ORDER BY 1").fetchall()
    finally:
        c.close()


def _columnas(ruta: str) -> list[str]:
    c = sqlite3.connect(ruta)
    try:
        return [f[1] for f in c.execute("PRAGMA table_info(clientes)")]
    finally:
        c.close()


def _version(ruta: str) -> int:
    c = sqlite3.connect(ruta)
    try:
        return c.execute("PRAGMA user_version").fetchone()[0]
    finally:
        c.close()


def test_v1_a_v2_conserva_datos(tmp_path):
    ruta = str(tmp_path / "v1.db")
    _crear_bd_v1(ruta)
    assert "tipo_documento" not in _columnas(ruta)
    clientes_antes = _volcar(ruta, "clientes")
    otras = {t: _volcar(ruta, t) for t in ("presupuestos", "lineas", "contadores")}

    db.inicializar(ruta)

    assert _version(ruta) == 2
    assert _columnas(ruta)[-1] == "tipo_documento"
    clientes_despues = _volcar(ruta, "clientes")
    assert [fila[:-1] for fila in clientes_despues] == clientes_antes
    assert [fila[-1] for fila in clientes_despues] == [""]
    for tabla, filas in otras.items():
        assert _volcar(ruta, tabla) == filas, tabla

    db.inicializar(ruta)  # idempotente
    assert _version(ruta) == 2
    assert _volcar(ruta, "clientes") == clientes_despues


def test_bd_nueva_en_version_2(tmp_path):
    ruta = str(tmp_path / "nueva.db")
    db.inicializar(ruta)
    assert _version(ruta) == 2
    assert "tipo_documento" in _columnas(ruta)


def test_tipo_documento_restringido(tmp_path):
    ruta = str(tmp_path / "nueva.db")
    db.inicializar(ruta)
    c = db.conectar(ruta)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("INSERT INTO clientes (nombre, categoria, territorio, tipo_documento) "
                      "VALUES ('X', 'empresa', 'peninsula', 'pasaporte')")
    finally:
        c.close()
