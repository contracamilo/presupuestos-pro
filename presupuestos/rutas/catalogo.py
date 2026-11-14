"""Catálogo de servicios (FR-004, FR-005)."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from presupuestos import db
from presupuestos.dominio import formato
from presupuestos.rutas import pagina, plantillas, usuario_actual

router = APIRouter(dependencies=[Depends(usuario_actual)])

UNIDADES = ("hora", "día", "proyecto", "unidad")


def _leer(form) -> tuple[dict | None, str | None]:
    nombre = str(form.get("nombre", "")).strip()
    if not nombre:
        return None, "El nombre es obligatorio."
    unidad = str(form.get("unidad", ""))
    if unidad not in UNIDADES:
        return None, "Elige una unidad: hora, día, proyecto o unidad."
    try:
        precio = formato.leer_importe(str(form.get("precio", "")))
    except ValueError as e:
        return None, f"Precio: {e}"
    return {"nombre": nombre, "descripcion": str(form.get("descripcion", "")).strip(),
            "unidad": unidad, "precio_cent": precio}, None


def _lista(request: Request, conn: sqlite3.Connection, status_code: int = 200):
    servicios = conn.execute("SELECT * FROM servicios WHERE archivado = 0 ORDER BY nombre COLLATE NOCASE").fetchall()
    return plantillas.TemplateResponse(
        request, "fragmentos/_catalogo_lista.html", {"servicios": servicios, "unidades": UNIDADES},
        status_code=status_code,
    )


def _error(mensaje: str, destino: str) -> HTMLResponse:
    html = plantillas.env.from_string('<p class="error">{{ m }}</p>').render(m=mensaje)
    return HTMLResponse(html, status_code=422, headers={"HX-Retarget": destino, "HX-Reswap": "innerHTML"})


@router.get("/catalogo")
def catalogo(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    servicios = conn.execute("SELECT * FROM servicios WHERE archivado = 0 ORDER BY nombre COLLATE NOCASE").fetchall()
    return pagina(request, "catalogo.html", {"servicios": servicios, "unidades": UNIDADES})


@router.post("/catalogo")
async def crear(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    datos, error = _leer(await request.form())
    if error:
        return _error(error, "#error-servicio-nuevo")
    conn.execute(
        "INSERT INTO servicios (nombre, descripcion, unidad, precio_cent) VALUES (?, ?, ?, ?)",
        (datos["nombre"], datos["descripcion"], datos["unidad"], datos["precio_cent"]),
    )
    return _lista(request, conn)


@router.put("/catalogo/{id_}")
async def editar(request: Request, id_: int, conn: sqlite3.Connection = Depends(db.get_db)):
    if conn.execute("SELECT 1 FROM servicios WHERE id = ? AND archivado = 0", (id_,)).fetchone() is None:
        raise HTTPException(status_code=404)
    datos, error = _leer(await request.form())
    if error:
        return _error(error, f"#error-servicio-{id_}")
    conn.execute(
        "UPDATE servicios SET nombre = ?, descripcion = ?, unidad = ?, precio_cent = ? WHERE id = ?",
        (datos["nombre"], datos["descripcion"], datos["unidad"], datos["precio_cent"], id_),
    )
    return _lista(request, conn)


@router.post("/catalogo/{id_}/archivar")
def archivar(request: Request, id_: int, conn: sqlite3.Connection = Depends(db.get_db)):
    """No se borra: sale del selector de líneas y los presupuestos no cambian (CL11)."""
    if conn.execute("SELECT 1 FROM servicios WHERE id = ?", (id_,)).fetchone() is None:
        raise HTTPException(status_code=404)
    conn.execute("UPDATE servicios SET archivado = 1 WHERE id = ?", (id_,))
    return _lista(request, conn)
