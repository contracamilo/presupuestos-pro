"""Países del selector del cliente, en español (FR-113, FR-114, R8). Sin datos externos (FR-028).

Si cambia la composición de la UE, basta con editar PAISES_UE.
"""

import unicodedata


def _clave(nombre: str) -> str:
    """Orden alfabético español ignorando tildes."""
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", nombre) if unicodedata.category(c) != "Mn")
    return sin_tildes.casefold()


PAISES_UE = sorted([
    "Alemania", "Austria", "Bélgica", "Bulgaria", "Chipre", "Croacia", "Dinamarca", "Eslovaquia",
    "Eslovenia", "España", "Estonia", "Finlandia", "Francia", "Grecia", "Hungría", "Irlanda", "Italia",
    "Letonia", "Lituania", "Luxemburgo", "Malta", "Países Bajos", "Polonia", "Portugal",
    "República Checa", "Rumanía", "Suecia",
], key=_clave)

_FUERA_UE = [
    "Afganistán", "Albania", "Andorra", "Angola", "Antigua y Barbuda", "Arabia Saudí", "Argelia",
    "Argentina", "Armenia", "Australia", "Azerbaiyán", "Bahamas", "Bangladés", "Barbados", "Baréin",
    "Belice", "Benín", "Bielorrusia", "Bolivia", "Bosnia y Herzegovina", "Botsuana", "Brasil", "Brunéi",
    "Burkina Faso", "Burundi", "Bután", "Cabo Verde", "Camboya", "Camerún", "Canadá", "Catar", "Chad",
    "Chile", "China", "Colombia", "Comoras", "Corea del Norte", "Corea del Sur", "Costa de Marfil",
    "Costa Rica", "Cuba", "Dominica", "Ecuador", "Egipto", "El Salvador", "Emiratos Árabes Unidos",
    "Eritrea", "Esuatini", "Estados Unidos", "Etiopía", "Filipinas", "Fiyi", "Gabón", "Gambia",
    "Georgia", "Ghana", "Granada", "Guatemala", "Guinea", "Guinea-Bisáu", "Guinea Ecuatorial", "Guyana",
    "Haití", "Honduras", "India", "Indonesia", "Irak", "Irán", "Islandia", "Islas Marshall",
    "Islas Salomón", "Israel", "Jamaica", "Japón", "Jordania", "Kazajistán", "Kenia", "Kirguistán",
    "Kiribati", "Kosovo", "Kuwait", "Laos", "Lesoto", "Líbano", "Liberia", "Libia", "Liechtenstein",
    "Macedonia del Norte", "Madagascar", "Malasia", "Malaui", "Maldivas", "Malí", "Marruecos",
    "Mauricio", "Mauritania", "México", "Micronesia", "Moldavia", "Mónaco", "Mongolia", "Montenegro",
    "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Nicaragua", "Níger", "Nigeria", "Noruega",
    "Nueva Zelanda", "Omán", "Pakistán", "Palaos", "Palestina", "Panamá", "Papúa Nueva Guinea",
    "Paraguay", "Perú", "Reino Unido", "República Centroafricana", "República del Congo",
    "República Democrática del Congo", "República Dominicana", "Ruanda", "Rusia", "Samoa",
    "San Cristóbal y Nieves", "San Marino", "San Vicente y las Granadinas", "Santa Lucía",
    "Santo Tomé y Príncipe", "Senegal", "Serbia", "Seychelles", "Sierra Leona", "Singapur", "Siria",
    "Somalia", "Sri Lanka", "Sudáfrica", "Sudán", "Sudán del Sur", "Suiza", "Surinam", "Tailandia",
    "Taiwán", "Tanzania", "Tayikistán", "Timor Oriental", "Togo", "Tonga", "Trinidad y Tobago", "Túnez",
    "Turkmenistán", "Turquía", "Tuvalu", "Ucrania", "Uganda", "Uruguay", "Uzbekistán", "Vanuatu",
    "Vaticano", "Venezuela", "Vietnam", "Yemen", "Yibuti", "Zambia", "Zimbabue",
]

# «España» primero; el resto en orden alfabético.
PAISES = ["España"] + sorted([p for p in PAISES_UE if p != "España"] + _FUERA_UE, key=_clave)


def opciones(territorio: str) -> list[str]:
    if territorio in ("peninsula", "canarias"):
        return ["España"]
    if territorio == "ue":
        return [p for p in PAISES_UE if p != "España"]
    if territorio == "fuera_ue":
        return sorted((p for p in PAISES if p not in PAISES_UE), key=_clave)
    return []


def es_valido(territorio: str, pais: str, guardado: str) -> bool:
    """Vacío (el país no es obligatorio), de la lista del territorio o el valor que el cliente ya tenía
    guardado (clientes de v1)."""
    return pais == "" or pais in opciones(territorio) or (bool(guardado) and pais == guardado)
