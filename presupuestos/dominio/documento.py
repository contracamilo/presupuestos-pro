"""Tipo de documento del cliente según categoría y territorio (FR-112, FR-114, R7).

Una sola regla para el servidor (validación) y la pantalla (filtrado del selector).
El tipo es opcional: '' («Sin indicar») siempre es válido.
"""

TIPOS = ("nif", "cif", "nie", "nif_iva_ue", "extranjero")

ETIQUETAS = {
    "": "Sin indicar",
    "nif": "NIF",
    "cif": "CIF",
    "nie": "NIE",
    "nif_iva_ue": "NIF-IVA UE",
    "extranjero": "Otro documento extranjero",
}

# (categoria, territorio) → tipos permitidos. Combinaciones ausentes (particular fuera de España) no admiten ninguno.
_PERMITIDOS = {
    ("particular", "peninsula"): ["nif", "nie"],
    ("particular", "canarias"): ["nif", "nie"],
    ("empresa", "peninsula"): ["nif", "cif", "nie"],
    ("empresa", "canarias"): ["nif", "cif", "nie"],
    ("empresa", "ue"): ["nif_iva_ue", "extranjero"],
    ("empresa", "fuera_ue"): ["extranjero"],
}

_PRESELECCION = {
    ("empresa", "ue"): "nif_iva_ue",
    ("empresa", "fuera_ue"): "extranjero",
}

COMBINACIONES = tuple(_PERMITIDOS)


def tipos_permitidos(categoria: str, territorio: str) -> list[str]:
    return list(_PERMITIDOS.get((categoria, territorio), []))


def preseleccion(categoria: str, territorio: str) -> str:
    """Tipo que se elige solo si el selector está vacío o deja de ser válido ('' = «Sin indicar»)."""
    return _PRESELECCION.get((categoria, territorio), "")


def es_valido(categoria: str, territorio: str, tipo: str) -> bool:
    return tipo == "" or tipo in tipos_permitidos(categoria, territorio)


def permitido_en(tipo: str) -> list[str]:
    """Combinaciones 'categoria:territorio' donde el tipo es válido (para el selector de la pantalla)."""
    return [f"{c}:{t}" for (c, t), tipos in _PERMITIDOS.items() if tipo in tipos]


def preseleccionado_en(tipo: str) -> list[str]:
    return [f"{c}:{t}" for (c, t), pre in _PRESELECCION.items() if pre == tipo]
