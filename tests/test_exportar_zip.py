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


# ---------------------------------------------------------------- T006: POST /exportar (modo=todo)

import io
import zipfile

from presupuestos.dominio import fechas
from tests.conftest import crear_usuario, entrar


@pytest.fixture
def pdf_falso(monkeypatch):
    """El PDF capturado es el propio HTML; la lista `generados` guarda cada HTML generado."""
    generados = []

    def falso(html):
        generados.append(html)
        return html.encode()

    monkeypatch.setattr("presupuestos.pdf.generar_pdf", falso)
    return generados


def abrir_zip(r) -> zipfile.ZipFile:
    return zipfile.ZipFile(io.BytesIO(r.content))


def escenario_todo(conn):
    ids = [crear(conn, "PRE-2026-001", "Estudio García"),
           crear(conn, "PRE-2026-002", "Diseño/Web S.L."),
           crear(conn, "PRE-2026-003", "Acme SL")]
    borrador = crear(conn, "PRE-2026-004", "Borrador SL", descargado=False)
    return ids, borrador


def test_exportar_todo(titular, conn, perfil, pdf_falso):
    escenario_todo(conn)
    r = titular.post("/exportar", data={"modo": "todo"})
    assert r.status_code == 200
    assert r.headers["Content-Type"] == "application/zip"
    base = f"presupuestospro-copia-{fechas.hoy()}"
    assert f'filename="{base}.zip"' in r.headers["Content-Disposition"]
    z = abrir_zip(r)
    assert sorted(z.namelist()) == sorted([
        f"{base}.json", "PRE-2026-001 - Estudio García.pdf", "PRE-2026-002 - Diseño Web S.L.pdf",
        "PRE-2026-003 - Acme SL.pdf"])
    datos = json.loads(z.read(f"{base}.json"))
    assert datos["alcance"] == "completo" and len(datos["datos"]["presupuestos"]) == 4


def test_exportar_sin_sesion(cliente):
    r = cliente.post("/exportar", data={"modo": "todo"})
    assert r.status_code == 303 and r.headers["location"] == "/entrar"


def test_asistente_puede_exportar(conn, cliente, perfil, pdf_falso):
    crear_usuario(conn)
    crear_usuario(conn, "asistente", "pablo@ejemplo.es")
    entrar(cliente, "pablo@ejemplo.es")
    crear(conn, "PRE-2026-001")
    assert cliente.post("/exportar", data={"modo": "todo"}).status_code == 200


def test_exportar_sin_presupuestos(titular):
    r = titular.post("/exportar", data={"modo": "todo"})
    assert r.status_code == 422 and r.json() == {"error": "No hay presupuestos que exportar."}


@pytest.mark.parametrize("datos", [{}, {"modo": "otro"}])
def test_exportar_modo_no_valido(titular, datos):
    r = titular.post("/exportar", data=datos)
    assert r.status_code == 422 and r.json() == {"error": "Elige qué exportar."}


def test_pdf_del_zip_igual_a_la_descarga_individual(titular, conn, perfil, pdf_falso):
    ids, _ = escenario_todo(conn)
    z = abrir_zip(titular.post("/exportar", data={"modo": "todo"}))
    en_zip = {n: z.read(n).decode() for n in z.namelist() if n.endswith(".pdf")}
    individuales = {}
    for id_, n in zip(ids, ["PRE-2026-001 - Estudio García.pdf", "PRE-2026-002 - Diseño Web S.L.pdf",
                            "PRE-2026-003 - Acme SL.pdf"]):
        r = titular.get(f"/presupuestos/{id_}/pdf")
        assert r.status_code == 200
        individuales[n] = r.content.decode()
    assert en_zip == individuales


def test_el_json_no_lleva_cuentas(conn, cliente, perfil, pdf_falso):
    crear_usuario(conn)
    crear_usuario(conn, "asistente", "pablo@ejemplo.es")
    entrar(cliente, "pablo@ejemplo.es")
    logo = conn.execute("INSERT INTO logos (tipo, datos, creado_en) VALUES ('image/png', x'89504e47', '2026-11-01')").lastrowid
    crear(conn, "PRE-2026-001", logo=logo)
    z = abrir_zip(cliente.post("/exportar", data={"modo": "todo"}))
    texto = z.read([n for n in z.namelist() if n.endswith(".json")][0]).decode()
    assert "hash_contrasena" not in texto and "pablo@ejemplo.es" not in texto and "titular@ejemplo.es" not in texto
    datos = json.loads(texto)["datos"]
    assert "usuarios" not in datos
    assert datos["logos"][0]["datos_base64"] == "iVBORw=="
    assert datos["clientes"][0]["tipo_documento"] == "cif"


def test_historial_incluye_la_ventana(titular, conn, perfil):
    assert "No hay presupuestos que exportar" in titular.get("/").text
    crear(conn, "PRE-2026-001")
    html = titular.get("/").text
    assert 'id="abrir-exportar"' in html and 'id="ventana-exportar"' in html
    assert 'data-exportables="1"' in html and "Descargar .zip" in html
