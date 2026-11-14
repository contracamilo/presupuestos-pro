-- PresupuestosPro v1.1 — esquema completo (data-model.md de la 001 y de la 002)
-- Importes en céntimos, cantidades en centésimas, porcentajes enteros, fechas AAAA-MM-DD.

CREATE TABLE IF NOT EXISTS logos (
    id        INTEGER PRIMARY KEY,
    tipo      TEXT NOT NULL CHECK (tipo IN ('image/png', 'image/jpeg', 'image/svg+xml')),
    datos     BLOB NOT NULL,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS perfil (
    id        INTEGER PRIMARY KEY CHECK (id = 1),
    nombre    TEXT NOT NULL DEFAULT '',
    nif       TEXT NOT NULL DEFAULT '',
    direccion TEXT NOT NULL DEFAULT '',
    email     TEXT NOT NULL DEFAULT '',
    telefono  TEXT NOT NULL DEFAULT '',
    logo_id   INTEGER REFERENCES logos(id)
);
INSERT OR IGNORE INTO perfil (id) VALUES (1);

CREATE TABLE IF NOT EXISTS ajustes (
    id               INTEGER PRIMARY KEY CHECK (id = 1),
    tipo_iva         INTEGER NOT NULL DEFAULT 21 CHECK (tipo_iva IN (21, 10, 4, 0)),
    retencion_activa INTEGER NOT NULL DEFAULT 0 CHECK (retencion_activa IN (0, 1)),
    tipo_retencion   INTEGER NOT NULL DEFAULT 15 CHECK (tipo_retencion IN (15, 7)),
    dias_validez     INTEGER NOT NULL DEFAULT 30 CHECK (dias_validez >= 1),
    mencion_canarias TEXT NOT NULL DEFAULT ''
);
INSERT OR IGNORE INTO ajustes (id) VALUES (1);

CREATE TABLE IF NOT EXISTS servicios (
    id          INTEGER PRIMARY KEY,
    nombre      TEXT NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    unidad      TEXT NOT NULL CHECK (unidad IN ('hora', 'día', 'proyecto', 'unidad')),
    precio_cent INTEGER NOT NULL CHECK (precio_cent >= 0),
    archivado   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS clientes (
    id                 INTEGER PRIMARY KEY,
    nombre             TEXT NOT NULL,
    nif                TEXT NOT NULL DEFAULT '',
    direccion          TEXT NOT NULL DEFAULT '',
    pais               TEXT NOT NULL DEFAULT '',
    email              TEXT NOT NULL DEFAULT '',
    categoria          TEXT NOT NULL CHECK (categoria IN ('empresa', 'particular')),
    territorio         TEXT NOT NULL CHECK (territorio IN ('peninsula', 'canarias', 'ue', 'fuera_ue')),
    nif_iva_verificado INTEGER NOT NULL DEFAULT 0,
    archivado          INTEGER NOT NULL DEFAULT 0,
    anonimizado        INTEGER NOT NULL DEFAULT 0,
    tipo_documento     TEXT NOT NULL DEFAULT '' CHECK (tipo_documento IN ('', 'nif', 'cif', 'nie', 'nif_iva_ue', 'extranjero')),
    CHECK (categoria = 'empresa' OR territorio IN ('peninsula', 'canarias')),
    CHECK (nif_iva_verificado = 0 OR territorio = 'ue')
);

CREATE TABLE IF NOT EXISTS presupuestos (
    id                     INTEGER PRIMARY KEY,
    numero                 TEXT NOT NULL UNIQUE,
    fecha_creacion         TEXT NOT NULL,
    fecha_emision          TEXT NOT NULL,
    fecha_validez          TEXT NOT NULL,
    validez_editada_a_mano INTEGER NOT NULL DEFAULT 0,
    tipo_iva               INTEGER NOT NULL CHECK (tipo_iva IN (21, 10, 4, 0)),
    cliente_id             INTEGER REFERENCES clientes(id),
    notas                  TEXT NOT NULL DEFAULT '',
    emisor_congelado       TEXT,
    actualizado_en         TEXT NOT NULL,
    CHECK (fecha_validez >= fecha_emision)
);

CREATE TABLE IF NOT EXISTS lineas (
    id             INTEGER PRIMARY KEY,
    presupuesto_id INTEGER NOT NULL REFERENCES presupuestos(id) ON DELETE CASCADE,
    posicion       INTEGER NOT NULL,
    descripcion    TEXT NOT NULL,
    unidad         TEXT,
    cantidad_cent  INTEGER NOT NULL CHECK (cantidad_cent > 0),
    precio_cent    INTEGER NOT NULL CHECK (precio_cent >= 0)
);
CREATE INDEX IF NOT EXISTS lineas_presupuesto ON lineas(presupuesto_id, posicion);

CREATE TABLE IF NOT EXISTS contadores (
    anio   INTEGER PRIMARY KEY,
    ultimo INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS usuarios (
    id              INTEGER PRIMARY KEY,
    nombre          TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE COLLATE NOCASE,
    hash_contrasena TEXT NOT NULL,
    tipo            TEXT NOT NULL CHECK (tipo IN ('titular', 'asistente')),
    activo          INTEGER NOT NULL DEFAULT 1,
    creado_en       TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS un_solo_titular ON usuarios(tipo) WHERE tipo = 'titular';

CREATE TABLE IF NOT EXISTS sesiones (
    hash_token       TEXT PRIMARY KEY,
    usuario_id       INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    creada_en        TEXT NOT NULL,
    ultima_actividad TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS intentos_acceso (
    email           TEXT PRIMARY KEY,
    fallos          INTEGER NOT NULL DEFAULT 0,
    bloqueado_hasta TEXT
);

PRAGMA user_version = 2;
