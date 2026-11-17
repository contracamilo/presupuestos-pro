"""Exportación (FR-029) y orden de copia (FR-041)."""

import sqlite3

from presupuestos.__main__ import copia
from tests.conftest import crear_usuario, entrar


def test_orden_copia(conn, ruta_bd, tmp_path, cliente):
    crear_usuario(conn)
    entrar(cliente)
    cliente.post("/presupuestos")
    cliente.post("/presupuestos")
    archivo = copia(str(tmp_path / "copias"))
    assert archivo.exists()
    c = sqlite3.connect(archivo)
    try:
        numeros = [f[0] for f in c.execute("SELECT numero FROM presupuestos ORDER BY numero")]
    finally:
        c.close()
    originales = [f[0] for f in conn.execute("SELECT numero FROM presupuestos ORDER BY numero")]
    assert numeros == originales and len(numeros) == 2
