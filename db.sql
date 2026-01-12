BEGIN;

-- =========================
-- DROP (por si estas probando)
-- =========================
DROP TABLE IF EXISTS usuario_vendedor CASCADE;
DROP TABLE IF EXISTS usuario_admin_empresa CASCADE;
DROP TABLE IF EXISTS usuario_admin_plataforma CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;

DROP TABLE IF EXISTS suscripcion_pago CASCADE;
DROP TABLE IF EXISTS suscripcion CASCADE;
DROP TABLE IF EXISTS plan CASCADE;

DROP TABLE IF EXISTS empresa_config CASCADE;
DROP TABLE IF EXISTS empresa CASCADE;

-- =========================
-- EMPRESA + CONFIG
-- =========================
CREATE TABLE empresa
(
    empresa_id BIGSERIAL PRIMARY KEY,
    nombre     TEXT        NOT NULL,
    nit        TEXT,
    estado     TEXT        NOT NULL DEFAULT 'ACTIVA',
    creado_en  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE empresa_config
(
    empresa_id     BIGINT PRIMARY KEY REFERENCES empresa (empresa_id) ON DELETE CASCADE,
    moneda         TEXT          NOT NULL DEFAULT 'BOB',
    tasa_impuesto  NUMERIC(6, 3) NOT NULL DEFAULT 0,
    logo_url       TEXT,
    actualizado_en TIMESTAMPTZ   NOT NULL DEFAULT now()
);

-- =========================
-- PLAN + SUSCRIPCION + PAGO SUSCRIPCION
-- =========================
CREATE TABLE plan
(
    plan_id       BIGSERIAL PRIMARY KEY,
    nombre        TEXT           NOT NULL,
    precio        NUMERIC(12, 2) NOT NULL DEFAULT 0,
    periodo_cobro TEXT           NOT NULL
);

CREATE TABLE suscripcion
(
    suscripcion_id BIGSERIAL PRIMARY KEY,
    empresa_id     BIGINT NOT NULL REFERENCES empresa (empresa_id) ON DELETE CASCADE,
    plan_id        BIGINT NOT NULL REFERENCES plan (plan_id),
    estado         TEXT   NOT NULL,
    inicio         DATE   NOT NULL,
    fin            DATE,
    renovacion     DATE,
    UNIQUE (empresa_id, suscripcion_id)
);

CREATE TABLE suscripcion_pago
(
    pago_suscripcion_id BIGSERIAL PRIMARY KEY,
    empresa_id          BIGINT         NOT NULL REFERENCES empresa (empresa_id) ON DELETE CASCADE,
    suscripcion_id      BIGINT         NOT NULL,
    monto               NUMERIC(12, 2) NOT NULL,
    moneda              TEXT           NOT NULL DEFAULT 'BOB',
    metodo              TEXT           NOT NULL,
    referencia_qr       TEXT,
    estado              TEXT           NOT NULL,
    pagado_en           TIMESTAMPTZ,
    UNIQUE (empresa_id, pago_suscripcion_id),
    FOREIGN KEY (empresa_id, suscripcion_id)
        REFERENCES suscripcion (empresa_id, suscripcion_id)
        ON DELETE CASCADE
);

-- =========================
-- USUARIO + ROLES (especializacion)
-- =========================
CREATE TABLE usuario
(
    usuario_id    BIGSERIAL PRIMARY KEY,
    empresa_id    BIGINT      NOT NULL REFERENCES empresa (empresa_id) ON DELETE CASCADE,
    email         TEXT        NOT NULL,
    password_hash TEXT        NOT NULL,
    activo        BOOLEAN     NOT NULL DEFAULT TRUE,
    creado_en     TIMESTAMPTZ NOT NULL DEFAULT now(),
    ultimo_login  TIMESTAMPTZ,
    UNIQUE (empresa_id, email),
    UNIQUE (empresa_id, usuario_id)
);

CREATE TABLE usuario_admin_plataforma
(
    empresa_id BIGINT NOT NULL REFERENCES empresa (empresa_id) ON DELETE CASCADE,
    usuario_id BIGINT NOT NULL,
    PRIMARY KEY (empresa_id, usuario_id),
    FOREIGN KEY (empresa_id, usuario_id)
        REFERENCES usuario (empresa_id, usuario_id)
        ON DELETE CASCADE
);

CREATE TABLE usuario_admin_empresa
(
    empresa_id BIGINT NOT NULL REFERENCES empresa (empresa_id) ON DELETE CASCADE,
    usuario_id BIGINT NOT NULL,
    PRIMARY KEY (empresa_id, usuario_id),
    FOREIGN KEY (empresa_id, usuario_id)
        REFERENCES usuario (empresa_id, usuario_id)
        ON DELETE CASCADE
);

CREATE TABLE usuario_vendedor
(
    empresa_id BIGINT NOT NULL REFERENCES empresa (empresa_id) ON DELETE CASCADE,
    usuario_id BIGINT NOT NULL,
    PRIMARY KEY (empresa_id, usuario_id),
    FOREIGN KEY (empresa_id, usuario_id)
        REFERENCES usuario (empresa_id, usuario_id)
        ON DELETE CASCADE
);

COMMIT;

-- =========================
-- DATOS DE PRUEBA (MVP)
-- =========================
-- Asume que ya existen las tablas:
-- empresa, empresa_config, usuario, usuario_admin_plataforma, usuario_admin_empresa, usuario_vendedor

BEGIN;

-- 1) EMPRESAS
INSERT INTO empresa (nombre, nit, estado)
VALUES ('Tienda Don Pepe', '1234567011', 'ACTIVA'),
       ('Market La Paz', '9876543210', 'ACTIVA');

-- 2) CONFIG EMPRESA
INSERT INTO empresa_config (empresa_id, moneda, tasa_impuesto, logo_url)
VALUES (1, 'BOB', 13.000, 'https://cdn.demo/logo1.png'),
       (2, 'BOB', 13.000, 'https://cdn.demo/logo2.png');

-- 3) USUARIOS (password_hash: string dummy solo para probar queries)
-- OJO: esto no es hash real bcrypt, es solo para poblar datos.
INSERT INTO usuario (empresa_id, email, password_hash, activo)
VALUES (1, 'platformaws@demo.com', 'HASH_DUMMY_1', true),
       (1, 'admin@donpepe.com', 'HASH_DUMMY_2', true),
       (1, 'seller1@donpepe.com', 'HASH_DUMMY_3', true),
       (2, 'admin@marketlapaz.com', 'HASH_DUMMY_4', true),
       (2, 'seller1@marketlapaz.com', 'HASH_DUMMY_5', true);

-- 4) ROLES (tablas separadas)
-- Empresa 1: platform@demo.com = ADMIN_PLATAFORMA
INSERT INTO usuario_admin_plataforma (empresa_id, usuario_id)
SELECT u.empresa_id, u.usuario_id
FROM usuario u
WHERE u.empresa_id = 1
  AND u.email = 'platform@demo.com';

-- Empresa 1: admin@donpepe.com = ADMIN_EMPRESA
INSERT INTO usuario_admin_empresa (empresa_id, usuario_id)
SELECT u.empresa_id, u.usuario_id
FROM usuario u
WHERE u.empresa_id = 1
  AND u.email = 'admin@donpepe.com';

-- Empresa 1: seller1@donpepe.com = VENDEDOR
INSERT INTO usuario_vendedor (empresa_id, usuario_id)
SELECT u.empresa_id, u.usuario_id
FROM usuario u
WHERE u.empresa_id = 1
  AND u.email = 'seller1@donpepe.com';

-- Empresa 2: admin@marketlapaz.com = ADMIN_EMPRESA
INSERT INTO usuario_admin_empresa (empresa_id, usuario_id)
SELECT u.empresa_id, u.usuario_id
FROM usuario u
WHERE u.empresa_id = 2
  AND u.email = 'admin@marketlapaz.com';

-- Empresa 2: seller1@marketlapaz.com = VENDEDOR
INSERT INTO usuario_vendedor (empresa_id, usuario_id)
SELECT u.empresa_id, u.usuario_id
FROM usuario u
WHERE u.empresa_id = 2
  AND u.email = 'seller1@marketlapaz.com';

COMMIT;

-- =========================
-- CONSULTAS PARA VERIFICAR
-- =========================

-- Ver usuarios por empresa
SELECT empresa_id, usuario_id, email, activo
FROM usuario
ORDER BY empresa_id, usuario_id;

-- Ver roles por empresa (join simple)
SELECT u.empresa_id,
       u.usuario_id,
       u.email,
       CASE WHEN ap.usuario_id IS NOT NULL THEN 'ADMIN_PLATAFORMA' END AS admin_plataforma,
       CASE WHEN ae.usuario_id IS NOT NULL THEN 'ADMIN_EMPRESA' END    AS admin_empresa,
       CASE WHEN v.usuario_id IS NOT NULL THEN 'VENDEDOR' END          AS vendedor
FROM usuario u
         LEFT JOIN usuario_admin_plataforma ap
                   ON ap.empresa_id = u.empresa_id AND ap.usuario_id = u.usuario_id
         LEFT JOIN usuario_admin_empresa ae
                   ON ae.empresa_id = u.empresa_id AND ae.usuario_id = u.usuario_id
         LEFT JOIN usuario_vendedor v
                   ON v.empresa_id = u.empresa_id AND v.usuario_id = u.usuario_id
ORDER BY u.empresa_id, u.usuario_id;
