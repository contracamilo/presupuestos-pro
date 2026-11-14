"""Clientes: selector del presupuesto, alta, edición, archivo y anonimización (FR-006 a FR-009, FR-043)."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from presupuestos import db
from presupuestos.dominio import documento, paises
from presupuestos.dominio.validacion import TERRITORIOS_ESPANA, validar_cliente
from presupuestos.rutas import es_htmx, pagina, plantillas, redirigir, usuario_actual
from presupuestos.rutas.presupuestos import _contexto

router = APIRouter(dependencies=[Depends(usuario_actual)])

CAMPOS = ("nombre", "nif", "direccion", "pais", "email", "categoria", "territorio", "tipo_documento")


def _datos_formulario(form) -> dict:
    datos = {campo: str(form.get(campo, "")).strip() for campo in CAMPOS}
    datos["nif_iva_verificado"] = 1 if form.get("nif_iva_verificado") else 0
    return datos


def _validar(datos: dict, pais_guardado: str = "") -> list[str]:
    """Reglas de la 001 más tipo de documento y país (FR-112, FR-113, R7, R8). Ajusta el país en España."""
    errores = validar_cliente(datos)
    if errores:
        return errores
    categoria, territorio = datos["categoria"], datos["territorio"]
    if not documento.es_valido(categoria, territorio, datos["tipo_documento"]):
        errores.append("Tipo de documento no válido para este cliente.")
    if territorio in TERRITORIOS_ESPANA:
        datos["pais"] = "España"
    elif not paises.es_valido(territorio, datos["pais"], pais_guardado):
        errores.append("Elige un país de la lista.")
    return errores


def _errores_html(errores: list[str], destino: str) -> HTMLResponse:
    html = plantillas.env.from_string(
        '<ul class="errores">{% for e in errores %}<li>{{ e }}</li>{% endfor %}</ul>'
    ).render(errores=errores)
    return HTMLResponse(html, status_code=422, headers={"HX-Retarget": destino, "HX-Reswap": "innerHTML"})


def _cliente(conn: sqlite3.Connection, id_: int) -> dict:
    fila = conn.execute("SELECT * FROM clientes WHERE id = ?", (id_,)).fetchone()
    if fila is None:
        raise HTTPException(status_code=404)
    return dict(fila)


def _buscar(conn: sqlite3.Connection, q: str, limite: int | None = None) -> list:
    sql = "SELECT * FROM clientes WHERE archivado = 0 AND anonimizado = 0"
    parametros: tuple = ()
    if q.strip():
        sql += " AND (nombre LIKE ? OR nif LIKE ?)"
        patron = f"%{q.strip()}%"
        parametros = (patron, patron)
    sql += " ORDER BY nombre COLLATE NOCASE LIMIT ?"
    return conn.execute(sql, parametros + (limite or -1,)).fetchall()


# ---------------------------------------------------------------- lista y buscador


@router.get("/clientes")
def lista(request: Request, q: str = "", conn: sqlite3.Connection = Depends(db.get_db)):
    contexto = {"clientes": _buscar(conn, q), "q": q}
    if es_htmx(request) and request.headers.get("HX-Target") == "lista-clientes":
        return plantillas.TemplateResponse(request, "fragmentos/_clientes_lista.html", contexto)
    return pagina(request, "clientes.html", contexto)


@router.get("/clientes/buscar")
def buscar(request: Request, q: str = "", presupuesto_id: int | None = None,
           conn: sqlite3.Connection = Depends(db.get_db)):
    """Resultados para el selector del presupuesto (FR-008): solo clientes activos, máximo 20."""
    clientes = _buscar(conn, q, limite=20) if q.strip() else []
    return plantillas.TemplateResponse(
        request, "fragmentos/_resultados_cliente.html",
        {"clientes": clientes, "presupuesto_id": presupuesto_id, "q": q},
    )


# ---------------------------------------------------------------- alta


@router.post("/clientes")
async def crear(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    form = await request.form()
    datos = _datos_formulario(form)
    presupuesto_id = str(form.get("presupuesto_id", "")).strip()
    destino = "#error-cliente-nuevo" if presupuesto_id else "#error-cliente"
    if errores := _validar(datos):
        return _errores_html(errores, destino)

    with db.transaccion_exclusiva(conn):
        cur = conn.execute(
            "INSERT INTO clientes (nombre, nif, direccion, pais, email, categoria, territorio, tipo_documento, "
            "nif_iva_verificado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            tuple(datos[c] for c in CAMPOS) + (datos["nif_iva_verificado"],),
        )
        cliente_id = cur.lastrowid
        if presupuesto_id:
            # Alta desde el presupuesto: queda seleccionado y las líneas no se tocan (FR-008, CA3).
            if conn.execute("SELECT 1 FROM presupuestos WHERE id = ?", (presupuesto_id,)).fetchone() is None:
                raise HTTPException(status_code=404)
            conn.execute(
                "UPDATE presupuestos SET cliente_id = ?, actualizado_en = ? WHERE id = ?",
                (cliente_id, db.ahora_utc(), presupuesto_id),
            )

    if presupuesto_id:
        contexto = _contexto(conn, int(presupuesto_id))
        contexto["reiniciar_nuevo_cliente"] = True
        return plantillas.TemplateResponse(request, "fragmentos/_respuesta_cabecera.html", contexto)
    return redirigir(request, "/clientes")


# ---------------------------------------------------------------- ficha y edición


@router.get("/clientes/{id_}")
def ficha(request: Request, id_: int, conn: sqlite3.Connection = Depends(db.get_db)):
    return pagina(request, "cliente.html", {"c": _cliente(conn, id_)})


@router.put("/clientes/{id_}")
async def editar(request: Request, id_: int, conn: sqlite3.Connection = Depends(db.get_db)):
    cliente = _cliente(conn, id_)
    if cliente["anonimizado"]:
        raise HTTPException(status_code=409, detail="Este cliente fue eliminado y no se puede editar")
    datos = _datos_formulario(await request.form())
    if errores := _validar(datos, pais_guardado=cliente["pais"]):
        return _errores_html(errores, "#error-cliente")
    conn.execute(
        "UPDATE clientes SET nombre = ?, nif = ?, direccion = ?, pais = ?, email = ?, categoria = ?, "
        "territorio = ?, tipo_documento = ?, nif_iva_verificado = ? WHERE id = ?",
        tuple(datos[c] for c in CAMPOS) + (datos["nif_iva_verificado"], id_),
    )
    return plantillas.TemplateResponse(
        request, "fragmentos/_ficha_cliente.html", {"c": _cliente(conn, id_), "guardado": True}
    )


@router.post("/clientes/{id_}/archivar")
def archivar(request: Request, id_: int, conn: sqlite3.Connection = Depends(db.get_db)):
    """No se borra: se archiva y sale de las listas; los presupuestos lo conservan (CL11, FR-009)."""
    _cliente(conn, id_)
    conn.execute("UPDATE clientes SET archivado = 1 WHERE id = ?", (id_,))
    return redirigir(request, "/clientes")


@router.post("/clientes/{id_}/anonimizar")
def anonimizar(request: Request, id_: int, conn: sqlite3.Connection = Depends(db.get_db)):
    """Derecho de supresión (FR-043): irreversible; se conservan categoría y territorio."""
    _cliente(conn, id_)
    conn.execute(
        "UPDATE clientes SET nombre = 'Cliente eliminado', nif = '', direccion = '', pais = '', email = '', "
        "tipo_documento = '', anonimizado = 1, archivado = 1 WHERE id = ?",
        (id_,),
    )
    return redirigir(request, "/clientes")
