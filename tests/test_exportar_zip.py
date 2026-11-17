"""Exportar en un .zip (spec 004). El PDF se captura sin WeasyPrint, como en test_pdf_contenido."""

import json

import pytest

from presupuestos.rutas.exportar import presupuestos_exportables, resumen_exportacion

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
    assert resumen_exportacion(conn) == {"total": 4, "exportables": 2, "sin_pdf": 2}


# ---------------------------------------------------------------- T006: POST /exportar (modo=todo)

import io
import zipfile

from presupuestos.dominio import estado, fechas
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
        "PRE-2026-001 - Estudio García.pdf", "PRE-2026-002 - Diseño Web S.L.pdf", "PRE-2026-003 - Acme SL.pdf"])


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


def test_exportar_solo_con_borradores(titular, conn, perfil, pdf_falso):
    crear(conn, "PRE-2026-001", descargado=False)  # sin PDF no hay nada que exportar (no hay archivo de datos)
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


def test_historial_incluye_la_ventana(titular, conn, perfil):
    assert "No hay presupuestos que exportar" in titular.get("/").text
    crear(conn, "PRE-2026-001", descargado=False)
    assert "No hay presupuestos que exportar" in titular.get("/").text  # un borrador no tiene PDF
    assert 'id="form-exportar"' not in titular.get("/").text
    crear(conn, "PRE-2026-002")
    html = titular.get("/").text
    assert 'id="abrir-exportar"' in html and 'id="ventana-exportar"' in html
    assert 'data-exportables="1"' in html and "Descargar .zip" in html


# ---------------------------------------------------------------- T014: modo=seleccion

def escenario_seleccion(conn):
    ids = [crear(conn, "PRE-2026-001", "Estudio García"),
           crear(conn, "PRE-2026-002", "Diseño/Web S.L."),
           crear(conn, "PRE-2026-003", "Acme SL")]
    borrador = crear(conn, "PRE-2026-004", "Borrador SL", descargado=False)
    anonimo = crear(conn, "PRE-2026-005", "Eliminado", anonimizado=True)
    return ids, borrador, anonimo


def test_seleccion_parcial(titular, conn, perfil, pdf_falso):
    ids, _, _ = escenario_seleccion(conn)
    r = titular.post("/exportar", data={"modo": "seleccion", "ids": [str(ids[0]), str(ids[2])]})
    assert r.status_code == 200
    base = f"presupuestospro-seleccion-{fechas.hoy()}"
    assert f'filename="{base}.zip"' in r.headers["Content-Disposition"]
    z = abrir_zip(r)
    assert sorted(z.namelist()) == sorted(["PRE-2026-001 - Estudio García.pdf", "PRE-2026-003 - Acme SL.pdf"])


def test_seleccion_vacia(titular, conn, perfil, pdf_falso):
    escenario_seleccion(conn)
    for datos in ({"modo": "seleccion"}, {"modo": "seleccion", "ids": "abc"}):
        r = titular.post("/exportar", data=datos)
        assert r.status_code == 422 and r.json() == {"error": "Marca al menos un presupuesto."}


def test_seleccion_con_id_no_exportable(titular, conn, perfil, pdf_falso):
    ids, borrador, anonimo = escenario_seleccion(conn)
    for malo in (borrador, anonimo, 99999):
        r = titular.post("/exportar", data={"modo": "seleccion", "ids": [str(ids[0]), str(malo)]})
        assert r.status_code == 409
        assert r.json() == {"error": "La lista ha cambiado. Cierra la ventana y vuelve a abrirla."}
    assert pdf_falso == []  # no se generó nada


def test_seleccion_no_incluye_lo_descargado_despues(titular, conn, perfil, pdf_falso):
    ids, borrador, _ = escenario_seleccion(conn)
    conn.execute("UPDATE presupuestos SET emisor_congelado = ? WHERE id = ?", (json.dumps(EMISOR), borrador))
    z = abrir_zip(titular.post("/exportar", data={"modo": "seleccion", "ids": [str(ids[0])]}))
    assert [n for n in z.namelist() if n.endswith(".pdf")] == ["PRE-2026-001 - Estudio García.pdf"]


def test_todo_ignora_los_ids(titular, conn, perfil, pdf_falso):
    ids, _, _ = escenario_seleccion(conn)
    r = titular.post("/exportar", data={"modo": "todo", "ids": [str(ids[0])]})
    z = abrir_zip(r)
    assert "copia" in r.headers["Content-Disposition"] and len([n for n in z.namelist() if n.endswith(".pdf")]) == 3


def test_ventana_ofrece_seleccion(titular, conn, perfil):
    crear(conn, "PRE-2026-001", "Estudio García")
    crear(conn, "PRE-2026-002", "Borrador SL", descargado=False)
    html = titular.get("/").text
    assert 'id="modo-seleccion"' in html and 'id="marcar-todos"' in html
    assert html.count('name="ids"') == 1 and "PRE-2026-001" in html
    assert "copia de seguridad" not in html and "archivo de datos" not in html


# ---------------------------------------------------------------- T019: solo lectura y coherencia

def _foto(conn):
    return ([tuple(f) for f in conn.execute("SELECT * FROM presupuestos ORDER BY id")],
            [tuple(f) for f in conn.execute("SELECT * FROM contadores ORDER BY anio")],
            [tuple(f) for f in conn.execute("SELECT * FROM lineas ORDER BY id")])


@pytest.mark.parametrize("datos", [{"modo": "todo"}, "seleccion"])
def test_exportar_no_escribe_nada(titular, conn, perfil, pdf_falso, datos):
    ids, borrador, _ = escenario_seleccion(conn)
    conn.execute("INSERT INTO contadores (anio, ultimo) VALUES (?, 5)", (int(fechas.hoy()[:4]),))
    if datos == "seleccion":
        datos = {"modo": "seleccion", "ids": [str(ids[0])]}
    antes = _foto(conn)
    assert titular.post("/exportar", data=datos).status_code == 200
    assert _foto(conn) == antes
    fila = conn.execute("SELECT emisor_congelado FROM presupuestos WHERE id = ?", (borrador,)).fetchone()
    assert fila[0] is None  # el borrador sigue sin fijar el emisor
    assert estado.estado(fila[0], "2999-12-31", fechas.hoy()) == "borrador"
    # El siguiente presupuesto recibe el número consecutivo esperado.
    r = titular.post("/presupuestos")
    nuevo = conn.execute("SELECT numero FROM presupuestos WHERE id = ?", (int(r.headers["location"].rsplit("/", 1)[1]),)).fetchone()[0]
    assert nuevo == f"PRE-{fechas.hoy()[:4]}-006"  # el contador sembrado en 5 no se movió con la exportación


def test_lectura_de_un_solo_instante(titular, conn, perfil, pdf_falso, monkeypatch):
    ids, borrador, _ = escenario_seleccion(conn)
    from presupuestos.rutas import presupuestos as rutas_presupuestos

    original = rutas_presupuestos.html_pdf
    hecho = []

    def html_con_escritura_ajena(c, datos):
        if not hecho:  # mientras se prepara el primer PDF, otra sesión cambia datos
            hecho.append(1)
            crear(conn, "PRE-2026-099", "Nuevo SL")
            conn.execute("UPDATE presupuestos SET emisor_congelado = ? WHERE id = ?", (json.dumps(EMISOR), borrador))
        return original(c, datos)

    monkeypatch.setattr(rutas_presupuestos, "html_pdf", html_con_escritura_ajena)
    z = abrir_zip(titular.post("/exportar", data={"modo": "todo"}))
    nombres = z.namelist()
    assert hecho
    assert not any("099" in n or "Borrador" in n for n in nombres)  # lo creado o descargado a mitad no entra
    assert len(nombres) == 3


# ---------------------------------------------------------------- T020: recuento en la ventana

def test_recuento_de_la_ventana(titular, conn, perfil):
    crear(conn, "PRE-2026-001")
    crear(conn, "PRE-2026-002")
    crear(conn, "PRE-2026-003", descargado=False)
    html = " ".join(titular.get("/").text.split())
    assert "Se incluirán 2 PDF." in html
    assert "El presupuesto sin PDF no se incluirá." in html
    assert "Descargar .zip (2 archivos)" in html
    crear(conn, "PRE-2026-004", descargado=False)
    assert "Los 2 presupuestos sin PDF no se incluirán." in " ".join(titular.get("/").text.split())


def test_recuento_con_un_solo_pdf(titular, conn, perfil):
    crear(conn, "PRE-2026-001")
    html = " ".join(titular.get("/").text.split())
    assert "Se incluirá 1 PDF." in html and "Descargar .zip (1 archivo)" in html


# ---------------------------------------------------------------- T023: errores y volumen

def test_fallo_al_generar_un_pdf(titular, conn, perfil, monkeypatch):
    escenario_todo(conn)

    def roto(html):
        raise RuntimeError("fallo de WeasyPrint")

    monkeypatch.setattr("presupuestos.pdf.generar_pdf", roto)
    antes = _foto(conn)
    r = titular.post("/exportar", data={"modo": "todo"})
    assert r.status_code == 500
    assert r.json() == {"error": "No se ha podido preparar la copia. Inténtalo de nuevo."}
    assert r.headers["Content-Type"].startswith("application/json")
    assert _foto(conn) == antes


@pytest.mark.parametrize("cantidad", [50, 200])
def test_volumen(titular, conn, perfil, pdf_falso, cantidad):
    for i in range(cantidad):
        crear(conn, f"PRE-2026-{i + 1:03d}", f"Cliente {i % 7}")
    z = abrir_zip(titular.post("/exportar", data={"modo": "todo"}))
    pdfs = [n for n in z.namelist() if n.endswith(".pdf")]
    assert len(pdfs) == cantidad and len(set(pdfs)) == cantidad
    assert len(z.namelist()) == cantidad


def test_estilos_respetan_hidden_en_la_ventana():
    """`.error` y `.mensaje` fuerzan `display`; sin esta regla el error vacío se vería siempre."""
    from pathlib import Path
    css = (Path(__file__).parent.parent / "presupuestos" / "static" / "estilos.css").read_text(encoding="utf-8")
    assert "dialog#ventana-exportar [hidden] { display: none; }" in css
