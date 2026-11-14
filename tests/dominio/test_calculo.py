"""Todos los ejemplos obligatorios de data-model.md (SC-002), con retención activa al 15 % e IVA 21 %."""

import pytest

from presupuestos.dominio.calculo import calcular, redondeo
from presupuestos.dominio.tratamiento import INVERSION_SUJETO_PASIVO, NO_SUJETA


def linea(cantidad_cent, precio_cent):
    return {"cantidad_cent": cantidad_cent, "precio_cent": precio_cent}


def cliente(categoria, territorio, verificado=False):
    return {"categoria": categoria, "territorio": territorio, "nif_iva_verificado": int(verificado)}


BASE = [linea(1000, 4500), linea(100, 30000)]
REFERENCIA = [linea(100, 150000), linea(100, 50000)]


@pytest.mark.parametrize(
    "caso, lineas, cli, tipo_ret, esperado",
    [
        ("CA6 empresa península", BASE, cliente("empresa", "peninsula"), 15, (75000, 15750, 11250, 79500)),
        ("CA7 particular", BASE, cliente("particular", "peninsula"), 15, (75000, 15750, 0, 90750)),
        ("CA8 UE verificado", BASE, cliente("empresa", "ue", True), 15, (75000, 0, 0, 75000)),
        ("CL3 fuera UE", BASE, cliente("empresa", "fuera_ue"), 15, (75000, 0, 0, 75000)),
        ("CL4 Canarias empresa", BASE, cliente("empresa", "canarias"), 15, (75000, 0, 11250, 63750)),
        ("CA9 cantidad 12", [linea(1200, 4500), linea(100, 30000)], cliente("empresa", "peninsula"), 15,
         (84000, 17640, 12600, 89040)),
        ("Ref. 15 %", REFERENCIA, cliente("empresa", "peninsula"), 15, (200000, 42000, 30000, 212000)),
        ("Ref. 7 %", REFERENCIA, cliente("empresa", "peninsula"), 7, (200000, 42000, 14000, 228000)),
        ("Ref. particular", REFERENCIA, cliente("particular", "peninsula"), 15, (200000, 42000, 0, 242000)),
    ],
)
def test_ejemplos_obligatorios(caso, lineas, cli, tipo_ret, esperado):
    t = calcular(lineas, 21, cli, True, tipo_ret, "")
    assert (t.base, t.iva, t.retencion, t.total) == esperado, caso
    assert t.provisional is False


def test_ca8_y_cl3_menciones():
    assert calcular(BASE, 21, cliente("empresa", "ue", True), True, 15, "").mencion == INVERSION_SUJETO_PASIVO
    assert calcular(BASE, 21, cliente("empresa", "fuera_ue"), True, 15, "").mencion == NO_SUJETA


def test_retencion_solo_si_aplica():
    t = calcular(BASE, 21, cliente("particular", "peninsula"), True, 15, "")
    assert t.aplica_retencion is False
    t = calcular(BASE, 21, cliente("empresa", "peninsula"), False, 15, "")
    assert t.aplica_retencion is False and t.retencion == 0 and t.total == 90750


def test_cl7_cantidad_decimal():
    t = calcular([linea(150, 4500)], 21, cliente("empresa", "peninsula"), True, 15, "")
    assert t.importes_linea == [6750]
    assert t.base == 6750


def test_cl6_linea_cortesia_no_altera_totales():
    con = calcular(BASE + [linea(100, 0)], 21, cliente("empresa", "peninsula"), True, 15, "")
    sin = calcular(BASE, 21, cliente("empresa", "peninsula"), True, 15, "")
    assert con.importes_linea[-1] == 0
    assert (con.base, con.iva, con.retencion, con.total) == (sin.base, sin.iva, sin.retencion, sin.total)


def test_cl5_iva_reducido_10():
    t = calcular(BASE, 10, cliente("particular", "peninsula"), True, 15, "")
    assert t.iva == 7500
    assert t.total == 82500
    t = calcular(BASE, 10, cliente("empresa", "peninsula"), True, 15, "")
    assert (t.iva, t.total) == (7500, 71250)


def test_fr044_sin_cliente_totales_provisionales():
    t = calcular(BASE, 21, None, True, 15, "texto canarias")
    assert (t.base, t.iva, t.retencion, t.total) == (75000, 15750, 11250, 79500)
    assert t.provisional is True
    assert t.mencion is None


def test_ca4_importe_linea():
    t = calcular([linea(1000, 4500)], 21, None, False, 15, "")
    assert t.importes_linea == [45000]


def test_redondeo_mitad_hacia_arriba():
    assert redondeo(5, 10) == 1      # 0,5 → 1
    assert redondeo(4, 10) == 0      # 0,4 → 0
    assert redondeo(15, 10) == 2     # 1,5 → 2
    # 0,33 × 45,41 € = 14,9853 € → 14,99 €
    assert calcular([linea(33, 4541)], 0, None, False, 15, "").importes_linea == [1499]
