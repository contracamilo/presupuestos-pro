"""Países del selector según territorio (data-model.md, R8)."""

from presupuestos.dominio import paises
from presupuestos.dominio.paises import _clave


def test_listas():
    assert paises.PAISES[0] == "España"
    assert len(paises.PAISES) == len(set(paises.PAISES))
    assert len(paises.PAISES_UE) == 27
    assert {"España", "Alemania", "Francia"} <= set(paises.PAISES_UE)
    assert "Reino Unido" not in paises.PAISES_UE and "Suiza" not in paises.PAISES_UE
    assert set(paises.PAISES_UE) <= set(paises.PAISES)
    resto = paises.PAISES[1:]
    assert resto == sorted(resto, key=_clave)


def test_opciones_por_territorio():
    assert paises.opciones("peninsula") == ["España"]
    assert paises.opciones("canarias") == ["España"]
    ue = paises.opciones("ue")
    assert "España" not in ue
    assert set(ue) <= set(paises.PAISES_UE) and len(ue) == 26
    assert ue == sorted(ue, key=_clave)
    fuera = paises.opciones("fuera_ue")
    assert not set(fuera) & set(paises.PAISES_UE)
    assert "Reino Unido" in fuera and "Japón" in fuera
    assert fuera == sorted(fuera, key=_clave)


def test_es_valido():
    assert paises.es_valido("ue", "Alemania", guardado="")
    assert paises.es_valido("ue", "Alemania (Berlín)", guardado="Alemania (Berlín)")  # valor de v1
    assert not paises.es_valido("ue", "Japón", guardado="")
    assert not paises.es_valido("fuera_ue", "Francia", guardado="")
    assert paises.es_valido("ue", "", guardado="")  # el país no es obligatorio
