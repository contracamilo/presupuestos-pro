"""Perfil del emisor, logo y ajustes fiscales (FR-001 a FR-003)."""

import re
import sqlite3

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import Response

from presupuestos import db
from presupuestos.dominio.validacion import faltan_perfil
from presupuestos.rutas import pagina, redirigir, usuario_actual

router = APIRouter(dependencies=[Depends(usuario_actual)])

MAX_LOGO = 2 * 1024 * 1024
ERROR_LOGO = "Formatos permitidos: PNG, JPG o SVG, hasta 2 MB"
CAMPOS_PERFIL = ("nombre", "nif", "direccion", "email", "telefono")
_INICIO_SVG = re.compile(rb"^\s*(<\?xml[^>]*\?>\s*)?((<!--.*?-->|<!DOCTYPE[^>]*>)\s*)*<svg[\s>]", re.S | re.I)


def tipo_logo(datos: bytes) -> str | None:
    """Tipo real por contenido, no por extensión (D9, D12)."""
    if datos.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if datos.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    try:
        datos.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return "image/svg+xml" if _INICIO_SVG.match(datos.removeprefix(b"\xef\xbb\xbf")) else None


def _pagina_perfil(request: Request, conn: sqlite3.Connection, **extra):
    status = extra.pop("status_code", 200)
    contexto = {"perfil": db.leer_perfil(conn)}
    contexto.update(extra)
    return pagina(request, "perfil.html", contexto, status_code=status)


@router.get("/perfil")
def ver_perfil(request: Request, logo: str = "", conn: sqlite3.Connection = Depends(db.get_db)):
    return _pagina_perfil(request, conn, logo_quitado=logo == "quitado")


@router.post("/perfil")
async def guardar_perfil(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    form = await request.form()
    datos = {c: str(form.get(c, "")).strip() for c in CAMPOS_PERFIL}
    if faltan := faltan_perfil(datos):
        perfil = db.leer_perfil(conn)
        perfil.update(datos)
        return pagina(request, "perfil.html",
                      {"perfil": perfil, "error": "Faltan: " + ", ".join(faltan) + "."}, status_code=422)
    # UPSERT sin tocar logo_id (INSERT OR REPLACE borraría la fila y perdería el logo).
    conn.execute(
        "INSERT INTO perfil (id, nombre, nif, direccion, email, telefono) VALUES (1, ?, ?, ?, ?, ?) "
        "ON CONFLICT(id) DO UPDATE SET nombre = excluded.nombre, nif = excluded.nif, "
        "direccion = excluded.direccion, email = excluded.email, telefono = excluded.telefono",
        tuple(datos[c] for c in CAMPOS_PERFIL),
    )
    return _pagina_perfil(request, conn, guardado=True)


@router.post("/perfil/logo")
async def subir_logo(request: Request, logo: UploadFile = File(...), conn: sqlite3.Connection = Depends(db.get_db)):
    datos = await logo.read(MAX_LOGO + 1)
    tipo = tipo_logo(datos) if 0 < len(datos) <= MAX_LOGO else None
    if tipo is None:
        return _pagina_perfil(request, conn, error_logo=ERROR_LOGO, status_code=422)
    with db.transaccion_exclusiva(conn):
        cur = conn.execute(
            "INSERT INTO logos (tipo, datos, creado_en) VALUES (?, ?, ?)", (tipo, datos, db.ahora_utc())
        )
        conn.execute("UPDATE perfil SET logo_id = ? WHERE id = 1", (cur.lastrowid,))
    return _pagina_perfil(request, conn, logo_guardado=True)


@router.post("/perfil/logo/quitar")
def quitar_logo(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    """Deja el perfil sin logo (FR-116, R10). La fila de logos se conserva: los presupuestos ya
    descargados pueden apuntarla en emisor_congelado (D12)."""
    conn.execute("UPDATE perfil SET logo_id = NULL WHERE id = 1")
    return redirigir(request, "/perfil?logo=quitado")


@router.get("/logos/{id_}")
def ver_logo(id_: int, conn: sqlite3.Connection = Depends(db.get_db)):
    fila = conn.execute("SELECT tipo, datos FROM logos WHERE id = ?", (id_,)).fetchone()
    if fila is None:
        raise HTTPException(status_code=404)
    return Response(
        fila["datos"],
        media_type=fila["tipo"],
        headers={"Content-Security-Policy": "script-src 'none'; sandbox", "X-Content-Type-Options": "nosniff"},
    )


# ---------------------------------------------------------------- ajustes (FR-003)


@router.get("/ajustes")
def ver_ajustes(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    return pagina(request, "ajustes.html", {"ajustes": db.leer_ajustes(conn)})


@router.post("/ajustes")
async def guardar_ajustes(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    form = await request.form()
    errores = []
    try:
        tipo_iva = int(form.get("tipo_iva", ""))
    except ValueError:
        tipo_iva = -1
    if tipo_iva not in (21, 10, 4, 0):
        errores.append("El tipo de IVA debe ser 21 %, 10 %, 4 % o 0 %.")
    try:
        tipo_retencion = int(form.get("tipo_retencion", ""))
    except ValueError:
        tipo_retencion = -1
    if tipo_retencion not in (15, 7):
        errores.append("El tipo de retención debe ser 15 % o 7 %.")
    try:
        dias = int(str(form.get("dias_validez", "")).strip())
    except ValueError:
        dias = 0
    if dias < 1:
        errores.append("Los días de validez deben ser un número entero mayor o igual que 1.")
    datos = {
        "tipo_iva": tipo_iva,
        "retencion_activa": 1 if form.get("retencion_activa") else 0,
        "tipo_retencion": tipo_retencion,
        "dias_validez": dias,
        "mencion_canarias": str(form.get("mencion_canarias", "")).strip(),
    }
    if errores:
        return pagina(request, "ajustes.html", {"ajustes": datos, "errores": errores}, status_code=422)
    conn.execute(
        "UPDATE ajustes SET tipo_iva = ?, retencion_activa = ?, tipo_retencion = ?, dias_validez = ?, "
        "mencion_canarias = ? WHERE id = 1",
        (datos["tipo_iva"], datos["retencion_activa"], datos["tipo_retencion"], datos["dias_validez"],
         datos["mencion_canarias"]),
    )
    return pagina(request, "ajustes.html", {"ajustes": db.leer_ajustes(conn), "guardado": True})
