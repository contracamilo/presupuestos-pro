"""Presupuestos, líneas, PDF e historial (FR-010 a FR-026, FR-044)."""

import base64
import json
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from presupuestos import db
from presupuestos.dominio import estado, fechas, formato
from presupuestos.dominio.nombre_archivo import nombre_pdf
from presupuestos.dominio.validacion import requisitos_descarga
from presupuestos.rutas import es_htmx, pagina, plantillas, redirigir, usuario_actual

router = APIRouter(dependencies=[Depends(usuario_actual)])

TIPOS_IVA = (21, 10, 4, 0)
UNIDADES = ("hora", "día", "proyecto", "unidad")


# ---------------------------------------------------------------- utilidades


def _contexto(conn: sqlite3.Connection, id_: int) -> dict:
    datos = db.cargar_presupuesto(conn, id_)
    if datos is None:
        raise HTTPException(status_code=404)
    servicios = conn.execute(
        "SELECT id, nombre, unidad, precio_cent FROM servicios WHERE archivado = 0 ORDER BY nombre"
    ).fetchall()
    calc = datos["calculo"]
    p = datos["presupuesto"]
    return {
        "p": p,
        "estado": estado.estado(p["emisor_congelado"], p["fecha_validez"], fechas.hoy()),  # FR-209
        "lineas": list(zip(datos["lineas"], calc.importes_linea)),
        "cliente": datos["cliente"],
        "calc": calc,
        "perfil": datos["perfil_efectivo"],
        "servicios": servicios,
        "tipos_iva": TIPOS_IVA,
        "unidades": UNIDADES,
    }


def _fragmento(request: Request, nombre: str, contexto: dict) -> HTMLResponse:
    return plantillas.TemplateResponse(request, nombre, contexto)


def _error(mensaje: str, destino: str) -> HTMLResponse:
    """422 que HTMX muestra en la zona de error indicada (y no en los totales)."""
    html = plantillas.env.from_string('<p class="error">{{ m }}</p>').render(m=mensaje)
    return HTMLResponse(html, status_code=422, headers={"HX-Retarget": destino, "HX-Reswap": "innerHTML"})


def _tocar(conn: sqlite3.Connection, id_: int) -> None:
    conn.execute("UPDATE presupuestos SET actualizado_en = ? WHERE id = ?", (db.ahora_utc(), id_))


def _existe(conn: sqlite3.Connection, id_: int) -> dict:
    fila = conn.execute("SELECT * FROM presupuestos WHERE id = ?", (id_,)).fetchone()
    if fila is None:
        raise HTTPException(status_code=404)
    return dict(fila)


def respuesta_cabecera(request: Request, conn: sqlite3.Connection, id_: int) -> HTMLResponse:
    """Totales + fechas + cliente recalculados (fragmento tras un cambio de cabecera)."""
    return _fragmento(request, "fragmentos/_respuesta_cabecera.html", _contexto(conn, id_))


def _respuesta_lineas(request: Request, conn: sqlite3.Connection, id_: int) -> HTMLResponse:
    return _fragmento(request, "fragmentos/_respuesta_lineas.html", _contexto(conn, id_))


# ---------------------------------------------------------------- historial (FR-026)


@router.get("/")
def historial(request: Request, q: str = "", conn: sqlite3.Connection = Depends(db.get_db)):
    sql = (
        "SELECT p.*, c.nombre AS cliente_nombre FROM presupuestos p "
        "LEFT JOIN clientes c ON c.id = p.cliente_id"
    )
    parametros: tuple = ()
    if q.strip():
        sql += " WHERE p.numero LIKE ? OR c.nombre LIKE ?"
        patron = f"%{q.strip()}%"
        parametros = (patron, patron)
    sql += " ORDER BY p.fecha_emision DESC, p.numero DESC"

    perfil, ajustes = db.leer_perfil(conn), db.leer_ajustes(conn)
    hoy = fechas.hoy()
    filas = []
    for fila in conn.execute(sql, parametros).fetchall():
        p = dict(fila)
        lineas = conn.execute(
            "SELECT cantidad_cent, precio_cent FROM lineas WHERE presupuesto_id = ?", (p["id"],)
        ).fetchall()
        cliente = None
        if p["cliente_id"] is not None:
            cliente = conn.execute("SELECT * FROM clientes WHERE id = ?", (p["cliente_id"],)).fetchone()
        p["total"] = db.calcular_presupuesto(p, lineas, cliente, perfil, ajustes).total
        p["estado"] = estado.estado(p["emisor_congelado"], p["fecha_validez"], hoy)  # FR-209
        filas.append(p)

    contexto = {"presupuestos": filas, "q": q}
    if es_htmx(request) and request.headers.get("HX-Target") == "lista-presupuestos":
        return _fragmento(request, "fragmentos/_historial_lista.html", contexto)
    return pagina(request, "historial.html", contexto)


# ---------------------------------------------------------------- presupuesto


@router.post("/presupuestos")
def crear(request: Request, conn: sqlite3.Connection = Depends(db.get_db)):
    id_ = db.crear_presupuesto(conn, fechas.hoy())
    return redirigir(request, f"/presupuestos/{id_}")


@router.get("/presupuestos/{id_}")
def ver(request: Request, id_: int, volver: str = "", conn: sqlite3.Connection = Depends(db.get_db)):
    """`volver` es la búsqueda activa del historial, para regresar a ella (FR-105, R2)."""
    contexto = _contexto(conn, id_)
    contexto["volver"] = volver
    return pagina(request, "presupuesto.html", contexto)


@router.put("/presupuestos/{id_}")
async def guardar_campo(request: Request, id_: int, conn: sqlite3.Connection = Depends(db.get_db)):
    """Guarda un campo cada vez (FR-011, FR-014, FR-016, FR-017) y devuelve los totales recalculados."""
    p = _existe(conn, id_)
    form = await request.form()

    if "fecha_emision" in form:
        try:
            emision = fechas.leer_fecha(form["fecha_emision"])
        except ValueError as e:
            return _error(str(e), "#error-cabecera")
        if p["validez_editada_a_mano"]:
            if p["fecha_validez"] < emision:
                return _error("La fecha de validez no puede ser anterior a la de emisión.", "#error-cabecera")
            validez = p["fecha_validez"]
        else:
            validez = fechas.sumar_dias(emision, db.leer_ajustes(conn)["dias_validez"])
        conn.execute(
            "UPDATE presupuestos SET fecha_emision = ?, fecha_validez = ? WHERE id = ?", (emision, validez, id_)
        )
    elif "fecha_validez" in form:
        try:
            validez = fechas.leer_fecha(form["fecha_validez"])
        except ValueError as e:
            return _error(str(e), "#error-cabecera")
        if validez < p["fecha_emision"]:
            return _error("La fecha de validez no puede ser anterior a la de emisión.", "#error-cabecera")
        conn.execute(
            "UPDATE presupuestos SET fecha_validez = ?, validez_editada_a_mano = 1 WHERE id = ?", (validez, id_)
        )
    elif "tipo_iva" in form:
        try:
            tipo = int(form["tipo_iva"])
        except ValueError:
            tipo = -1
        if tipo not in TIPOS_IVA:
            return _error("El tipo de IVA debe ser 21 %, 10 %, 4 % o 0 %.", "#error-cabecera")
        conn.execute("UPDATE presupuestos SET tipo_iva = ? WHERE id = ?", (tipo, id_))
    elif "notas" in form:
        conn.execute("UPDATE presupuestos SET notas = ? WHERE id = ?", (str(form["notas"]).strip(), id_))
    elif "cliente_id" in form:
        cliente = conn.execute(
            "SELECT id FROM clientes WHERE id = ? AND archivado = 0 AND anonimizado = 0",
            (str(form["cliente_id"]),),
        ).fetchone()
        if cliente is None:
            return _error("Ese cliente ya no está disponible.", "#error-cabecera")
        conn.execute("UPDATE presupuestos SET cliente_id = ? WHERE id = ?", (cliente["id"], id_))
    else:
        return _error("No se ha indicado ningún cambio.", "#error-cabecera")

    _tocar(conn, id_)
    return respuesta_cabecera(request, conn, id_)


@router.delete("/presupuestos/{id_}")
def borrar(request: Request, id_: int, conn: sqlite3.Connection = Depends(db.get_db)):
    """Borra el presupuesto y sus líneas; el contador no cambia (FR-019)."""
    _existe(conn, id_)
    conn.execute("DELETE FROM presupuestos WHERE id = ?", (id_,))
    return redirigir(request, "/")


# ---------------------------------------------------------------- líneas (FR-012, FR-013)


def _leer_linea(form) -> tuple[dict | None, str | None]:
    descripcion = str(form.get("descripcion", "")).strip()
    if not descripcion:
        return None, "La descripción es obligatoria."
    try:
        cantidad = formato.leer_cantidad(str(form.get("cantidad", "")))
    except ValueError as e:
        return None, f"Cantidad: {e}"
    if cantidad <= 0:
        return None, "La cantidad debe ser mayor que 0."
    try:
        precio = formato.leer_importe(str(form.get("precio", "")))
    except ValueError as e:
        return None, f"Precio: {e}"
    unidad = str(form.get("unidad", "")).strip() or None
    if unidad is not None and unidad not in UNIDADES:
        return None, "Elige una unidad de la lista."
    return {"descripcion": descripcion, "cantidad_cent": cantidad, "precio_cent": precio, "unidad": unidad}, None


@router.post("/presupuestos/{id_}/lineas")
async def anadir_linea(request: Request, id_: int, conn: sqlite3.Connection = Depends(db.get_db)):
    _existe(conn, id_)
    form = await request.form()
    servicio_id = str(form.get("servicio_id", "")).strip()
    destino = "#error-nueva-linea"

    if servicio_id:
        destino = "#error-catalogo"
        servicio = conn.execute(
            "SELECT nombre, unidad, precio_cent FROM servicios WHERE id = ? AND archivado = 0", (servicio_id,)
        ).fetchone()
        if servicio is None:
            return _error("Ese servicio ya no está en el catálogo.", destino)
        try:
            cantidad = formato.leer_cantidad(str(form.get("cantidad", "1")))
        except ValueError as e:
            return _error(f"Cantidad: {e}", destino)
        if cantidad <= 0:
            return _error("La cantidad debe ser mayor que 0.", destino)
        # Copia independiente: no se guarda vínculo con el servicio (CA4, CA15).
        linea = {"descripcion": servicio["nombre"], "cantidad_cent": cantidad,
                 "precio_cent": servicio["precio_cent"], "unidad": servicio["unidad"]}
    else:
        linea, error = _leer_linea(form)
        if error:
            return _error(error, destino)

    posicion = conn.execute(
        "SELECT COALESCE(MAX(posicion), 0) + 1 FROM lineas WHERE presupuesto_id = ?", (id_,)
    ).fetchone()[0]
    conn.execute(
        "INSERT INTO lineas (presupuesto_id, posicion, descripcion, unidad, cantidad_cent, precio_cent) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (id_, posicion, linea["descripcion"], linea["unidad"], linea["cantidad_cent"], linea["precio_cent"]),
    )
    _tocar(conn, id_)
    return _respuesta_lineas(request, conn, id_)


def _linea(conn: sqlite3.Connection, id_: int, linea_id: int) -> dict:
    fila = conn.execute(
        "SELECT * FROM lineas WHERE id = ? AND presupuesto_id = ?", (linea_id, id_)
    ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404)
    return dict(fila)


@router.put("/presupuestos/{id_}/lineas/{linea_id}")
async def editar_linea(request: Request, id_: int, linea_id: int, conn: sqlite3.Connection = Depends(db.get_db)):
    _linea(conn, id_, linea_id)
    linea, error = _leer_linea(await request.form())
    if error:
        return _error(error, f"#error-linea-{linea_id}")
    conn.execute(
        "UPDATE lineas SET descripcion = ?, unidad = ?, cantidad_cent = ?, precio_cent = ? WHERE id = ?",
        (linea["descripcion"], linea["unidad"], linea["cantidad_cent"], linea["precio_cent"], linea_id),
    )
    _tocar(conn, id_)
    return _respuesta_lineas(request, conn, id_)


@router.post("/presupuestos/{id_}/lineas/{linea_id}/mover")
async def mover_linea(request: Request, id_: int, linea_id: int, conn: sqlite3.Connection = Depends(db.get_db)):
    actual = _linea(conn, id_, linea_id)
    direccion = (await request.form()).get("direccion")
    if direccion == "arriba":
        vecina = conn.execute(
            "SELECT id, posicion FROM lineas WHERE presupuesto_id = ? AND posicion < ? "
            "ORDER BY posicion DESC LIMIT 1", (id_, actual["posicion"])
        ).fetchone()
    elif direccion == "abajo":
        vecina = conn.execute(
            "SELECT id, posicion FROM lineas WHERE presupuesto_id = ? AND posicion > ? "
            "ORDER BY posicion ASC LIMIT 1", (id_, actual["posicion"])
        ).fetchone()
    else:
        return _error("Dirección no válida.", "#error-lineas")
    if vecina is not None:
        with db.transaccion_exclusiva(conn):
            conn.execute("UPDATE lineas SET posicion = ? WHERE id = ?", (vecina["posicion"], linea_id))
            conn.execute("UPDATE lineas SET posicion = ? WHERE id = ?", (actual["posicion"], vecina["id"]))
        _tocar(conn, id_)
    return _respuesta_lineas(request, conn, id_)


@router.delete("/presupuestos/{id_}/lineas/{linea_id}")
def borrar_linea(request: Request, id_: int, linea_id: int, conn: sqlite3.Connection = Depends(db.get_db)):
    _linea(conn, id_, linea_id)
    conn.execute("DELETE FROM lineas WHERE id = ?", (linea_id,))
    _tocar(conn, id_)
    return _respuesta_lineas(request, conn, id_)


# ---------------------------------------------------------------- PDF (FR-018, FR-021 a FR-025)


def html_pdf(conn: sqlite3.Connection, datos: dict) -> str:
    """HTML del PDF de un presupuesto ya cargado; lo usan la descarga individual y la exportación (FR-304)."""
    from presupuestos.pdf import estilos_comunes

    emisor = datos["perfil_efectivo"]
    logo_uri = None
    if emisor.get("logo_id"):
        logo = conn.execute("SELECT tipo, datos FROM logos WHERE id = ?", (emisor["logo_id"],)).fetchone()
        if logo:
            logo_uri = f"data:{logo['tipo']};base64,{base64.b64encode(logo['datos']).decode()}"

    calc = datos["calculo"]
    return plantillas.get_template("pdf.html").render(
        estilos_comunes=estilos_comunes(),
        p=datos["presupuesto"],
        emisor=emisor,
        logo_uri=logo_uri,
        cliente=datos["cliente"],
        lineas=list(zip(datos["lineas"], calc.importes_linea)),
        calc=calc,
    )


@router.get("/presupuestos/{id_}/pdf")
def descargar_pdf(request: Request, id_: int, conn: sqlite3.Connection = Depends(db.get_db)):
    datos = db.cargar_presupuesto(conn, id_)
    if datos is None:
        raise HTTPException(status_code=404)
    fallos = requisitos_descarga(datos["perfil_efectivo"], datos["cliente"], datos["lineas"])
    if fallos:
        contexto = _contexto(conn, id_)
        contexto["requisitos"] = fallos
        return pagina(request, "presupuesto.html", contexto, status_code=422)

    p = datos["presupuesto"]
    if p["emisor_congelado"] is None:
        perfil, ajustes = datos["perfil"], datos["ajustes"]
        congelado = {k: perfil[k] for k in ("nombre", "nif", "direccion", "email", "telefono", "logo_id")}
        congelado["retencion_activa"] = bool(ajustes["retencion_activa"])
        congelado["tipo_retencion"] = ajustes["tipo_retencion"]
        with db.transaccion_exclusiva(conn):
            conn.execute(
                "UPDATE presupuestos SET emisor_congelado = ? WHERE id = ? AND emisor_congelado IS NULL",
                (json.dumps(congelado, ensure_ascii=False), id_),
            )
        datos = db.cargar_presupuesto(conn, id_)

    from presupuestos.pdf import generar_pdf  # WeasyPrint solo se carga al generar un PDF

    html = html_pdf(conn, datos)
    archivo = nombre_pdf(p["numero"], datos["cliente"]["nombre"])
    return Response(
        generar_pdf(html),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{archivo}"'},
    )
