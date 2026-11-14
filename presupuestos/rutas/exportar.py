"""Exportar todos los datos de negocio (FR-029, contracts/archivo-exportacion.md). Sin cuentas ni contraseñas."""

import base64
import json
import sqlite3

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from presupuestos import db
from presupuestos.dominio import fechas
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


def datos_exportacion(conn: sqlite3.Connection) -> dict:
    perfil = _filas(conn, "SELECT nombre, nif, direccion, email, telefono, logo_id FROM perfil WHERE id = 1")[0]
    ajustes = _filas(conn, "SELECT tipo_iva, retencion_activa, tipo_retencion, dias_validez, mencion_canarias "
                           "FROM ajustes WHERE id = 1")[0]
    logos = [
        {"id": f["id"], "tipo": f["tipo"], "datos_base64": base64.b64encode(f["datos"]).decode()}
        for f in conn.execute("SELECT id, tipo, datos FROM logos ORDER BY id")
    ]
    servicios = _filas(conn, "SELECT id, nombre, descripcion, unidad, precio_cent, archivado FROM servicios ORDER BY id")
    clientes = _filas(conn, "SELECT id, nombre, nif, direccion, pais, email, categoria, territorio, "
                            "tipo_documento, nif_iva_verificado, archivado, anonimizado FROM clientes ORDER BY id")
    for c in clientes:
        c["anonimizado"] = bool(c["anonimizado"])
    presupuestos = _filas(conn, "SELECT id, numero, fecha_creacion, fecha_emision, fecha_validez, "
                                "validez_editada_a_mano, tipo_iva, cliente_id, notas, emisor_congelado "
                                "FROM presupuestos ORDER BY id")
    for p in presupuestos:
        if p["emisor_congelado"]:
            p["emisor_congelado"] = json.loads(p["emisor_congelado"])
        p["lineas"] = _filas(conn, "SELECT posicion, descripcion, unidad, cantidad_cent, precio_cent "
                                   "FROM lineas WHERE presupuesto_id = ? ORDER BY posicion", (p["id"],))
    contadores = _filas(conn, "SELECT anio, ultimo FROM contadores ORDER BY anio")
    return {
        "formato": "presupuestospro",
        "version": 2,
        "exportado_en": db.ahora_utc().replace("+00:00", "Z"),
        "datos": {
            "perfil": perfil,
            "ajustes": ajustes,
            "logos": logos,
            "servicios": servicios,
            "clientes": clientes,
            "presupuestos": presupuestos,
            "contadores": contadores,
        },
    }


@router.get("/exportar")
def exportar(conn: sqlite3.Connection = Depends(db.get_db)):
    contenido = json.dumps(datos_exportacion(conn), ensure_ascii=False, indent=2)
    return Response(
        contenido.encode("utf-8"),
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="presupuestospro-copia-{fechas.hoy()}.json"'},
    )
