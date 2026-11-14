"""PDF con WeasyPrint, sin acceso a internet (research.md D6 de la 001, V10 de la 003)."""

import base64
import re
from functools import lru_cache
from pathlib import Path

ESTATICOS = Path(__file__).parent / "static"
_URL_FUENTE = re.compile(r'url\("/static/fuentes/([\w.-]+\.woff2)"\)')


@lru_cache(maxsize=1)
def estilos_comunes() -> str:
    """tokens.css con las fuentes insertadas como data: (FR-201, FR-217).

    El PDF usa la misma paleta, escalas y tipografía que la app. Las fuentes se insertan en el CSS
    en lugar de dejar que el generador lea archivos locales: así sigue aceptando solo URIs data:.
    """
    css = (ESTATICOS / "tokens.css").read_text(encoding="utf-8")

    def insertar(m: re.Match) -> str:
        datos = base64.b64encode((ESTATICOS / "fuentes" / m.group(1)).read_bytes()).decode()
        return f'url("data:font/woff2;base64,{datos}")'

    return _URL_FUENTE.sub(insertar, css)


def generar_pdf(html: str) -> bytes:
    # WeasyPrint se importa aquí y no al principio del módulo: necesita librerías del sistema
    # (Pango, GLib) y así el resto del módulo y los tests que lo usan no dependen de ellas.
    from weasyprint import HTML, URLFetcher

    # Solo URIs data: (el logo y las fuentes). Cualquier otra URL se rechaza y no se descarga nada.
    solo_data = URLFetcher(allowed_protocols={"data"}, allow_redirects=False)
    return HTML(string=html, url_fetcher=solo_data).write_pdf()
