from presupuestos.dominio.validacion import faltan_perfil, requisitos_descarga, validar_cliente

PERFIL = {"nombre": "Laura", "nif": "12345678Z", "direccion": "C/ Mayor 1", "email": "l@e.es", "telefono": ""}
LINEAS = [{"cantidad_cent": 100, "precio_cent": 100}]


def cli(**kw):
    base = {"nombre": "Acme SL", "nif": "B1", "categoria": "empresa", "territorio": "peninsula",
            "nif_iva_verificado": 0, "anonimizado": 0}
    base.update(kw)
    return base


def test_faltan_perfil():
    assert faltan_perfil(PERFIL) == []
    assert faltan_perfil({}) == ["nombre", "NIF", "dirección", "email"]


def test_todo_correcto():
    assert requisitos_descarga(PERFIL, cli(), LINEAS) == []


def test_ca2_perfil_sin_nif():
    assert requisitos_descarga({**PERFIL, "nif": ""}, cli(), LINEAS) == ["Completa tu perfil: falta el NIF."]


def test_ca13_sin_cliente_ni_lineas():
    assert requisitos_descarga(PERFIL, None, []) == ["Selecciona un cliente.", "Añade al menos una línea."]


def test_cl13_empresa_espana_sin_nif():
    assert requisitos_descarga(PERFIL, cli(nif=""), LINEAS) == ["Completa el NIF del cliente Acme SL."]
    assert requisitos_descarga(PERFIL, cli(nif="", territorio="canarias"), LINEAS) != []
    # Particular o empresa extranjera sin NIF: la spec no lo bloquea
    assert requisitos_descarga(PERFIL, cli(nif="", categoria="particular"), LINEAS) == []
    assert requisitos_descarga(PERFIL, cli(nif="", territorio="fuera_ue"), LINEAS) == []


def test_cliente_anonimizado():
    assert requisitos_descarga(PERFIL, cli(anonimizado=1, nombre="Cliente eliminado", nif=""), LINEAS) == [
        "El cliente de este presupuesto fue eliminado: no se puede descargar."
    ]


def test_validar_cliente():
    ok = {"nombre": "Acme", "categoria": "empresa", "territorio": "ue", "nif_iva_verificado": True}
    assert validar_cliente(ok) == []
    assert validar_cliente({**ok, "nombre": " "}) == ["El nombre o razón social es obligatorio."]
    assert "Un cliente particular solo puede estar en España." in validar_cliente(
        {**ok, "categoria": "particular", "nif_iva_verificado": False})
    assert validar_cliente({**ok, "territorio": "peninsula"}) == [
        "«NIF-IVA verificado» solo se puede marcar para clientes de otro país UE."]
    assert validar_cliente({"nombre": "Ana", "categoria": "particular", "territorio": "canarias"}) == []
