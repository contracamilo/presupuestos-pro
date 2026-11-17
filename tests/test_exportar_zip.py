"""Exportar en un .zip (spec 004). El PDF se captura sin WeasyPrint, como en test_pdf_contenido."""

import json

import pytest

from presupuestos.rutas.exportar import datos_exportacion, presupuestos_exportables, resumen_exportacion

EMISOR = {"nombre": "Laura Gómez", "nif": "12345678Z", "direccion": "Calle Mayor 1", "email": "l@ejemplo.es",
          "telefono": "", "logo_id": None, "retencion_activa": False, "tipo_retencion": 15}


@pytest.fixture
def perfil(conn):
    conn.execute("UPDATE perfil SET nombre = 'Laura Gómez', nif = '12345678Z', direccion = 'Calle Mayor 1' WHERE id = 1")


def crear(conn, numero, cliente="Acme SL", descargado=True, validez="2999-12-31", anonimizado=False, logo=None):
    """Presupuesto con una línea, directamente por SQL (devuelve su id)."""
    cid = conn.execute(
        "INSERT INTO clientes (nombre, nif, categoria, territorio, tipo_documento, anonimizado) "
        "VALUES (?, 'B12345678', 'empresa', 'peninsula', 'cif', ?)", (cliente, int(anonimizado))).lastrowid
    emisor = json.dumps({**EMISOR, "logo_id": logo}) if descargado else None
    pid = conn.execute(
        "INSERT INTO presupuestos (numero, fecha_creacion, fecha_emision, fecha_validez, tipo_iva, cliente_id, "
        "emisor_congelado, actualizado_en) VALUES (?, '2026-11-01', '2026-11-01', ?, 21, ?, ?, '2026-11-01')",
        (numero, validez, cid, emisor)).lastrowid
    conn.execute("INSERT INTO lineas (presupuesto_id, posicion, descripcion, unidad, cantidad_cent, precio_cent) "
                 "VALUES (?, 1, 'Trabajo', 'hora', 100, 10000)", (pid,))
    return pid


# ---------------------------------------------------------------- T004: archivo de datos

def test_datos_completos_conservan_claves_y_alcance(conn, perfil):
    crear(conn, "PRE-2026-001")
    d = datos_exportacion(conn)
    assert d["alcance"] == "completo" and d["version"] == 2
    assert set(d["datos"]) == {"perfil", "ajustes", "logos", "servicios", "clientes", "presupuestos", "contadores"}
    assert d["datos"]["perfil"] is not None and d["datos"]["ajustes"] is not None


def test_datos_de_seleccion(conn, perfil):
    logo = conn.execute("INSERT INTO logos (tipo, datos, creado_en) VALUES ('image/png', x'89504e47', '2026-11-01')").lastrowid
    otro_logo = conn.execute("INSERT INTO logos (tipo, datos, creado_en) VALUES ('image/png', x'89504e48', '2026-11-01')").lastrowid
    conn.execute("INSERT INTO servicios (nombre, unidad, precio_cent) VALUES ('Hora', 'hora', 4500)")
    conn.execute("INSERT INTO contadores (anio, ultimo) VALUES (2026, 2)")
    a = crear(conn, "PRE-2026-001", "Acme SL", logo=logo)
    crear(conn, "PRE-2026-002", "Otro SL", logo=otro_logo)
    d = datos_exportacion(conn, [a])
    assert d["alcance"] == "seleccion"
    datos = d["datos"]
    assert [p["id"] for p in datos["presupuestos"]] == [a]
    assert [c["nombre"] for c in datos["clientes"]] == ["Acme SL"]
    assert [l["id"] for l in datos["logos"]] == [logo]
    assert datos["servicios"] == [] and datos["contadores"] == []
    assert datos["perfil"] is None and datos["ajustes"] is None


# ---------------------------------------------------------------- T005: exportables

def test_exportables_y_resumen(conn, perfil):
    valido = crear(conn, "PRE-2026-001")
    crear(conn, "PRE-2026-002", descargado=False)
    crear(conn, "PRE-2026-003", "Eliminado", anonimizado=True)
    caducado = crear(conn, "PRE-2026-004", validez="2026-11-02")
    lista = presupuestos_exportables(conn)
    assert [p["id"] for p in lista] == [caducado, valido]  # fecha de emisión igual: número descendente
    assert {p["id"]: p["estado"] for p in lista} == {valido: "enviado", caducado: "caducado"}
    assert lista[0]["numero"] == "PRE-2026-004" and lista[0]["cliente_nombre"] == "Acme SL"
    assert resumen_exportacion(conn) == {"total": 4, "exportables": 2, "solo_datos": 2}
