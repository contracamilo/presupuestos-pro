"""Tabla RN6: IVA, retención y mención según el tipo de cliente (D5).

Revisar con el asesor fiscal antes de usar con datos reales (supuesto de la spec).
"""

INVERSION_SUJETO_PASIVO = "Inversión del sujeto pasivo"
NO_SUJETA = "Operación no sujeta — Art. 69.Uno.1.º Ley 37/1992"


def tratamiento(
    categoria: str,
    territorio: str,
    nif_iva_verificado: bool,
    retencion_activa: bool,
    mencion_canarias: str,
) -> tuple[bool, bool, str | None]:
    """Devuelve (lleva_iva, aplica_retencion, mencion)."""
    if categoria == "particular":
        if territorio not in ("peninsula", "canarias"):
            raise ValueError("Un cliente particular solo puede estar en España.")
        return True, False, None

    if territorio == "peninsula":
        return True, bool(retencion_activa), None
    if territorio == "ue":
        if nif_iva_verificado:
            return False, False, INVERSION_SUJETO_PASIVO
        return True, False, None
    if territorio == "fuera_ue":
        return False, False, NO_SUJETA
    if territorio == "canarias":
        texto = (mencion_canarias or "").strip()
        return False, bool(retencion_activa), texto or None
    raise ValueError(f"Territorio desconocido: {territorio}")
