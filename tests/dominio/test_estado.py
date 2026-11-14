"""Estado del presupuesto deducido sin guardar nada (FR-209, FR-209a; data-model.md de la 003)."""

import pytest

from presupuestos.dominio import estado

HOY = "2026-11-14"
CONGELADO = '{"nombre": "Laura"}'


@pytest.mark.parametrize("congelado, validez, esperado", [
    (None, "2026-12-01", "borrador"),        # nunca descargado
    ("", "2026-12-01", "borrador"),          # vacío cuenta como no descargado
    (CONGELADO, "2026-12-01", "enviado"),    # descargado al menos una vez
    (None, "2026-11-13", "caducado"),        # validez pasada
    (CONGELADO, "2026-11-13", "caducado"),   # Caducado gana a Enviado (sesión de aclaraciones, Q2)
    (None, HOY, "borrador"),                 # validez = hoy: todavía no caduca
    (CONGELADO, HOY, "enviado"),
])
def test_regla(congelado, validez, esperado):
    assert estado.estado(congelado, validez, HOY) == esperado


def test_etiquetas_y_mostrables():
    assert estado.ETIQUETAS == {"borrador": "Borrador", "enviado": "Enviado", "caducado": "Caducado",
                                "aceptado": "Aceptado", "rechazado": "Rechazado"}
    assert estado.MOSTRABLES == ("borrador", "enviado", "caducado")
    assert set(estado.MOSTRABLES) < set(estado.ETIQUETAS)  # Aceptado y Rechazado solo diseñadas (FR-209a)
