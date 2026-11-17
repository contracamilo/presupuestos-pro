"""Exportar en un .zip con los PDF de los presupuestos ya descargados (spec 004, contracts/)."""

import io
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
    return {"total": total, "exportables": exportables, "sin_pdf": total - exportables}


def _error(codigo: int, mensaje: str) -> JSONResponse:
    return JSONResponse({"error": mensaje}, status_code=codigo)


@router.post("/exportar")
def exportar(modo: str = Form(""), ids: list[str] = Form([]), conn: sqlite3.Connection = Depends(db.get_db)):
    """Exporta un .zip con los PDF. Solo lectura (FR-305, research E3, E4)."""
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
            exportables = presupuestos_exportables(conn)
            if not exportables:
                return _error(422, "No hay presupuestos que exportar.")
            if marcados is not None:
                if not set(marcados) <= {e["id"] for e in exportables}:
                    return _error(409, "La lista ha cambiado. Cierra la ventana y vuelve a abrirla.")
                exportables = [e for e in exportables if e["id"] in marcados]
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
