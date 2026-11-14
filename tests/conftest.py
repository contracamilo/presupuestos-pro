import os

import pytest
from fastapi.testclient import TestClient

os.environ["COOKIE_SEGURA"] = "0"  # el cliente de pruebas usa http

from presupuestos import db, seguridad  # noqa: E402
from presupuestos.app import app  # noqa: E402

CONTRASENA = "contraseña-segura-1"


@pytest.fixture
def ruta_bd(tmp_path, monkeypatch):
    ruta = str(tmp_path / "prueba.db")
    monkeypatch.setenv("RUTA_BD", ruta)
    db.inicializar(ruta)
    return ruta


@pytest.fixture
def conn(ruta_bd):
    c = db.conectar(ruta_bd)
    yield c
    c.close()


@pytest.fixture
def cliente(ruta_bd):
    with TestClient(app, follow_redirects=False) as c:
        yield c


def crear_usuario(conn, tipo="titular", email="titular@ejemplo.es", contrasena=CONTRASENA, nombre="Laura"):
    cur = conn.execute(
        "INSERT INTO usuarios (nombre, email, hash_contrasena, tipo, activo, creado_en) VALUES (?, ?, ?, ?, 1, ?)",
        (nombre, email, seguridad.hash_contrasena(contrasena), tipo, db.ahora_utc()),
    )
    return cur.lastrowid


def entrar(cliente, email="titular@ejemplo.es", contrasena=CONTRASENA):
    return cliente.post("/entrar", data={"email": email, "contrasena": contrasena})


@pytest.fixture
def titular(conn, cliente):
    """Cliente HTTP con sesión de titular iniciada."""
    crear_usuario(conn)
    r = entrar(cliente)
    assert r.status_code == 303
    return cliente
