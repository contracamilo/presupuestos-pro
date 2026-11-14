"""Cálculo de totales RN1–RN5 en céntimos enteros (D4). Única función para pantalla y PDF."""

from dataclasses import dataclass

from presupuestos.dominio.tratamiento import tratamiento


def redondeo(numerador: int, denominador: int) -> int:
    """División entera con redondeo mitad hacia arriba (valores no negativos)."""
    return (2 * numerador + denominador) // (2 * denominador)


@dataclass(frozen=True)
class Totales:
    importes_linea: list[int]
    base: int
    lleva_iva: bool
    tipo_iva: int
    iva: int
    aplica_retencion: bool
    tipo_retencion: int
    retencion: int
    total: int
    mencion: str | None
    provisional: bool


def _campo(obj, nombre):
    return obj[nombre] if isinstance(obj, dict) or hasattr(obj, "keys") else getattr(obj, nombre)


def calcular(lineas, tipo_iva: int, cliente, retencion_activa: bool, tipo_retencion: int, mencion_canarias: str) -> Totales:
    importes = [redondeo(_campo(l, "cantidad_cent") * _campo(l, "precio_cent"), 100) for l in lineas]
    base = sum(importes)

    if cliente is None:
        lleva_iva, aplica_retencion, _ = tratamiento("empresa", "peninsula", False, retencion_activa, "")
        mencion, provisional = None, True
    else:
        lleva_iva, aplica_retencion, mencion = tratamiento(
            _campo(cliente, "categoria"),
            _campo(cliente, "territorio"),
            bool(_campo(cliente, "nif_iva_verificado")),
            retencion_activa,
            mencion_canarias,
        )
        provisional = False

    iva = redondeo(base * tipo_iva, 100) if lleva_iva else 0
    retencion = redondeo(base * tipo_retencion, 100) if aplica_retencion else 0
    return Totales(
        importes_linea=importes,
        base=base,
        lleva_iva=lleva_iva,
        tipo_iva=tipo_iva,
        iva=iva,
        aplica_retencion=aplica_retencion,
        tipo_retencion=tipo_retencion,
        retencion=retencion,
        total=base + iva - retencion,
        mencion=mencion,
        provisional=provisional,
    )
