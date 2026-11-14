"""Estado de un presupuesto, deducido de los datos que ya se guardan (FR-209, FR-209a).

No hay columna de estado: se calcula al mostrar el presupuesto. Cada presupuesto tiene un único
estado y «Caducado» prevalece sobre los demás (spec 003, sesión de aclaraciones):
  1. «Válido hasta» anterior a hoy        → caducado
  2. PDF descargado alguna vez            → enviado   (emisor_congelado relleno, FR-018 de la 001)
  3. En otro caso                         → borrador
Aceptado y Rechazado solo existen como etiqueta diseñada para una funcionalidad futura.
"""

ETIQUETAS = {
    "borrador": "Borrador",
    "enviado": "Enviado",
    "caducado": "Caducado",
    "aceptado": "Aceptado",
    "rechazado": "Rechazado",
}

MOSTRABLES = ("borrador", "enviado", "caducado")


def estado(emisor_congelado: str | None, fecha_validez: str, hoy: str) -> str:
    """Fechas en AAAA-MM-DD (comparables como texto); `hoy` es la fecha de España (fechas.hoy())."""
    if fecha_validez < hoy:
        return "caducado"
    if emisor_congelado:
        return "enviado"
    return "borrador"
