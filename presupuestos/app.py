"""Aplicación FastAPI: cabeceras de seguridad, comprobación de sesión y origen (D7, D9)."""

from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from presupuestos import db
from presupuestos.rutas import SinSesion, es_htmx, pagina

CABECERAS = {
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    ),
    "Strict-Transport-Security": "max-age=31536000",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "same-origin",
}

MENSAJES_ERROR = {
    403: "No tienes permiso para ver esta página.",
    404: "La página que buscas no existe.",
    405: "Esta acción no está permitida.",
    409: "No se puede hacer este cambio.",
    422: "Los datos enviados no son válidos.",
}


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI):
    db.inicializar()
    yield


# Sin /docs, /redoc ni /openapi.json: nada accesible sin sesión (FR-034).
app = FastAPI(lifespan=ciclo_de_vida, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


@app.middleware("http")
async def seguridad_http(request: Request, call_next):
    # Peticiones que modifican datos solo desde nuestro propio dominio (CSRF, D9).
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        origen = request.headers.get("origin")
        if origen and urlsplit(origen).netloc != request.headers.get("host"):
            return HTMLResponse("Origen no permitido.", status_code=403)
    respuesta = await call_next(request)
    for clave, valor in CABECERAS.items():
        respuesta.headers.setdefault(clave, valor)
    if not request.url.path.startswith("/static/"):
        # Tras cerrar sesión, «Atrás» no debe mostrar datos (FR-037, US8 AS8).
        respuesta.headers["Cache-Control"] = "no-store"
    return respuesta


@app.exception_handler(SinSesion)
async def sin_sesion(request: Request, _exc: SinSesion):
    if es_htmx(request):
        return Response(status_code=401, headers={"HX-Redirect": "/entrar"})
    return RedirectResponse("/entrar", status_code=303)


def _error(request: Request, codigo: int, detalle: str | None = None):
    mensaje = detalle or MENSAJES_ERROR.get(codigo, "Se ha producido un error.")
    if es_htmx(request):
        return HTMLResponse(f'<p class="error">{_escapar(mensaje)}</p>', status_code=codigo)
    return pagina(request, "error.html", {"codigo": codigo, "mensaje": mensaje}, status_code=codigo)


def _escapar(texto: str) -> str:
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@app.exception_handler(StarletteHTTPException)
async def error_http(request: Request, exc: StarletteHTTPException):
    detalle = exc.detail if isinstance(exc.detail, str) and exc.status_code in (409, 422) else None
    return _error(request, exc.status_code, detalle)


@app.exception_handler(RequestValidationError)
async def error_validacion(request: Request, _exc: RequestValidationError):
    return _error(request, 422)


from presupuestos.rutas import (  # noqa: E402  (se registran tras crear la app)
    catalogo,
    clientes,
    cuentas,
    exportar,
    perfil,
    presupuestos,
    sesion,
)

for modulo in (sesion, presupuestos, clientes, catalogo, perfil, cuentas, exportar):
    app.include_router(modulo.router)
