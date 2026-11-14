"""Tipos de documento permitidos según categoría y territorio (data-model.md, R7)."""

import pytest

from presupuestos.dominio import documento


@pytest.mark.parametrize("categoria, territorio, esperado", [
    ("particular", "peninsula", ["nif", "nie"]),
    ("particular", "canarias", ["nif", "nie"]),
    ("empresa", "peninsula", ["nif", "cif", "nie"]),
    ("empresa", "canarias", ["nif", "cif", "nie"]),
    ("empresa", "ue", ["nif_iva_ue", "extranjero"]),
    ("empresa", "fuera_ue", ["extranjero"]),
])
def test_tipos_permitidos(categoria, territorio, esperado):
    assert documento.tipos_permitidos(categoria, territorio) == esperado


def test_preseleccion():
    assert documento.preseleccion("empresa", "ue") == "nif_iva_ue"
    assert documento.preseleccion("empresa", "fuera_ue") == "extranjero"
    for categoria in ("empresa", "particular"):
        for territorio in ("peninsula", "canarias"):
            assert documento.preseleccion(categoria, territorio) == ""


def test_es_valido():
    for categoria, territorio in documento.COMBINACIONES:
        assert documento.es_valido(categoria, territorio, "")
    assert not documento.es_valido("particular", "peninsula", "cif")
    assert not documento.es_valido("empresa", "fuera_ue", "nif")
    assert not documento.es_valido("empresa", "peninsula", "pasaporte")
    assert documento.es_valido("empresa", "ue", "nif_iva_ue")


def test_etiquetas():
    assert set(documento.ETIQUETAS.values()) == {
        "NIF", "CIF", "NIE", "NIF-IVA UE", "Otro documento extranjero", "Sin indicar"}
    assert set(documento.ETIQUETAS) == {""} | set(documento.TIPOS)
