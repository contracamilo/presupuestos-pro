import pytest

from presupuestos.dominio import fechas, formato
from presupuestos.dominio.nombre_archivo import limpiar_nombre, nombre_pdf, nombre_pdf_zip


def test_euros():
    assert formato.euros(123456) == "1.234,56 €"
    assert formato.euros(75000) == "750,00 €"
    assert formato.euros(-11250) == "−112,50 €"
    assert formato.euros(0) == "0,00 €"
    assert formato.euros(100000000) == "1.000.000,00 €"


def test_cantidad_y_porcentaje():
    assert formato.cantidad(1000) == "10"
    assert formato.cantidad(150) == "1,5"
    assert formato.cantidad(125) == "1,25"
    assert formato.porcentaje(21) == "21 %"


@pytest.mark.parametrize("texto, cent", [("1500", 150000), ("1500,5", 150050), ("1.500,50", 150050),
                                          ("45", 4500), ("0", 0), (" 12,3 ", 1230)])
def test_leer_importe_valido(texto, cent):
    assert formato.leer_importe(texto) == cent


@pytest.mark.parametrize("texto", ["10,555", "-1", "abc", "", "1,2,3", "1.50"])
def test_leer_importe_invalido(texto):
    with pytest.raises(ValueError):
        formato.leer_importe(texto)


def test_leer_cantidad():
    assert formato.leer_cantidad("1,5") == 150
    assert formato.leer_cantidad("10") == 1000


def test_fechas():
    assert fechas.sumar_dias("2026-11-13", 30) == "2026-12-13"
    assert fechas.a_dmy("2026-12-13") == "13/12/2026"
    assert fechas.a_dmy(None) == ""


def test_nombre_pdf():
    assert nombre_pdf("PRE-2026-015", "Acme SL") == "PRE-2026-015_Acme-SL.pdf"
    assert nombre_pdf("PRE-2026-016", "Peña & Cía") == "PRE-2026-016_Pena-Cia.pdf"


def test_leer_fecha_calendario_y_respaldo():
    assert fechas.leer_fecha("2026-11-20") == "2026-11-20"
    assert fechas.leer_fecha("20/11/2026") == "2026-11-20"
    assert fechas.leer_fecha(" 2026-11-20 ") == "2026-11-20"


@pytest.mark.parametrize("texto", ["2026-02-30", "30/02/2026", "mañana", ""])
def test_leer_fecha_invalida(texto):
    with pytest.raises(ValueError) as error:
        fechas.leer_fecha(texto)
    with pytest.raises(ValueError) as esperado:
        fechas.leer_dmy("texto no válido")
    assert str(error.value) == str(esperado.value)


def test_nombre_pdf_zip():
    assert nombre_pdf_zip("PRE-2026-001", "Diseño/Web S.L.") == "PRE-2026-001 - Diseño Web S.L.pdf"
    assert nombre_pdf_zip("PRE-2026-001", "Estudio García") == "PRE-2026-001 - Estudio García.pdf"
    assert nombre_pdf_zip("PRE-2026-001", "A:B*C?") == "PRE-2026-001 - A B C.pdf"
    assert nombre_pdf_zip("PRE-2026-001", "") == "PRE-2026-001 - Sin cliente.pdf"
    assert nombre_pdf_zip("PRE-2026-001", "///") == "PRE-2026-001 - Sin cliente.pdf"
    assert len(limpiar_nombre("x" * 150)) <= 80
    assert limpiar_nombre("a" * 79 + " " + "b" * 20) == "a" * 79


def test_nombre_pdf_individual_no_cambia():
    assert nombre_pdf("PRE-2026-001", "Estudio García") == "PRE-2026-001_Estudio-Garcia.pdf"
