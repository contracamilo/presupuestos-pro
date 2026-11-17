"""Paleta accesible y definida en un único lugar (FR-202, FR-212, SC-202, SC-209).

Ampliación de la 002 (modo oscuro): contrastes en los dos temas, paleta oscura completa y
solo de colores, y PDF siempre en claro (FR-127, FR-128, FR-130, SC-109, SC-110, research R16)."""

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).parent.parent / "presupuestos"
TOKENS = RAIZ / "static" / "tokens.css"
TOKENS_OSCURO = RAIZ / "static" / "tokens-oscuro.css"
ESTILOS = RAIZ / "static" / "estilos.css"
PDF = RAIZ / "templates" / "pdf.html"
PLANTILLAS = RAIZ / "templates"

# Pares de contracts/sistema-visual.md («Pares de contraste»): (primer plano, fondo, mínimo).
PARES = [
    ("--color-texto", "--color-fondo", 4.5),
    ("--color-texto", "--color-fondo-2", 4.5),
    ("--color-texto-suave", "--color-fondo", 4.5),
    ("--color-texto-suave", "--color-fondo-2", 4.5),
    ("--color-marca", "--color-fondo", 4.5),
    ("--color-marca", "--color-fondo-2", 4.5),
    ("--color-marca", "--color-marca-claro", 4.5),
    ("--color-sobre-marca", "--color-marca", 4.5),
    ("--color-sobre-marca", "--color-marca-hover", 4.5),
    ("--color-sobre-marca", "--color-error", 4.5),
    ("--color-borde-control", "--color-fondo", 3),
    # Ampliación 002: en oscuro el menú lateral usa --color-fondo-2 y lleva campos (selector «Tema»).
    ("--color-borde-control", "--color-fondo-2", 3),
    ("--color-exito", "--color-fondo", 4.5),
    ("--color-exito", "--color-exito-fondo", 4.5),
    ("--color-aviso", "--color-aviso-fondo", 4.5),
    ("--color-error", "--color-fondo", 4.5),
    ("--color-error", "--color-error-fondo", 4.5),
] + [(f"--estado-{e}-texto", f"--estado-{e}-fondo", 4.5)
     for e in ("borrador", "enviado", "caducado", "aceptado", "rechazado")] + [
    # El borde de cada etiqueta usa el color del texto: debe verse sobre el fondo de la página.
    (f"--estado-{e}-texto", "--color-fondo", 3) for e in ("borrador", "enviado", "caducado", "aceptado", "rechazado")
]

COLOR_LITERAL = re.compile(r"#[0-9a-fA-F]{3}\b|#[0-9a-fA-F]{6}\b|\brgba?\(|\bhsla?\(")


def _colores(archivo: Path = TOKENS) -> dict[str, str]:
    return dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{6})\s*;", archivo.read_text(encoding="utf-8")))


# Variables de color: empiezan por --color- o --estado- y valen #rrggbb o rgba(...).
VARIABLE_COLOR = re.compile(r"(--(?:color|estado)-[\w-]+):\s*(?:#[0-9a-fA-F]{6}|rgba\([^)]*\))\s*;")


def _paleta(tema: str) -> dict[str, str]:
    claro = _colores(TOKENS)
    return claro if tema == "claro" else {**claro, **_colores(TOKENS_OSCURO)}


def _luminancia(hexa: str) -> float:
    canales = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lineal = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
    return 0.2126 * lineal[0] + 0.7152 * lineal[1] + 0.0722 * lineal[2]


def contraste(a: str, b: str) -> float:
    claro, oscuro = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (claro + 0.05) / (oscuro + 0.05)


def _sin_comentarios(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


@pytest.mark.parametrize("tema", ("claro", "oscuro"))
@pytest.mark.parametrize("primero, fondo, minimo", PARES)
def test_contrastes_de_la_paleta(tema, primero, fondo, minimo):
    colores = _paleta(tema)
    valor = contraste(colores[primero], colores[fondo])
    assert valor >= minimo, f"[{tema}] {primero} sobre {fondo}: {valor:.2f}:1 < {minimo}:1"


def test_paleta_oscura_completa():
    """Ninguna zona queda con colores del claro (SC-109): mismos nombres salvo --color-fondo-logo."""
    claro = set(VARIABLE_COLOR.findall(_sin_comentarios(TOKENS.read_text(encoding="utf-8"))))
    oscuro = set(VARIABLE_COLOR.findall(_sin_comentarios(TOKENS_OSCURO.read_text(encoding="utf-8"))))
    assert claro - {"--color-fondo-logo"} == oscuro


def test_paleta_oscura_solo_colores():
    """tokens-oscuro.css: un bloque :root con color-scheme: dark y solo colores (FR-128)."""
    css = _sin_comentarios(TOKENS_OSCURO.read_text(encoding="utf-8"))
    assert re.search(r"color-scheme:\s*dark\s*;", css)
    assert css.count("{") == 1 and css.count("}") == 1 and css.strip().startswith(":root")
    variables = re.findall(r"(--[\w-]+)\s*:", css)
    assert variables and all(v.startswith(("--color-", "--estado-")) for v in variables), variables
    assert "--color-fondo-logo" not in variables


def test_pdf_sin_hoja_oscura():
    """El PDF solo lee tokens.css: sale siempre con la paleta clara (FR-130)."""
    from presupuestos import pdf

    css = pdf.estilos_comunes()
    assert "--color-fondo: #14191f" not in css and "color-scheme: dark" not in css
    assert "tokens-oscuro" not in PDF.read_text(encoding="utf-8")


def test_estilos_sin_colores_propios():
    css = _sin_comentarios(ESTILOS.read_text(encoding="utf-8"))
    assert not COLOR_LITERAL.findall(css), "estilos.css debe usar solo var(--…) de tokens.css y tokens-oscuro.css"


def test_pdf_sin_colores_propios():
    html = PDF.read_text(encoding="utf-8")
    estilos = "".join(re.findall(r"<style>(.*?)</style>", html, flags=re.S))
    assert not COLOR_LITERAL.findall(_sin_comentarios(estilos)), "pdf.html debe usar solo var(--…) de tokens.css"


def test_plantillas_sin_estilos_en_linea():
    """La CSP (style-src 'self') bloquea estilos en línea: solo pdf.html puede tenerlos."""
    for ruta in PLANTILLAS.rglob("*.html"):
        if ruta.name == "pdf.html":
            continue
        texto = ruta.read_text(encoding="utf-8")
        assert 'style="' not in texto and "<style" not in texto, ruta.name
