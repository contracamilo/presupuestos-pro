"""Exportar en un .zip (spec 004, contracts/): PDF + archivo de datos. Sin cuentas ni contraseñas."""

import base64
import io
import json
import logging
import sqlite3
import zipfile

from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse, Response

from presupuestos import db
from presupuestos.dominio import estado, fechas
from presupuestos.dominio.nombre_archivo import nombre_pdf_zip
from presupuestos.dominio.validacion import requisitos_descarga
from presupuestos.rutas import usuario_actual

router = APIRouter(dependencies=[Depends(usuario_actual)])

SI_NO = {"retencion_activa", "archivado", "nif_iva_verificado", "validez_editada_a_mano"}


def _filas(conn: sqlite3.Connection, sql: str, parametros: tuple = ()) -> list[dict]:
    resultado = []
    for fila in conn.execute(sql, parametros):
        d = dict(fila)
        for clave in SI_NO & d.keys():
            d[clave] = bool(d[clave])
        resultado.append(d)
    return resultado


def datos_exportacion(conn: sqlite3.Connection, ids: list[int] | None = None) -> dict:
    """Archivo de datos: completo (`ids=None`) o solo de los presupuestos de `ids` (contracts/archivo-exportacion.md)."""
    parcial = ids is not None
    marcas = ",".join("?" * len(ids)) if parcial else ""
    perfil = _filas(conn, "SELECT nombre, nif, direccion, email, telefono, logo_id FROM perfil WHERE id = 1")[0]
    ajustes = _filas(conn, "SELECT tipo_iva, retencion_activa, tipo_retencion, dias_validez, mencion_canarias "
                           "FROM ajustes WHERE id = 1")[0]
    servicios = [] if parcial else _filas(
        conn, "SELECT id, nombre, descripcion, unidad, precio_cent, archivado FROM servicios ORDER BY id")
    presupuestos = _filas(conn, "SELECT id, numero, fecha_creacion, fecha_emision, fecha_validez, "
                                "validez_editada_a_mano, tipo_iva, cliente_id, notas, emisor_congelado "
                                "FROM presupuestos" + (f" WHERE id IN ({marcas})" if parcial else "") + " ORDER BY id",
                          tuple(ids) if parcial else ())
    cliente_ids = {p["cliente_id"] for p in presupuestos if p["cliente_id"] is not None}
    clientes = _filas(conn, "SELECT id, nombre, nif, direccion, pais, email, categoria, territorio, "
                            "tipo_documento, nif_iva_verificado, archivado, anonimizado FROM clientes ORDER BY id")
    if parcial:
        clientes = [c for c in clientes if c["id"] in cliente_ids]
    for c in clientes:
        c["anonimizado"] = bool(c["anonimizado"])
    logo_ids = None
    for p in presupuestos:
        if p["emisor_congelado"]:
            p["emisor_congelado"] = json.loads(p["emisor_congelado"])
        p["lineas"] = _filas(conn, "SELECT posicion, descripcion, unidad, cantidad_cent, precio_cent "
                                   "FROM lineas WHERE presupuesto_id = ? ORDER BY posicion", (p["id"],))
    if parcial:
        logo_ids = {p["emisor_congelado"]["logo_id"] for p in presupuestos
                    if p["emisor_congelado"] and p["emisor_congelado"].get("logo_id")}
    logos = [
        {"id": f["id"], "tipo": f["tipo"], "datos_base64": base64.b64encode(f["datos"]).decode()}
        for f in conn.execute("SELECT id, tipo, datos FROM logos ORDER BY id")
        if logo_ids is None or f["id"] in logo_ids
    ]
    contadores = [] if parcial else _filas(conn, "SELECT anio, ultimo FROM contadores ORDER BY anio")
    return {
        "formato": "presupuestospro",
        "version": 2,
        "alcance": "seleccion" if parcial else "completo",
        "exportado_en": db.ahora_utc().replace("+00:00", "Z"),
        "datos": {
            "perfil": None if parcial else perfil,
            "ajustes": None if parcial else ajustes,
            "logos": logos,
            "servicios": servicios,
            "clientes": clientes,
            "presupuestos": presupuestos,
            "contadores": contadores,
        },
    }


def presupuestos_exportables(conn: sqlite3.Connection) -> list[dict]:
    """Presupuestos ya descargados cuyo PDF la app puede generar hoy, en el orden del historial (research E6)."""
    hoy = fechas.hoy()
    resultado = []
    ids = [f["id"] for f in conn.execute(
        "SELECT id FROM presupuestos WHERE emisor_congelado IS NOT NULL ORDER BY fecha_emision DESC, numero DESC")]
    for id_ in ids:
        datos = db.cargar_presupuesto(conn, id_)
        if requisitos_descarga(datos["perfil_efectivo"], datos["cliente"], datos["lineas"]):
            continue
        p = datos["presupuesto"]
        resultado.append({
            "id": id_, "numero": p["numero"], "cliente_nombre": datos["cliente"]["nombre"],
            "estado": estado.estado(p["emisor_congelado"], p["fecha_validez"], hoy),
            "fecha_emision": p["fecha_emision"],
        })
    return resultado


def resumen_exportacion(conn: sqlite3.Connection) -> dict:
    total = conn.execute("SELECT COUNT(*) FROM presupuestos").fetchone()[0]
    exportables = len(presupuestos_exportables(conn))
    return {"total": total, "exportables": exportables, "solo_datos": total - exportables}


def _error(codigo: int, mensaje: str) -> JSONResponse:
    return JSONResponse({"error": mensaje}, status_code=codigo)


@router.post("/exportar")
def exportar(modo: str = Form(""), ids: list[str] = Form([]), conn: sqlite3.Connection = Depends(db.get_db)):
    """Exporta un .zip con los PDF y el archivo de datos. Solo lectura (FR-305, research E3, E4)."""
    from presupuestos.rutas.presupuestos import html_pdf

    if modo not in ("todo", "seleccion"):
        return _error(422, "Elige qué exportar.")
    marcados: list[int] | None = None
    if modo == "seleccion":
        try:
            marcados = sorted({int(i) for i in ids})
        except ValueError:
            marcados = []
        if not marcados:
            return _error(422, "Marca al menos un presupuesto.")

    try:
        conn.execute("BEGIN")  # una sola lectura coherente; se cierra con ROLLBACK, nunca escribe
        try:
            if conn.execute("SELECT COUNT(*) FROM presupuestos").fetchone()[0] == 0:
                return _error(422, "No hay presupuestos que exportar.")
            exportables = presupuestos_exportables(conn)
            if marcados is not None:
                if not set(marcados) <= {e["id"] for e in exportables}:
                    return _error(409, "La lista ha cambiado. Cierra la ventana y vuelve a abrirla.")
                exportables = [e for e in exportables if e["id"] in marcados]
            datos_archivo = datos_exportacion(conn, marcados)
            pdfs = []
            for e in sorted(exportables, key=lambda e: e["numero"]):
                datos = db.cargar_presupuesto(conn, e["id"])
                pdfs.append((nombre_pdf_zip(e["numero"], e["cliente_nombre"]), html_pdf(conn, datos)))
        finally:
            conn.execute("ROLLBACK")

        from presupuestos.pdf import generar_pdf  # WeasyPrint solo se carga al generar un PDF

        base = f"presupuestospro-{'copia' if marcados is None else 'seleccion'}-{fechas.hoy()}"
        salida = io.BytesIO()
        with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr(f"{base}.json", json.dumps(datos_archivo, ensure_ascii=False, indent=2))
            for nombre, html in pdfs:
                z.writestr(nombre, generar_pdf(html))
    except Exception:
        logging.getLogger(__name__).exception("Fallo al preparar la exportación")
        return _error(500, "No se ha podido preparar la copia. Inténtalo de nuevo.")
    return Response(
        salida.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{base}.zip"'},
    )
