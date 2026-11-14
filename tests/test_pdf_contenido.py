"""El rediseño no cambia el contenido del PDF (FR-215, SC-206) ni muestra el estado (FR-211).

Compara el texto visible del HTML que se manda al generador con una referencia guardada con la
plantilla de v1.1, antes del rediseño. Para regenerarla (solo si el contrato del PDF cambia):
    REGENERAR_REFERENCIAS=1 pytest tests/test_pdf_contenido.py
"""

import os
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

import pytest

REFERENCIAS = Path(__file__).parent / "referencias"
PNG_MINIMO = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
PALABRAS_ESTADO = ("Borrador", "Enviado", "Caducado", "Aceptado", "Rechazado")


class _Texto(HTMLParser):
    """Texto visible: sin <style>, <title> ni etiquetas."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.partes, self._ignorar = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "title", "script"):
            self._ignorar += 1

    def handle_endtag(self, tag):
        if tag in ("style", "title", "script"):
            self._ignorar -= 1

    def handle_data(self, data):
        if not self._ignorar:
            self.partes.append(data)


def texto_visible(html: str) -> str:
    p = _Texto()
    p.feed(html)
    return re.sub(r"\s+", " ", unescape(" ".join(p.partes))).strip()


def _capturar_html(cliente, monkeypatch, id_: int) -> str:
    capturado = {}

    def falso_generar(html):
        capturado["html"] = html
        return b"%PDF-falso"

    monkeypatch.setattr("presupuestos.pdf.generar_pdf", falso_generar)
    r = cliente.get(f"/presupuestos/{id_}/pdf")
    assert r.status_code == 200, r.text[:300]
    return capturado["html"]


def _nuevo_presupuesto(cliente, conn, numero: str, datos_cliente: dict) -> int:
    r = cliente.post("/presupuestos")
    id_ = int(r.headers["location"].rsplit("/", 1)[1])
    # Número y fechas fijos: la referencia no depende del día en que se ejecute el test.
    conn.execute("UPDATE presupuestos SET numero = ?, fecha_emision = '2026-11-14', fecha_validez = '2026-12-14' "
                 "WHERE id = ?", (numero, id_))
    base = {"nif": "", "direccion": "", "email": "", "pais": "", "tipo_documento": ""}
    base.update(datos_cliente)
    assert cliente.post("/clientes", data=base).status_code == 303
    cliente_id = conn.execute("SELECT MAX(id) FROM clientes").fetchone()[0]
    assert cliente.put(f"/presupuestos/{id_}", data={"cliente_id": str(cliente_id)}).status_code == 200
    return id_


@pytest.fixture
def escenario(titular, conn):
    conn.execute("UPDATE perfil SET nombre = 'Laura Gómez Peña', nif = '12345678Z', "
                 "direccion = 'Calle Mayor 1, 2.º B\n28013 Madrid', email = 'laura@ejemplo.es', "
                 "telefono = '600 123 456' WHERE id = 1")
    logo = conn.execute("INSERT INTO logos (tipo, datos, creado_en) VALUES ('image/png', ?, '2026-11-14')",
                        (PNG_MINIMO,)).lastrowid
    conn.execute("UPDATE perfil SET logo_id = ? WHERE id = 1", (logo,))
    conn.execute("UPDATE ajustes SET retencion_activa = 1, tipo_retencion = 15 WHERE id = 1")

    # A: con logo, empresa en península, 3 líneas, retención y notas de dos líneas.
    a = _nuevo_presupuesto(titular, conn, "PRE-2026-015", {
        "nombre": "Acme Desarrollos SL", "nif": "B12345678", "categoria": "empresa", "territorio": "peninsula",
        "tipo_documento": "cif", "direccion": "Avenida de la Paz 10\n41001 Sevilla", "email": "compras@acme.es"})
    for descripcion, cantidad, unidad, precio in [("Análisis y diseño de la aplicación", "12,5", "hora", "45"),
                                                 ("Desarrollo de la API", "3", "día", "360"),
                                                 ("Puesta en marcha", "1", "proyecto", "250,50")]:
        titular.post(f"/presupuestos/{a}/lineas",
                     data={"descripcion": descripcion, "cantidad": cantidad, "unidad": unidad, "precio": precio})
    titular.put(f"/presupuestos/{a}", data={"notas": "Pago a 30 días.\nIncluye dos revisiones."})
    return titular, a


def _presupuesto_b(titular, conn) -> int:
    """B: sin logo, cliente UE con NIF-IVA verificado (mención), 40 líneas y total ≥ 1.000.000,00 €."""
    conn.execute("UPDATE perfil SET logo_id = NULL WHERE id = 1")
    b = _nuevo_presupuesto(titular, conn, "PRE-2026-016", {
        "nombre": "Müller & Söhne GmbH", "nif": "DE123456789", "categoria": "empresa", "territorio": "ue",
        "tipo_documento": "nif_iva_ue", "pais": "Alemania", "nif_iva_verificado": "1"})
    larga = "Integración " + "con el sistema de facturación y pruebas de aceptación " * 6
    for i in range(40):
        descripcion = larga.strip()[:300] if i == 0 else f"Módulo {i + 1}"
        titular.post(f"/presupuestos/{b}/lineas",
                     data={"descripcion": descripcion, "cantidad": "1", "unidad": "unidad", "precio": "30.000"})
    return b


def _comparar(nombre: str, texto: str) -> None:
    ruta = REFERENCIAS / nombre
    if os.environ.get("REGENERAR_REFERENCIAS") == "1":
        REFERENCIAS.mkdir(exist_ok=True)
        ruta.write_text(texto + "\n", encoding="utf-8")
        return
    assert ruta.exists(), f"Falta la referencia {ruta}; genérala con REGENERAR_REFERENCIAS=1"
    assert texto == ruta.read_text(encoding="utf-8").strip()


def _comprobar_html(html: str) -> None:
    for palabra in PALABRAS_ESTADO:
        assert palabra not in texto_visible(html), palabra  # el estado no va al PDF (FR-211)
    # Misma tipografía que la app, incrustada: el generador no lee archivos ni internet (FR-201, FR-217, FR-218).
    assert "data:font/woff2;base64," in html
    assert re.search(r'font-family:\s*"Inter"', html)
    assert "/static/" not in html and "http" not in html
    assert '<html lang="es">' in html  # FR-214b


def test_pdf_a_mismo_contenido(escenario, monkeypatch):
    titular, a = escenario
    html = _capturar_html(titular, monkeypatch, a)
    _comprobar_html(html)
    _comparar("pdf_a.txt", texto_visible(html))


def test_pdf_b_mismo_contenido(escenario, conn, monkeypatch):
    titular, _ = escenario
    b = _presupuesto_b(titular, conn)
    html = _capturar_html(titular, monkeypatch, b)
    _comprobar_html(html)
    texto = texto_visible(html)
    assert "1.200.000,00 €" in texto
    _comparar("pdf_b.txt", texto)
