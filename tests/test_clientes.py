"""Tipo de documento y país del cliente validados en el servidor; anonimización (FR-112 a FR-114, FR-043)."""

BASE = {"nombre": "Acme", "nif": "X1", "direccion": "", "email": "", "pais": "",
        "categoria": "empresa", "territorio": "peninsula", "tipo_documento": ""}


def _datos(**cambios):
    datos = dict(BASE)
    datos.update(cambios)
    return datos


def _cliente(conn, nombre="Acme"):
    return dict(conn.execute("SELECT * FROM clientes WHERE nombre = ?", (nombre,)).fetchone())


def test_tipo_documento_no_permitido(titular, conn):
    r = titular.post("/clientes", data=_datos(categoria="particular", tipo_documento="cif"))
    assert r.status_code == 422 and "Tipo de documento no válido para este cliente." in r.text
    r = titular.post("/clientes", data=_datos(territorio="fuera_ue", tipo_documento="nif", pais="Japón"))
    assert r.status_code == 422 and "Tipo de documento no válido para este cliente." in r.text
    r = titular.post("/clientes", data=_datos(tipo_documento="pasaporte"))
    assert r.status_code == 422
    assert conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0] == 0


def test_pais_fuera_de_la_lista(titular, conn):
    r = titular.post("/clientes", data=_datos(territorio="ue", pais="Japón"))
    assert r.status_code == 422 and "Elige un país de la lista." in r.text
    r = titular.post("/clientes", data=_datos(territorio="fuera_ue", pais="Francia"))
    assert r.status_code == 422 and "Elige un país de la lista." in r.text
    assert conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0] == 0


def test_alta_valida_guarda_tipo_y_pais(titular, conn):
    r = titular.post("/clientes", data=_datos(territorio="ue", pais="Alemania", tipo_documento="nif_iva_ue"))
    assert r.status_code == 303
    c = _cliente(conn)
    assert (c["tipo_documento"], c["pais"]) == ("nif_iva_ue", "Alemania")


def test_espana_fuerza_pais(titular, conn):
    r = titular.post("/clientes", data=_datos(pais="Francia", tipo_documento="cif"))
    assert r.status_code == 303
    assert _cliente(conn)["pais"] == "España"


def test_edicion_acepta_pais_guardado_de_v1(titular, conn):
    conn.execute("INSERT INTO clientes (nombre, pais, categoria, territorio) "
                 "VALUES ('Acme', 'Alemania (Berlín)', 'empresa', 'ue')")
    id_ = _cliente(conn)["id"]
    r = titular.get(f"/clientes/{id_}")
    assert "Revisar país: Alemania (Berlín)" in r.text
    r = titular.put(f"/clientes/{id_}", data=_datos(territorio="ue", pais="Alemania (Berlín)", nombre="Acme"))
    assert r.status_code == 200
    r = titular.put(f"/clientes/{id_}", data=_datos(territorio="ue", pais="Austria (Viena)"))
    assert r.status_code == 422 and "Elige un país de la lista." in r.text


def test_anonimizar_vacia_tipo_documento(titular, conn):
    titular.post("/clientes", data=_datos(tipo_documento="cif", nif="B12345678"))
    id_ = _cliente(conn)["id"]
    assert titular.post(f"/clientes/{id_}/anonimizar").status_code == 303
    c = dict(conn.execute("SELECT * FROM clientes WHERE id = ?", (id_,)).fetchone())
    assert (c["tipo_documento"], c["nif"], c["pais"], c["anonimizado"]) == ("", "", "", 1)
