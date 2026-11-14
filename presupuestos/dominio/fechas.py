"""Fechas sin hora: AAAA-MM-DD ↔ DD/MM/AAAA (RN8, D18)."""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

ZONA = ZoneInfo("Europe/Madrid")
ERROR_FECHA = "Escribe la fecha como DD/MM/AAAA, por ejemplo 13/11/2026."


def hoy() -> str:
    return datetime.now(ZONA).date().isoformat()


def de_iso(texto: str) -> date:
    return date.fromisoformat(texto)


def a_iso(d: date) -> str:
    return d.isoformat()


def sumar_dias(fecha_iso: str, dias: int) -> str:
    return a_iso(de_iso(fecha_iso) + timedelta(days=dias))


def a_dmy(fecha_iso: str | None) -> str:
    if not fecha_iso:
        return ""
    return de_iso(fecha_iso).strftime("%d/%m/%Y")


def leer_dmy(texto: str) -> str:
    """'13/11/2026' → '2026-11-13'. Lanza ValueError con mensaje en español."""
    try:
        return datetime.strptime((texto or "").strip(), "%d/%m/%Y").date().isoformat()
    except ValueError:
        raise ValueError(ERROR_FECHA) from None


def leer_fecha(texto: str) -> str:
    """Fecha del calendario ('2026-11-20') o escrita a mano ('20/11/2026') → '2026-11-20' (FR-115, R9).

    Lanza ValueError con el mismo mensaje en español que leer_dmy.
    """
    limpio = (texto or "").strip()
    if len(limpio) == 10 and limpio[4] == "-" and limpio[7] == "-":
        try:
            return a_iso(de_iso(limpio))
        except ValueError:
            raise ValueError(ERROR_FECHA) from None  # fecha imposible, p. ej. 2026-02-30
    return leer_dmy(limpio)
