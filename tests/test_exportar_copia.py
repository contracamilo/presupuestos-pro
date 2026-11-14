"""Exportación (FR-029) y orden de copia (FR-041)."""

import sqlite3

from presupuestos.__main__ import copia
from tests.conftest import crear_usuario, entrar


def test_exportacion_completa_y_sin_cuentas(conn, cliente):
    crear_usuario(conn)
    crear_usuario(conn, "asistente", "pablo@ejemplo.es")
    conn.execute("INSERT INTO logos (tipo, datos, creado_en) VALUES ('image/png', x'89504e47', '2026-11-14')")
    conn.execute("INSERT INTO servicios (nombre, unidad, precio_cent) VALUES ('Hora de desarrollo', 'hora', 4500)")
    conn.execute("INSERT INTO clientes (nombre, nif, categoria, territorio, tipo_documento) "
                 "VALUES ('Acme SL', 'B12345678', 'empresa', 'peninsula', 'cif')")

    entrar(cliente, "pablo@ejemplo.es")  # también puede exportar un asistente
    cliente.post("/presupuestos")
    r = cliente.get("/exportar")
    assert r.status_code == 200
    assert 'filename="presupuestospro-copia-' in r.headers["Content-Disposition"]
    datos = r.json()
    assert datos["formato"] == "presupuestospro" and datos["version"] == 2
    assert set(datos["datos"]) == {"perfil", "ajustes", "logos", "servicios", "clientes", "presupuestos", "contadores"}
    assert datos["datos"]["logos"][0]["datos_base64"] == "iVBORw=="
    assert datos["datos"]["ajustes"]["retencion_activa"] is False
    assert all("tipo_documento" in c for c in datos["datos"]["clientes"])
    assert datos["datos"]["clientes"][0]["tipo_documento"] == "cif"
    assert datos["datos"]["presupuestos"][0]["numero"].startswith("PRE-")
    assert datos["datos"]["presupuestos"][0]["lineas"] == []
    texto = r.text
    assert "hash_contrasena" not in texto
    assert "pablo@ejemplo.es" not in texto and "titular@ejemplo.es" not in texto
    assert "usuarios" not in datos["datos"]


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
