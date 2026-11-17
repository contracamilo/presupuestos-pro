"""Tema claro, oscuro o del sistema: ruta POST /tema, cookie y tema que pinta el servidor.

Spec 002, US7 (FR-117 a FR-126), contracts/tema.md y research R12, R14, R15.
"""

import re

import pytest

from tests.conftest import crear_usuario


def _cookie_tema(r) -> str | None:
    for valor in r.headers.get_list("set-cookie"):
        if valor.startswith("tema="):
            return valor
    return None


def _apariencia(html: str) -> tuple[str, str]:
    media = re.search(r'<link id="tokens-oscuro" rel="stylesheet" href="/static/tokens-oscuro.css" media="([^"]*)">', html)
    meta = re.search(r'<meta name="color-scheme" content="([^"]*)">', html)
    assert media and meta, "faltan el enlace #tokens-oscuro o el meta color-scheme"
    return media.group(1), meta.group(1)


def test_tema_exige_sesion(cliente):
    r = cliente.post("/tema", data={"tema": "oscuro"})
    assert r.status_code == 303 and r.headers["location"] == "/entrar"
    assert _cookie_tema(r) is None


def test_tema_con_fetch_devuelve_204_y_cookie(titular):
    r = titular.post("/tema", data={"tema": "oscuro"}, headers={"X-Tema-Fetch": "1"})
    assert r.status_code == 204
    cookie = _cookie_tema(r)
    assert cookie is not None
    for parte in ("tema=oscuro", "Max-Age=34560000", "HttpOnly", "Path=/"):
        assert parte in cookie, (parte, cookie)
    assert "samesite=lax" in cookie.lower()
    assert "Secure" not in cookie  # COOKIE_SEGURA=0 en conftest.py


@pytest.mark.parametrize("volver", ["/clientes", "/?q=Acme"])
def test_tema_sin_js_redirige_a_volver(titular, volver):
    r = titular.post("/tema", data={"tema": "claro", "volver": volver})
    assert r.status_code == 303 and r.headers["location"] == volver
    assert _cookie_tema(r).startswith("tema=claro")


@pytest.mark.parametrize("volver", ["//ejemplo.com", "https://ejemplo.com/x", "clientes", ""])
def test_tema_volver_externo_va_a_inicio(titular, volver):
    r = titular.post("/tema", data={"tema": "oscuro", "volver": volver})
    assert r.status_code == 303 and r.headers["location"] == "/"


@pytest.mark.parametrize("volver, destino", [
    ("/mi-cuenta/contrasena", "/"),  # solo admite POST: sin JS daría 405 (FR-120)
    ("/no-existe", "/"),
    ("/presupuestos/1", "/presupuestos/1"),  # ruta con parámetro que admite GET
])
def test_tema_volver_sin_get_va_a_inicio(titular, volver, destino):
    r = titular.post("/tema", data={"tema": "oscuro", "volver": volver})
    assert r.status_code == 303 and r.headers["location"] == destino


def test_error_sin_sesion_sigue_al_sistema(titular):
    titular.cookies.set("tema", "oscuro")
    r = titular.get("/no-existe")
    assert r.status_code == 404
    assert 'media="(prefers-color-scheme: dark)"' in r.text


def test_tema_valor_desconocido(titular):
    r = titular.post("/tema", data={"tema": "azul"})
    assert r.status_code == 422
    assert _cookie_tema(r) is None


def test_tema_origen_ajeno(titular):
    r = titular.post("/tema", data={"tema": "oscuro"}, headers={"Origin": "https://otro.ejemplo"})
    assert r.status_code == 403


@pytest.mark.parametrize("cookie, media, scheme", [
    ("claro", "not all", "light"),
    ("oscuro", "all", "dark"),
    ("sistema", "(prefers-color-scheme: dark)", "light dark"),
    (None, "(prefers-color-scheme: dark)", "light dark"),
    ("azul", "(prefers-color-scheme: dark)", "light dark"),
])
def test_base_segun_cookie(titular, cookie, media, scheme):
    if cookie is not None:
        titular.cookies.set("tema", cookie)
    html = titular.get("/").text
    assert _apariencia(html) == (media, scheme)
    # Orden de carga (R14): tokens.css, tokens-oscuro.css, estilos.css.
    assert html.index("/static/tokens.css") < html.index("/static/tokens-oscuro.css") < html.index("/static/estilos.css")


@pytest.mark.parametrize("cookie, marcado", [(None, "sistema"), ("oscuro", "oscuro")])
def test_selector_en_menu(titular, cookie, marcado):
    if cookie is not None:
        titular.cookies.set("tema", cookie)
    html = titular.get("/clientes").text
    inicio = html.index('<form class="form-tema" method="post" action="/tema">')
    fin = html.index("</form>", inicio)
    form = html[inicio:fin]
    assert "<legend" in form and ">Tema</legend>" in form
    radios = re.findall(r'<input type="radio" name="tema" value="(\w+)"( checked)?>', form)
    assert [v for v, _ in radios] == ["claro", "oscuro", "sistema"]
    assert [v for v, c in radios if c] == [marcado]
    assert '<input type="hidden" name="volver" value="/clientes">' in form
    assert re.search(r"<button[^>]*>Aplicar</button>", form)
    # Después de «Mi cuenta» y antes de «Salir» (FR-117).
    assert html.index(">Mi cuenta</a>") < inicio < html.index('action="/salir"')


def test_sin_sesion_sigue_al_sistema(cliente, conn):
    crear_usuario(conn)
    cliente.cookies.set("tema", "oscuro")
    r = cliente.get("/entrar")
    assert r.status_code == 200
    assert _apariencia(r.text) == ("(prefers-color-scheme: dark)", "light dark")
    assert "form-tema" not in r.text
