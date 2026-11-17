"""Piezas compartidas por todas las rutas: plantillas y control de sesión (FR-034, FR-035)."""

import sqlite3
from pathlib import Path

from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from presupuestos import seguridad
from presupuestos.db import get_db
from presupuestos.dominio import documento, estado, fechas, formato, paises

plantillas = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
plantillas.env.autoescape = True
plantillas.env.filters["euros"] = formato.euros
plantillas.env.filters["cantidad"] = formato.cantidad
plantillas.env.filters["porcentaje"] = formato.porcentaje
plantillas.env.filters["fecha"] = fechas.a_dmy
plantillas.env.filters["importe_editable"] = formato.importe_editable
# Selectores del formulario de cliente (FR-112, FR-113): las mismas reglas que valida el servidor.
plantillas.env.globals["documento"] = documento
plantillas.env.globals["paises"] = paises
# Etiquetas de estado del presupuesto (FR-209, FR-209a).
plantillas.env.globals["etiquetas_estado"] = estado.ETIQUETAS

COOKIE = "sesion"

# ------------------------------------------------------------ tema (FR-121 a FR-126, research R12, R14)
# Se recuerda por dispositivo en la cookie `tema`. El servidor pinta cada página ya con el tema
# correcto (sin destello): base.html pone el `media` del enlace a tokens-oscuro.css y el `content`
# del meta color-scheme según esta tabla. Con «sistema» es el navegador quien sigue al dispositivo.
COOKIE_TEMA = "tema"
TEMAS = ("claro", "oscuro", "sistema")
APARIENCIA = {  # tema: (media del <link id="tokens-oscuro">, content del <meta name="color-scheme">)
    "claro": ("not all", "light"),
    "oscuro": ("all", "dark"),
    "sistema": ("(prefers-color-scheme: dark)", "light dark"),
}


def tema_actual(request: Request) -> str:
    """Tema de la cookie si es válido y hay sesión; si no, «sistema» (FR-122, FR-124).

    `request.state.usuario` lo pone `usuario_actual`: las páginas sin sesión (entrar, crear titular,
    errores de direcciones inexistentes) no lo tienen y por eso siguen al sistema.
    """
    tema = request.cookies.get(COOKIE_TEMA)
    if tema in TEMAS and getattr(request.state, "usuario", None):
        return tema
    return "sistema"


plantillas.env.globals["tema_actual"] = tema_actual
plantillas.env.globals["APARIENCIA"] = APARIENCIA


class SinSesion(Exception):
    """Se convierte en 303 a /entrar o en 401 con HX-Redirect (app.py)."""


def es_htmx(request: Request) -> bool:
    return request.headers.get("HX-Request") == "true"


def usuario_actual(request: Request, conn: sqlite3.Connection = Depends(get_db)) -> dict:
    usuario = seguridad.usuario_de_sesion(conn, request.cookies.get(COOKIE))
    if usuario is None:
        raise SinSesion()
    request.state.usuario = usuario
    return usuario


def solo_titular(usuario: dict = Depends(usuario_actual)) -> dict:
    if usuario["tipo"] != "titular":
        raise HTTPException(status_code=403)
    return usuario


def pagina(request: Request, nombre: str, contexto: dict | None = None, status_code: int = 200):
    ctx = {"usuario": getattr(request.state, "usuario", None)}
    ctx.update(contexto or {})
    return plantillas.TemplateResponse(request, nombre, ctx, status_code=status_code)


def redirigir(request: Request, url: str) -> Response:
    """Tras una acción: HTMX sigue la cabecera HX-Redirect; un formulario normal, el 303."""
    if es_htmx(request):
        return Response(status_code=200, headers={"HX-Redirect": url})
    return RedirectResponse(url, status_code=303)
