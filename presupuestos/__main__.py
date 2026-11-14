"""Órdenes del administrador técnico (contracts/cli-administracion.md).

    python -m presupuestos restablecer-titular
    python -m presupuestos copia --destino /copias
"""

import argparse
import getpass
import sqlite3
import sys
from pathlib import Path

from presupuestos import db, seguridad
from presupuestos.dominio import fechas

# Textos de argparse en español de España (FR-030).
_TEXTOS = {
    "usage: ": "uso: ",
    "options": "opciones",
    "positional arguments": "argumentos",
    "show this help message and exit": "muestra esta ayuda y termina",
    "the following arguments are required: %s": "faltan estos argumentos obligatorios: %s",
    "%(prog)s: error: %(message)s\n": "%(prog)s: error: %(message)s\n",
    "invalid choice: %(value)r (choose from %(choices)s)": "orden no válida: %(value)r (elige entre %(choices)s)",
    "unrecognized arguments: %s": "argumentos no reconocidos: %s",
    "expected one argument": "falta el valor de la opción",
}
argparse._ = lambda texto: _TEXTOS.get(texto, texto)


def _pedir_contrasena() -> str:
    if not sys.stdin.isatty():
        raise SystemExit(
            "Error: la contraseña se pide por teclado y aquí no hay una terminal interactiva.\n"
            "Ejecuta la orden en una terminal normal (con «docker compose exec», sin «-T»)."
        )
    try:
        primera = getpass.getpass("Contraseña nueva: ")
        if error := seguridad.validar_longitud(primera):
            raise SystemExit(f"Error: {error}.")
        if getpass.getpass("Repite la contraseña: ") != primera:
            raise SystemExit("Error: las contraseñas no coinciden.")
    except (EOFError, KeyboardInterrupt):
        raise SystemExit("\nOperación cancelada. No se ha cambiado nada.") from None
    return primera


def restablecer_titular() -> None:
    db.inicializar()
    conn = db.conectar()
    try:
        fila = conn.execute("SELECT id, email FROM usuarios WHERE tipo = 'titular'").fetchone()
        if fila is None:
            raise SystemExit("Error: no existe ninguna cuenta de titular. Créala desde el navegador en /crear-titular.")
        contrasena = _pedir_contrasena()
        with db.transaccion_exclusiva(conn):
            conn.execute(
                "UPDATE usuarios SET hash_contrasena = ? WHERE id = ?",
                (seguridad.hash_contrasena(contrasena), fila["id"]),
            )
            seguridad.borrar_sesiones_usuario(conn, fila["id"])
            seguridad.limpiar_intentos(conn, fila["email"])
        print(f"Contraseña del titular ({fila['email']}) restablecida. Se han cerrado sus sesiones.")
    finally:
        conn.close()


def copia(destino: str) -> Path:
    """Copia en caliente y comprobada de la base de datos (FR-041)."""
    carpeta = Path(destino)
    carpeta.mkdir(parents=True, exist_ok=True)
    archivo = carpeta / f"presupuestospro-{fechas.hoy()}.db"
    origen = db.conectar()
    copia_conn = sqlite3.connect(archivo)
    try:
        origen.backup(copia_conn)
        resultado = copia_conn.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        copia_conn.close()
        origen.close()
    if resultado != "ok":
        raise SystemExit(f"Error: la copia {archivo} no es correcta ({resultado}).")
    print(f"Copia creada: {archivo} ({archivo.stat().st_size / 1024:.1f} KB).")
    return archivo


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m presupuestos", description="Órdenes de administración de PresupuestosPro.")
    ordenes = parser.add_subparsers(dest="orden", required=True, metavar="orden")

    ordenes.add_parser("restablecer-titular", help="Asigna una contraseña nueva al titular.")

    p = ordenes.add_parser("copia", help="Copia de seguridad de la base de datos.")
    p.add_argument("--destino", required=True, help="Carpeta donde guardar la copia.")

    args = parser.parse_args(argv)
    if args.orden == "restablecer-titular":
        restablecer_titular()
    elif args.orden == "copia":
        copia(args.destino)


if __name__ == "__main__":
    sys.exit(main())
