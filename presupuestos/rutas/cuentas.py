"""Mi cuenta y gestión de usuarios por el titular (FR-035, FR-036, FR-039, FR-106, FR-107)."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request

from presupuestos import db, seguridad
from presupuestos.rutas import COOKIE, pagina, redirigir, solo_titular, usuario_actual

router = APIRouter()


# ---------------------------------------------------------------- mi cuenta


@router.get("/mi-cuenta")
def mi_cuenta(request: Request, _u: dict = Depends(usuario_actual)):
    return pagina(request, "mi_cuenta.html", {"errores": {}})


@router.post("/mi-cuenta/contrasena")
async def cambiar_contrasena(request: Request, usuario: dict = Depends(usuario_actual),
                             conn: sqlite3.Connection = Depends(db.get_db)):
    form = await request.form()
    actual, nueva, repetir = (str(form.get(c, "")) for c in ("actual", "nueva", "repetir"))
    fila = conn.execute("SELECT hash_contrasena FROM usuarios WHERE id = ?", (usuario["id"],)).fetchone()
    errores = {}
    if not seguridad.verificar_contrasena(fila["hash_contrasena"], actual):
        errores["actual"] = "La contraseña actual no es correcta."
    nueva_errores = seguridad.validar_nueva(nueva, repetir)
    if "contrasena" in nueva_errores:
        errores["nueva"] = nueva_errores["contrasena"]
    if "repetir" in nueva_errores:
        errores["repetir"] = nueva_errores["repetir"]
    if errores:
        return pagina(request, "mi_cuenta.html", {"errores": errores}, status_code=422)
    with db.transaccion_exclusiva(conn):
        conn.execute("UPDATE usuarios SET hash_contrasena = ? WHERE id = ?",
                     (seguridad.hash_contrasena(nueva), usuario["id"]))
        seguridad.borrar_sesiones_usuario(conn, usuario["id"], excepto=request.cookies.get(COOKIE))
    return pagina(request, "mi_cuenta.html", {"errores": {}, "guardado": True})


# ---------------------------------------------------------------- usuarios (solo titular)


def _pagina_usuarios(request: Request, conn: sqlite3.Connection, status_code: int = 200, **extra):
    usuarios = conn.execute(
        "SELECT id, nombre, email, tipo, activo FROM usuarios ORDER BY tipo DESC, nombre COLLATE NOCASE"
    ).fetchall()
    contexto = {"usuarios": usuarios, "errores_alta": {}, "errores_restablecer": {}, "restablecer_id": None}
    contexto.update(extra)
    return pagina(request, "usuarios.html", contexto, status_code=status_code)


def _asistente(conn: sqlite3.Connection, id_: int) -> dict:
    fila = conn.execute("SELECT id, tipo FROM usuarios WHERE id = ?", (id_,)).fetchone()
    if fila is None:
        raise HTTPException(status_code=404)
    return dict(fila)


@router.get("/usuarios")
def usuarios(request: Request, _t: dict = Depends(solo_titular), conn: sqlite3.Connection = Depends(db.get_db)):
    return _pagina_usuarios(request, conn)


@router.post("/usuarios")
async def alta_asistente(request: Request, _t: dict = Depends(solo_titular),
                         conn: sqlite3.Connection = Depends(db.get_db)):
    form = await request.form()
    nombre = str(form.get("nombre", "")).strip()
    email = str(form.get("email", "")).strip().lower()
    contrasena, repetir = str(form.get("contrasena", "")), str(form.get("repetir", ""))
    alta = {"nombre": nombre, "email": email}
    errores = {}
    if not nombre:
        errores["nombre"] = "Indica el nombre."
    if "@" not in email:
        errores["email"] = "Indica un email válido."
    errores.update(seguridad.validar_nueva(contrasena, repetir))
    if not errores:
        try:
            conn.execute(
                "INSERT INTO usuarios (nombre, email, hash_contrasena, tipo, activo, creado_en) "
                "VALUES (?, ?, ?, 'asistente', 1, ?)",
                (nombre, email, seguridad.hash_contrasena(contrasena), db.ahora_utc()),
            )
        except sqlite3.IntegrityError:
            errores["email"] = "Ya existe una cuenta con ese email."
    if errores:
        return _pagina_usuarios(request, conn, 422, errores_alta=errores, alta=alta, abrir_alta=True)
    return _pagina_usuarios(request, conn, mensaje=f"Cuenta de {nombre} creada.")


@router.post("/usuarios/{id_}/baja")
def baja(request: Request, id_: int, _t: dict = Depends(solo_titular), conn: sqlite3.Connection = Depends(db.get_db)):
    if _asistente(conn, id_)["tipo"] == "titular":
        raise HTTPException(status_code=422, detail="El titular no puede darse de baja")
    with db.transaccion_exclusiva(conn):
        conn.execute("UPDATE usuarios SET activo = 0 WHERE id = ?", (id_,))
        seguridad.borrar_sesiones_usuario(conn, id_)
    return redirigir(request, "/usuarios")


@router.post("/usuarios/{id_}/contrasena")
async def nueva_contrasena(request: Request, id_: int, _t: dict = Depends(solo_titular),
                           conn: sqlite3.Connection = Depends(db.get_db)):
    if _asistente(conn, id_)["tipo"] != "asistente":
        raise HTTPException(status_code=422, detail="La contraseña del titular se cambia en «Mi cuenta»")
    form = await request.form()
    contrasena, repetir = str(form.get("contrasena", "")), str(form.get("repetir", ""))
    if errores := seguridad.validar_nueva(contrasena, repetir):
        return _pagina_usuarios(request, conn, 422, errores_restablecer=errores, restablecer_id=id_)
    with db.transaccion_exclusiva(conn):
        conn.execute("UPDATE usuarios SET hash_contrasena = ? WHERE id = ?",
                     (seguridad.hash_contrasena(contrasena), id_))
        seguridad.borrar_sesiones_usuario(conn, id_)
    return _pagina_usuarios(request, conn, mensaje="Contraseña cambiada. La anterior ya no funciona.")
