"""Control de acceso (FR-034 a FR-039, SC-010) y protección de origen (D9)."""

from datetime import datetime, timedelta, timezone

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from presupuestos.app import app
from tests.conftest import CONTRASENA, crear_usuario, entrar

# /salir no muestra datos: sin sesión solo borra la cookie y lleva a /entrar.
PUBLICAS = {"/entrar", "/salir", "/crear-titular"}


def _rutas_protegidas():
    from presupuestos.rutas import catalogo, clientes, cuentas, exportar, perfil, presupuestos, sesion

    todas = [r for m in (sesion, presupuestos, clientes, catalogo, perfil, cuentas, exportar) for r in m.router.routes]
    for ruta in todas:
        if isinstance(ruta, APIRoute) and ruta.path not in PUBLICAS:
            path = ruta.path.replace("{id_}", "1").replace("{linea_id}", "1")
            for metodo in ruta.methods:
                yield metodo, path


def test_toda_ruta_exige_sesion(cliente):
    rutas = list(_rutas_protegidas())
    assert len(rutas) > 20
    for metodo, path in rutas:
        r = cliente.request(metodo, path)
        assert r.status_code == 303 and r.headers["location"] == "/entrar", (metodo, path, r.status_code)
        r = cliente.request(metodo, path, headers={"HX-Request": "true"})
        assert r.status_code == 401 and r.headers["HX-Redirect"] == "/entrar", (metodo, path)


def test_sin_documentacion_publica(cliente):
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert cliente.get(path).status_code in (303, 404)


def test_pantalla_entrar_publica_y_con_cabeceras(conn, cliente):
    crear_usuario(conn)
    r = cliente.get("/entrar")
    assert r.status_code == 200
    assert "Iniciar sesión" in r.text
    assert "default-src 'self'" in r.headers["Content-Security-Policy"]
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["Cache-Control"] == "no-store"


def test_entrar_y_salir(titular):
    assert titular.get("/").status_code == 200
    r = titular.post("/salir")
    assert r.status_code == 303 and r.headers["location"] == "/entrar"
    assert titular.get("/").status_code == 303


def test_credenciales_incorrectas_mensaje_generico(conn, cliente):
    crear_usuario(conn)
    for email in ("titular@ejemplo.es", "nadie@ejemplo.es"):
        r = entrar(cliente, email, "otra-contraseña-mala")
        assert r.status_code == 401
        assert "Email o contraseña incorrectos" in r.text


def test_bloqueo_tras_5_fallos(conn, cliente):
    crear_usuario(conn)
    for _ in range(5):
        assert entrar(cliente, contrasena="contraseña-mala").status_code == 401
    r = entrar(cliente)
    assert r.status_code == 429
    assert "Demasiados intentos" in r.text
    pasado = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    conn.execute("UPDATE intentos_acceso SET bloqueado_hasta = ?", (pasado,))
    assert entrar(cliente).status_code == 303


def test_asistente_sin_acceso_a_usuarios(conn, cliente):
    crear_usuario(conn, "asistente", "pablo@ejemplo.es")
    entrar(cliente, "pablo@ejemplo.es")
    assert cliente.get("/").status_code == 200
    assert cliente.get("/usuarios").status_code == 403
    datos = {"nombre": "X", "email": "x@e.es", "contrasena": "x" * 12, "repetir": "x" * 12}
    assert cliente.post("/usuarios", data=datos).status_code == 403
    assert ">Usuarios<" not in cliente.get("/").text


def test_alta_y_baja_de_asistente(titular, ruta_bd):
    r = titular.post("/usuarios", data={"nombre": "Pablo", "email": "Pablo@Ejemplo.es", "contrasena": CONTRASENA, "repetir": CONTRASENA})
    assert r.status_code == 200
    # Email repetido
    r = titular.post("/usuarios", data={"nombre": "Otro", "email": "pablo@ejemplo.es", "contrasena": CONTRASENA, "repetir": CONTRASENA})
    assert r.status_code == 422 and "Ya existe una cuenta con ese email" in r.text
    # Contraseña corta
    r = titular.post("/usuarios", data={"nombre": "Ana", "email": "ana@ejemplo.es", "contrasena": "corta", "repetir": "corta"})
    assert r.status_code == 422 and "al menos 10 caracteres" in r.text

    with TestClient(app, follow_redirects=False) as pablo:
        assert entrar(pablo, "pablo@ejemplo.es").status_code == 303
        assert pablo.get("/").status_code == 200
        from presupuestos import db
        c = db.conectar(ruta_bd)
        pablo_id = c.execute("SELECT id FROM usuarios WHERE email = 'pablo@ejemplo.es'").fetchone()[0]
        c.close()
        assert titular.post(f"/usuarios/{pablo_id}/baja").status_code == 303
        assert pablo.get("/").status_code == 303
        assert entrar(pablo, "pablo@ejemplo.es").status_code == 401


def test_titular_no_puede_darse_de_baja(titular, conn):
    titular_id = conn.execute("SELECT id FROM usuarios WHERE tipo = 'titular'").fetchone()[0]
    r = titular.post(f"/usuarios/{titular_id}/baja")
    assert r.status_code == 422
    assert conn.execute("SELECT activo FROM usuarios WHERE id = ?", (titular_id,)).fetchone()[0] == 1


def test_titular_restablece_contrasena_de_asistente(titular, conn):
    pablo_id = crear_usuario(conn, "asistente", "pablo@ejemplo.es")
    with TestClient(app, follow_redirects=False) as pablo:
        entrar(pablo, "pablo@ejemplo.es")
        r = titular.post(f"/usuarios/{pablo_id}/contrasena", data={"contrasena": "nueva-contraseña-1", "repetir": "nueva-contraseña-1"})
        assert r.status_code == 200
        assert pablo.get("/").status_code == 303  # su sesión se cierra
        assert entrar(pablo, "pablo@ejemplo.es").status_code == 401
        assert entrar(pablo, "pablo@ejemplo.es", "nueva-contraseña-1").status_code == 303


def test_cambiar_contrasena_invalida_otras_sesiones(conn, cliente):
    crear_usuario(conn)
    entrar(cliente)
    with TestClient(app, follow_redirects=False) as otra:
        entrar(otra)
        r = cliente.post("/mi-cuenta/contrasena", data={"actual": "incorrecta-xx", "nueva": "nueva-contraseña-1", "repetir": "nueva-contraseña-1"})
        assert r.status_code == 422
        r = cliente.post("/mi-cuenta/contrasena", data={"actual": CONTRASENA, "nueva": "corta", "repetir": "corta"})
        assert r.status_code == 422
        r = cliente.post("/mi-cuenta/contrasena", data={"actual": CONTRASENA, "nueva": "nueva-contraseña-1",
                                                         "repetir": "nueva-contraseña-1"})
        assert r.status_code == 200
        assert cliente.get("/").status_code == 200  # la sesión actual sigue
        assert otra.get("/").status_code == 303     # las demás se cierran
    assert entrar(cliente, contrasena=CONTRASENA).status_code == 401
    assert entrar(cliente, contrasena="nueva-contraseña-1").status_code == 303


def test_sesion_caduca_tras_8_horas(titular, conn):
    hace_9h = (datetime.now(timezone.utc) - timedelta(hours=9)).isoformat(timespec="seconds")
    conn.execute("UPDATE sesiones SET ultima_actividad = ?", (hace_9h,))
    assert titular.get("/").status_code == 303


def test_origen_ajeno_rechazado(titular):
    r = titular.post("/presupuestos", headers={"Origin": "https://malo.example"})
    assert r.status_code == 403
    r = titular.post("/presupuestos", headers={"Origin": "http://testserver"})
    assert r.status_code == 303


def test_respuestas_autenticadas_sin_cache(titular):
    r = titular.post("/presupuestos")
    id_ = r.headers["location"].rsplit("/", 1)[1]
    for path in ("/", f"/presupuestos/{id_}"):
        assert titular.get(path).headers["Cache-Control"] == "no-store", path


# ---------------------------------------------------------------- v1.1: titular desde el navegador y Usuarios


def _datos_titular(**cambios):
    datos = {"nombre": "Laura", "email": "Laura@Ejemplo.es", "contrasena": CONTRASENA, "repetir": CONTRASENA}
    datos.update(cambios)
    return datos


def _titulares(conn):
    return conn.execute("SELECT COUNT(*) FROM usuarios WHERE tipo = 'titular'").fetchone()[0]


def test_crear_titular_sin_titular(conn, cliente):
    r = cliente.get("/entrar")
    assert r.status_code == 303 and r.headers["location"] == "/crear-titular"
    r = cliente.get("/crear-titular")
    assert r.status_code == 200 and "Crear la cuenta del titular" in r.text
    assert 'id="menu-lateral"' not in r.text
    r = cliente.post("/crear-titular", data=_datos_titular())
    assert r.status_code == 303 and r.headers["location"] == "/"
    assert "sesion" in r.cookies
    fila = conn.execute("SELECT email, tipo, activo FROM usuarios").fetchone()
    assert tuple(fila) == ("laura@ejemplo.es", "titular", 1)
    assert cliente.get("/").status_code == 200  # sesión abierta


def test_crear_titular_no_muestra_datos_del_perfil(conn, cliente):
    conn.execute("UPDATE perfil SET nombre = 'Estudio Gómez SL', nif = 'B12345678' WHERE id = 1")
    r = cliente.get("/crear-titular")
    assert "Estudio Gómez" not in r.text and "B12345678" not in r.text


def test_crear_titular_con_titular_existente(conn, cliente):
    crear_usuario(conn)
    r = cliente.get("/crear-titular")
    assert r.status_code == 303 and r.headers["location"].startswith("/entrar")
    r = cliente.post("/crear-titular", data=_datos_titular(email="otra@ejemplo.es"))
    assert r.status_code == 303 and r.headers["location"] == "/entrar?aviso=titular-existe"
    assert _titulares(conn) == 1
    r = cliente.get("/entrar?aviso=titular-existe")
    assert "La cuenta del titular ya existe. Inicia sesión." in r.text


def test_crear_titular_validacion(conn, cliente):
    r = cliente.post("/crear-titular", data=_datos_titular(contrasena="123456789", repetir="123456789"))
    assert r.status_code == 422 and "al menos 10 caracteres" in r.text
    r = cliente.post("/crear-titular", data=_datos_titular(repetir="otra-contraseña-9"))
    assert r.status_code == 422 and "Las contraseñas no coinciden." in r.text
    assert 'value="laura@ejemplo.es"' in r.text  # se conserva el email
    assert CONTRASENA not in r.text               # nunca las contraseñas
    r = cliente.post("/crear-titular", data=_datos_titular(nombre=" ", email="sin-arroba"))
    assert r.status_code == 422
    assert conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0


def test_crear_titular_duplicado_por_carrera(conn, cliente, monkeypatch):
    """Otro envío crea el titular entre la comprobación y la inserción: el índice único lo impide."""
    from presupuestos.rutas import sesion

    assert cliente.get("/crear-titular").status_code == 200
    monkeypatch.setattr(sesion, "_hay_titular", lambda c: False)
    crear_usuario(conn, email="primero@ejemplo.es")
    r = cliente.post("/crear-titular", data=_datos_titular())
    assert r.status_code == 303 and r.headers["location"] == "/entrar?aviso=titular-existe"
    assert _titulares(conn) == 1


def test_repetir_distinto_en_alta_y_mi_cuenta(titular, conn):
    r = titular.post("/usuarios", data={"nombre": "Ana", "email": "ana@ejemplo.es",
                                        "contrasena": CONTRASENA, "repetir": "otra-contraseña-9"})
    assert r.status_code == 422 and "Las contraseñas no coinciden." in r.text
    assert "<details class=\"alta-usuario\" open>" in r.text
    assert conn.execute("SELECT COUNT(*) FROM usuarios WHERE email = 'ana@ejemplo.es'").fetchone()[0] == 0
    r = titular.post("/mi-cuenta/contrasena", data={"actual": CONTRASENA, "nueva": "nueva-contraseña-1",
                                                     "repetir": "nueva-contraseña-2"})
    assert r.status_code == 422 and "Las contraseñas no coinciden." in r.text
    pablo_id = crear_usuario(conn, "asistente", "pablo@ejemplo.es")
    r = titular.post(f"/usuarios/{pablo_id}/contrasena", data={"contrasena": "nueva-contraseña-1",
                                                               "repetir": "nueva-contraseña-2"})
    assert r.status_code == 422 and "Las contraseñas no coinciden." in r.text


def test_rutas_cuentas_eliminadas(titular):
    assert titular.get("/cuentas").status_code == 404
    assert ">Usuarios<" in titular.get("/").text


def test_quitar_logo_conserva_la_imagen(titular, conn):
    """La ruta exige sesión (test_toda_ruta_exige_sesion); el logo deja de estar en el perfil pero no se borra."""
    logo_id = conn.execute("INSERT INTO logos (tipo, datos, creado_en) VALUES ('image/png', x'89504e47', "
                           "'2026-11-14')").lastrowid
    conn.execute("UPDATE perfil SET logo_id = ? WHERE id = 1", (logo_id,))
    assert "Quitar logo" in titular.get("/perfil").text
    r = titular.post("/perfil/logo/quitar", headers={"HX-Request": "true"})
    assert r.headers["HX-Redirect"] == "/perfil?logo=quitado"
    assert conn.execute("SELECT logo_id FROM perfil WHERE id = 1").fetchone()[0] is None
    assert conn.execute("SELECT COUNT(*) FROM logos").fetchone()[0] == 1
    r = titular.get("/perfil?logo=quitado")
    assert "Logo quitado." in r.text and "Quitar logo" not in r.text


def test_exportar_solo_por_post(cliente, titular):
    """Spec 004 (FR-314): la exportación suelta por GET ya no existe; /exportar solo admite POST."""
    r = titular.get("/exportar")
    assert r.status_code == 405 and "Esta acción no está permitida" in r.text
    assert 'href="/exportar"' not in titular.get("/").text  # sin enlace en el menú


def test_exportar_post_sin_sesion(cliente):
    r = cliente.post("/exportar", data={"modo": "todo"})
    assert r.status_code == 303 and r.headers["location"] == "/entrar"
