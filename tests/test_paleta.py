"""Paleta accesible y definida en un único lugar (FR-202, FR-212, SC-202, SC-209)."""

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).parent.parent / "presupuestos"
TOKENS = RAIZ / "static" / "tokens.css"
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


def _colores() -> dict[str, str]:
    return dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{6})\s*;", TOKENS.read_text(encoding="utf-8")))


def _luminancia(hexa: str) -> float:
    canales = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lineal = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
    return 0.2126 * lineal[0] + 0.7152 * lineal[1] + 0.0722 * lineal[2]


def contraste(a: str, b: str) -> float:
    claro, oscuro = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (claro + 0.05) / (oscuro + 0.05)


def _sin_comentarios(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


@pytest.mark.parametrize("primero, fondo, minimo", PARES)
def test_contrastes_de_la_paleta(primero, fondo, minimo):
    colores = _colores()
    valor = contraste(colores[primero], colores[fondo])
    assert valor >= minimo, f"{primero} sobre {fondo}: {valor:.2f}:1 < {minimo}:1"


def test_estilos_sin_colores_propios():
    css = _sin_comentarios(ESTILOS.read_text(encoding="utf-8"))
    assert not COLOR_LITERAL.findall(css), "estilos.css debe usar solo var(--…) de tokens.css"


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
