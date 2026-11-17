"""Inicio y cierre de sesión, creación de la cuenta del titular y elección de tema
(FR-034, FR-037, FR-038, FR-108 a FR-110, FR-117 a FR-122)."""

import os
import sqlite3

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, Response
from starlette.routing import Match, Mount

from presupuestos import db, seguridad
from presupuestos.db import get_db
from presupuestos.rutas import COOKIE, COOKIE_TEMA, TEMAS, pagina, usuario_actual

router = APIRouter()

INCORRECTO = "Email o contraseña incorrectos"
BLOQUEADO = "Demasiados intentos. Vuelve a intentarlo en unos minutos."
AVISOS = {"titular-existe": "La cuenta del titular ya existe. Inicia sesión."}


def _hay_titular(conn: sqlite3.Connection) -> bool:
    return conn.execute("SELECT 1 FROM usuarios WHERE tipo = 'titular'").fetchone() is not None


def _respuesta_con_sesion(token: str) -> RedirectResponse:
    respuesta = RedirectResponse("/", status_code=303)
    respuesta.set_cookie(
        COOKIE,
        token,
        httponly=True,
        samesite="lax",
        secure=os.environ.get("COOKIE_SEGURA", "1") == "1",
        path="/",
    )
    return respuesta


@router.get("/entrar")
def entrar_form(request: Request, aviso: str = "", conn: sqlite3.Connection = Depends(get_db)):
    # Instalación nueva: toda visita acaba aquí y se lleva a crear el titular (R4).
    if not _hay_titular(conn):
        return RedirectResponse("/crear-titular", status_code=303)
    return pagina(request, "entrar.html", {"aviso": AVISOS.get(aviso)})


@router.post("/entrar")
def entrar(
    request: Request,
    email: str = Form(""),
    contrasena: str = Form(""),
    conn: sqlite3.Connection = Depends(get_db),
):
    email = email.strip().lower()
    if seguridad.esta_bloqueado(conn, email):
        return pagina(request, "entrar.html", {"error": BLOQUEADO, "email": email}, status_code=429)

    fila = conn.execute(
        "SELECT id, hash_contrasena, activo FROM usuarios WHERE email = ?", (email,)
    ).fetchone()
    valida = seguridad.verificar_contrasena(fila["hash_contrasena"] if fila else None, contrasena)
    if not (fila and fila["activo"] and valida):
        seguridad.registrar_fallo(conn, email)
        return pagina(request, "entrar.html", {"error": INCORRECTO, "email": email}, status_code=401)

    seguridad.limpiar_intentos(conn, email)
    return _respuesta_con_sesion(seguridad.crear_sesion(conn, fila["id"]))


# ---------------------------------------------------------------- primera puesta en marcha (R4)
# Pública solo mientras no existe titular. El índice único un_solo_titular impide que haya dos
# aunque lleguen dos envíos a la vez. La página no recibe ni muestra datos del perfil (FR-110).


@router.get("/crear-titular")
def crear_titular_form(request: Request, conn: sqlite3.Connection = Depends(get_db)):
    if _hay_titular(conn):
        return RedirectResponse("/entrar", status_code=303)
    return pagina(request, "crear_titular.html", {"errores": {}, "datos": {}})


@router.post("/crear-titular")
def crear_titular(
    request: Request,
    nombre: str = Form(""),
    email: str = Form(""),
    contrasena: str = Form(""),
    repetir: str = Form(""),
    conn: sqlite3.Connection = Depends(get_db),
):
    if _hay_titular(conn):
        return RedirectResponse("/entrar?aviso=titular-existe", status_code=303)
    nombre, email = nombre.strip(), email.strip().lower()
    errores = {}
    if not nombre:
        errores["nombre"] = "Indica tu nombre."
    if "@" not in email:
        errores["email"] = "Indica un email válido."
    errores.update(seguridad.validar_nueva(contrasena, repetir))
    if errores:
        return pagina(request, "crear_titular.html",
                      {"errores": errores, "datos": {"nombre": nombre, "email": email}}, status_code=422)
    try:
        cur = conn.execute(
            "INSERT INTO usuarios (nombre, email, hash_contrasena, tipo, activo, creado_en) "
            "VALUES (?, ?, ?, 'titular', 1, ?)",
            (nombre, email, seguridad.hash_contrasena(contrasena), db.ahora_utc()),
        )
    except sqlite3.IntegrityError:
        return RedirectResponse("/entrar?aviso=titular-existe", status_code=303)
    return _respuesta_con_sesion(seguridad.crear_sesion(conn, cur.lastrowid))


@router.post("/salir")
def salir(request: Request, conn: sqlite3.Connection = Depends(get_db)):
    seguridad.borrar_sesion(conn, request.cookies.get(COOKIE))
    respuesta = RedirectResponse("/entrar", status_code=303)
    respuesta.delete_cookie(COOKIE, path="/")
    return respuesta


# ---------------------------------------------------------------- Tema (FR-117 a FR-122, research R12, R15)
# Guarda la elección en la cookie `tema` del dispositivo; no toca la base de datos. Cerrar sesión no
# la borra. app.js la envía con la cabecera X-Tema-Fetch (204); sin JS, el formulario recarga la pantalla.

DURACION_TEMA = 400 * 24 * 60 * 60  # 400 días: el máximo que admiten los navegadores


def _destino(request: Request, volver: str) -> str:
    """`volver` solo si es una ruta interna que la app abre con GET; si no, el historial (FR-120).

    Así no se redirige a otro sitio y no se da un 405 cuando la pantalla actual es la respuesta de un
    envío con errores (p. ej. /mi-cuenta/contrasena, que solo admite POST).
    """
    if not volver.startswith("/") or volver.startswith("//"):
        return "/"
    # Se pregunta a cada ruta registrada si atiende un GET a esa dirección (sin la consulta).
    # Match.FULL = coincide la dirección y el método; los archivos estáticos (Mount) no cuentan.
    alcance = {"type": "http", "method": "GET", "path": volver.split("?")[0],
               "root_path": "", "headers": [], "query_string": b""}
    for r in request.app.routes:
        if not isinstance(r, Mount) and r.matches(alcance)[0] == Match.FULL:
            return volver
    return "/"


def _poner_cookie_tema(respuesta: Response, tema: str) -> Response:
    respuesta.set_cookie(
        COOKIE_TEMA,
        tema,
        max_age=DURACION_TEMA,
        httponly=True,
        samesite="lax",
        secure=os.environ.get("COOKIE_SEGURA", "1") == "1",
        path="/",
    )
    return respuesta


@router.post("/tema")
def elegir_tema(
    request: Request,
    tema: str = Form(""),
    volver: str = Form(""),
    _usuario: dict = Depends(usuario_actual),
):
    if tema not in TEMAS:
        raise HTTPException(status_code=422)
    if request.headers.get("X-Tema-Fetch") == "1":
        return _poner_cookie_tema(Response(status_code=204), tema)
    return _poner_cookie_tema(RedirectResponse(_destino(request, volver), status_code=303), tema)
