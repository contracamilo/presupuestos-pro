"""Nombre del archivo PDF (FR-022, D19)."""

import re
import unicodedata


def nombre_pdf(numero: str, nombre_cliente: str) -> str:
    sin_tildes = unicodedata.normalize("NFD", nombre_cliente)
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    limpio = re.sub(r"[^A-Za-z0-9 -]", "", sin_tildes)
    limpio = re.sub(r"-+", "-", limpio.replace(" ", "-")).strip("-")
    return f"{numero}_{limpio}.pdf" if limpio else f"{numero}.pdf"


_PROHIBIDOS = re.compile(r'[/\\:*?"<>|\x00-\x1f\x7f]')


def limpiar_nombre(texto: str) -> str:
    """Nombre de cliente apto para un nombre de archivo, conservando tildes y «ñ» (FR-308)."""
    limpio = re.sub(r"\s+", " ", _PROHIBIDOS.sub(" ", texto)).strip(" .")
    return limpio[:80].strip(" .")


def nombre_pdf_zip(numero: str, nombre_cliente: str) -> str:
    """Nombre del PDF dentro del .zip: «número - cliente.pdf» (FR-307)."""
    return f"{numero} - {limpiar_nombre(nombre_cliente) or 'Sin cliente'}.pdf"
