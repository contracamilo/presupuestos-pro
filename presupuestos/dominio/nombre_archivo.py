"""Nombre del archivo PDF (FR-022, D19)."""

import re
import unicodedata


def nombre_pdf(numero: str, nombre_cliente: str) -> str:
    sin_tildes = unicodedata.normalize("NFD", nombre_cliente)
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    limpio = re.sub(r"[^A-Za-z0-9 -]", "", sin_tildes)
    limpio = re.sub(r"-+", "-", limpio.replace(" ", "-")).strip("-")
    return f"{numero}_{limpio}.pdf" if limpio else f"{numero}.pdf"
