"""Formato español de importes, cantidades y porcentajes (RN11, FR-030, D18)."""

import re

MENOS = "−"  # signo menos tipográfico


def _miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def euros(cent: int) -> str:
    signo = MENOS if cent < 0 else ""
    cent = abs(cent)
    return f"{signo}{_miles(cent // 100)},{cent % 100:02d} €"


def cantidad(centesimas: int) -> str:
    entero, dec = divmod(centesimas, 100)
    if dec == 0:
        return _miles(entero)
    return f"{_miles(entero)},{dec:02d}".rstrip("0")


def porcentaje(n: int) -> str:
    return f"{n} %"


def importe_editable(cent: int) -> str:
    """Valor para rellenar un campo de formulario (sin €)."""
    return f"{cent // 100},{cent % 100:02d}"


_NUMERO = re.compile(r"^(\d{1,3}(\.\d{3})+|\d+)(,(\d+))?$")


def _leer_centesimas(texto: str, que: str) -> int:
    t = (texto or "").strip().replace(" ", "")
    if t.startswith("-") or t.startswith(MENOS):
        raise ValueError(f"El {que} no puede ser negativo.")
    m = _NUMERO.match(t)
    if not m:
        raise ValueError(f"Escribe un {que} válido, por ejemplo 1.234,56.")
    entero = int(m.group(1).replace(".", ""))
    dec = m.group(4) or ""
    if len(dec) > 2:
        raise ValueError(f"El {que} admite como máximo 2 decimales.")
    return entero * 100 + int(dec.ljust(2, "0") or 0)


def leer_importe(texto: str) -> int:
    """'1.500,50' → 150050 céntimos. Lanza ValueError con mensaje en español."""
    return _leer_centesimas(texto, "importe")


def leer_cantidad(texto: str) -> int:
    """'1,5' → 150 centésimas."""
    return _leer_centesimas(texto, "número")
