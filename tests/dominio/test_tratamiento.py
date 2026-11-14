"""Tabla RN6 completa."""

import pytest

from presupuestos.dominio.tratamiento import INVERSION_SUJETO_PASIVO, NO_SUJETA, tratamiento


@pytest.mark.parametrize(
    "categoria, territorio, verificado, esperado",
    [
        ("empresa", "peninsula", False, (True, True, None)),
        ("particular", "peninsula", False, (True, False, None)),
        ("particular", "canarias", False, (True, False, None)),
        ("empresa", "ue", True, (False, False, INVERSION_SUJETO_PASIVO)),
        ("empresa", "ue", False, (True, False, None)),  # CL1
        ("empresa", "fuera_ue", False, (False, False, NO_SUJETA)),
        ("empresa", "canarias", False, (False, True, "Mención configurada")),
    ],
)
def test_tabla_rn6(categoria, territorio, verificado, esperado):
    assert tratamiento(categoria, territorio, verificado, True, "Mención configurada") == esperado


def test_retencion_desactivada_en_emisor():
    assert tratamiento("empresa", "peninsula", False, False, "") == (True, False, None)
    assert tratamiento("empresa", "canarias", False, False, "") == (False, False, None)


def test_canarias_sin_texto_no_muestra_mencion():
    assert tratamiento("empresa", "canarias", False, True, "") == (False, True, None)
    assert tratamiento("empresa", "canarias", False, True, "   ") == (False, True, None)


def test_particular_fuera_de_espana_no_admitido():
    with pytest.raises(ValueError):
        tratamiento("particular", "ue", False, True, "")
