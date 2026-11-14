"""Numeración PRE-AAAA-NNN (FR-010, FR-033, CA10, CL10)."""

import threading

from presupuestos import db


def _numero(conn, id_):
    return conn.execute("SELECT numero FROM presupuestos WHERE id = ?", (id_,)).fetchone()[0]


def test_ca10_correlativos(conn):
    conn.execute("INSERT INTO contadores (anio, ultimo) VALUES (2026, 14)")
    a = db.crear_presupuesto(conn, "2026-11-14")
    b = db.crear_presupuesto(conn, "2026-11-14")
    assert (_numero(conn, a), _numero(conn, b)) == ("PRE-2026-015", "PRE-2026-016")


def test_cl10_cambio_de_anio(conn):
    conn.execute("INSERT INTO contadores (anio, ultimo) VALUES (2026, 120)")
    assert _numero(conn, db.crear_presupuesto(conn, "2027-01-02")) == "PRE-2027-001"


def test_borrar_no_reutiliza_numero(conn):
    db.crear_presupuesto(conn, "2026-11-14")
    ultimo = db.crear_presupuesto(conn, "2026-11-14")
    conn.execute("DELETE FROM presupuestos WHERE id = ?", (ultimo,))
    assert _numero(conn, db.crear_presupuesto(conn, "2026-11-14")) == "PRE-2026-003"


def test_numero_usa_anio_de_creacion(conn):
    id_ = db.crear_presupuesto(conn, "2026-12-31")
    conn.execute("UPDATE presupuestos SET fecha_emision = '2027-01-05', fecha_validez = '2027-02-04' WHERE id = ?", (id_,))
    assert _numero(conn, id_) == "PRE-2026-001"


def test_creaciones_simultaneas_sin_duplicados(ruta_bd):
    numeros, errores = [], []

    def crear():
        c = db.conectar(ruta_bd)
        try:
            numeros.append(_numero(c, db.crear_presupuesto(c, "2026-11-14")))
        except Exception as e:  # pragma: no cover - se informa abajo
            errores.append(e)
        finally:
            c.close()

    hilos = [threading.Thread(target=crear) for _ in range(10)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    assert not errores
    assert sorted(numeros) == [f"PRE-2026-{n:03d}" for n in range(1, 11)]
