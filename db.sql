drop table if exists notificacion cascade;
drop table if exists venta_detalle cascade;
drop table if exists venta cascade;

drop table if exists compra_detalle cascade;
drop table if exists compra cascade;
drop table if exists proveedor cascade;

drop table if exists producto cascade;
drop table if exists categoria cascade;

drop table if exists cliente_empresa cascade;
drop table if exists cliente cascade;

drop table if exists usuario_encargado_inventario cascade;
drop table if exists usuario_vendedor cascade;
drop table if exists usuario_admin_empresa cascade;
drop table if exists usuario_empresa cascade;
drop table if exists platform_admin_profile cascade;
drop table if exists usuario_admin_plataforma cascade;
drop table if exists usuario cascade;

drop table if exists empresa_settings cascade;
drop table if exists plan cascade;
drop table if exists empresa cascade;

drop table if exists token_blocklist cascade;

create table empresa
(
    empresa_id bigserial primary key,
    nombre     text        not null,
    nit        text,
    estado     text        not null default 'ACTIVA',
    creado_en  timestamptz not null default now()
);

create index idx_empresa_nombre on empresa (nombre);

create table plan
(
    plan_id       bigserial primary key,
    nombre        text           not null,
    precio        numeric(12, 2) not null default 0,
    periodo_cobro text           not null
);

create index idx_plan_nombre on plan (nombre);

create table empresa_settings
(
    empresa_id                bigint primary key references empresa (empresa_id) on delete cascade,

    moneda                    text          not null default 'BOB',
    tasa_impuesto             numeric(6, 3) not null default 0,
    logo_url                  text,

    plan_id                   bigint references plan (plan_id),
    suscripcion_estado        text          not null default 'INACTIVA',
    suscripcion_inicio        date,
    suscripcion_fin           date,
    suscripcion_renovacion    date,

    ultimo_pago_monto         numeric(12, 2),
    ultimo_pago_moneda        text                   default 'BOB',
    ultimo_pago_metodo        text,
    ultimo_pago_referencia_qr text,
    ultimo_pago_estado        text,
    ultimo_pagado_en          timestamptz,

    actualizado_en            timestamptz   not null default now()
);

create table usuario
(
    usuario_id    bigserial primary key,
    email         text        not null unique,
    password_hash text        not null,
    activo        boolean     not null default true,
    creado_en     timestamptz not null default now(),
    ultimo_login  timestamptz
);

create table usuario_admin_plataforma
(
    usuario_id bigint primary key references usuario (usuario_id) on delete cascade
);

create table platform_admin_profile
(
    usuario_id   bigint primary key references usuario (usuario_id) on delete cascade,
    display_name text,
    telefono     text
);

create table usuario_empresa
(
    empresa_id bigint      not null references empresa (empresa_id) on delete cascade,
    usuario_id bigint      not null references usuario (usuario_id) on delete cascade,
    activo     boolean     not null default true,
    creado_en  timestamptz not null default now(),
    primary key (empresa_id, usuario_id)
);

create index idx_usuario_empresa_usuario on usuario_empresa (usuario_id);

create table usuario_admin_empresa
(
    empresa_id bigint not null,
    usuario_id bigint not null,
    primary key (empresa_id, usuario_id),
    foreign key (empresa_id, usuario_id) references usuario_empresa (empresa_id, usuario_id) on delete cascade
);

create table usuario_vendedor
(
    empresa_id bigint not null,
    usuario_id bigint not null,
    primary key (empresa_id, usuario_id),
    foreign key (empresa_id, usuario_id) references usuario_empresa (empresa_id, usuario_id) on delete cascade
);

create table usuario_encargado_inventario
(
    empresa_id bigint not null,
    usuario_id bigint not null,
    primary key (empresa_id, usuario_id),
    foreign key (empresa_id, usuario_id) references usuario_empresa (empresa_id, usuario_id) on delete cascade
);

create table cliente
(
    cliente_id    bigserial primary key,
    email         text        not null unique,
    password_hash text        not null,
    nombre_razon  text        not null,
    nit_ci        text,
    telefono      text,
    activo        boolean     not null default true,
    creado_en     timestamptz not null default now(),
    ultimo_login  timestamptz
);

create table cliente_empresa
(
    empresa_id bigint      not null references empresa (empresa_id) on delete cascade,
    cliente_id bigint      not null references cliente (cliente_id) on delete cascade,
    activo     boolean     not null default true,
    creado_en  timestamptz not null default now(),
    primary key (empresa_id, cliente_id)
);

create index idx_cliente_empresa_cliente on cliente_empresa (cliente_id);
create index idx_cliente_empresa_empresa on cliente_empresa (empresa_id);

create table categoria
(
    categoria_id bigserial primary key,
    empresa_id   bigint  not null references empresa (empresa_id) on delete cascade,
    nombre       text    not null,
    activo       boolean not null default true,
    unique (empresa_id, nombre),
    unique (empresa_id, categoria_id)
);

create index idx_categoria_empresa on categoria (empresa_id);

create table producto
(
    producto_id  bigserial primary key,
    empresa_id   bigint         not null references empresa (empresa_id) on delete cascade,
    categoria_id bigint         not null,
    codigo       text           not null,
    descripcion  text           not null,
    precio       numeric(12, 2) not null default 0,
    stock        numeric(12, 3) not null default 0,
    stock_min    integer        not null default 0,
    activo       boolean        not null default true,

    image_url       text,
    image_mime_type text,
    image_updated_at timestamptz,

    unique (empresa_id, codigo),
    unique (empresa_id, producto_id),

    foreign key (empresa_id, categoria_id) references categoria (empresa_id, categoria_id),

    check (precio >= 0),
    check (stock >= 0),
    check (stock_min >= 0),
    check (image_url is null or image_url ~* '^https?://')
    );

create index idx_producto_empresa on producto (empresa_id);
create index idx_producto_categoria on producto (empresa_id, categoria_id);

create table venta
(
    venta_id                  bigserial primary key,
    empresa_id                bigint         not null references empresa (empresa_id) on delete cascade,
    cliente_id                bigint         not null,

    fecha_hora                timestamptz    not null default now(),
    total                     numeric(12, 2) not null default 0,
    descuento_total           numeric(12, 2) not null default 0,
    estado                    text           not null default 'CREADA',

    pago_metodo               text,
    pago_monto                numeric(12, 2),
    pago_referencia_qr        text,
    pago_estado               text,
    pagado_en                 timestamptz,

    comprobante_tipo          text,
    comprobante_numero        text,
    comprobante_url_pdf       text,
    comprobante_emitido_en    timestamptz,

    envio_departamento        text,
    envio_ciudad              text,
    envio_zona_barrio         text,
    envio_direccion_linea     text,
    envio_referencia          text,
    envio_telefono_receptor   text,
    envio_costo               numeric(12, 2) not null default 0,
    envio_estado              text,
    envio_tracking            text,
    envio_fecha_despacho      timestamptz,
    envio_fecha_entrega       timestamptz,

    confirmado_por_usuario_id bigint         references usuario (usuario_id) on delete set null,
    confirmado_en             timestamptz,

    unique (empresa_id, venta_id),

    foreign key (empresa_id, cliente_id) references cliente_empresa (empresa_id, cliente_id) on delete restrict,

    check (total >= 0),
    check (descuento_total >= 0),
    check (envio_costo >= 0),
    check (pago_monto is null or pago_monto >= 0)
);

create index idx_venta_empresa on venta (empresa_id);
create index idx_venta_cliente on venta (empresa_id, cliente_id);

create table venta_detalle
(
    venta_detalle_id bigserial primary key,
    empresa_id       bigint         not null references empresa (empresa_id) on delete cascade,
    venta_id         bigint         not null,
    producto_id      bigint         not null,

    cantidad         numeric(12, 3) not null,
    precio_unit      numeric(12, 2) not null,
    descuento        numeric(12, 2) not null default 0,
    subtotal         numeric(12, 2) not null,

    unique (empresa_id, venta_detalle_id),

    foreign key (empresa_id, venta_id) references venta (empresa_id, venta_id) on delete cascade,
    foreign key (empresa_id, producto_id) references producto (empresa_id, producto_id),

    check (cantidad > 0),
    check (precio_unit >= 0),
    check (descuento >= 0),
    check (subtotal >= 0)
);

create index idx_venta_detalle_venta on venta_detalle (empresa_id, venta_id);

create table notificacion
(
    notificacion_id bigserial primary key,
    empresa_id      bigint      not null references empresa (empresa_id) on delete cascade,

    actor_type      text        not null,
    usuario_id      bigint references usuario (usuario_id) on delete cascade,
    cliente_id      bigint references cliente (cliente_id) on delete cascade,

    canal           text        not null,
    titulo          text        not null,
    cuerpo          text        not null,
    creado_en       timestamptz not null default now(),
    leido_en        timestamptz,

    unique (empresa_id, notificacion_id),

    check (
        (actor_type = 'user' and usuario_id is not null and cliente_id is null)
            or
        (actor_type = 'client' and cliente_id is not null and usuario_id is null)
        )
);

create index idx_notificacion_empresa on notificacion (empresa_id);

create table token_blocklist
(
    jti        text primary key,
    usuario_id bigint      references usuario (usuario_id) on delete set null,
    revoked_at timestamptz not null default now()
);

create index idx_token_blocklist_usuario on token_blocklist (usuario_id);

create table proveedor
(
    proveedor_id bigserial primary key,
    empresa_id   bigint not null references empresa (empresa_id) on delete cascade,

    nombre       text not null,
    nit          text,
    telefono     text,
    direccion    text,
    email        text,

    activo       boolean not null default true,
    creado_en    timestamptz not null default now(),

    unique (empresa_id, proveedor_id),
    unique (empresa_id, nombre)
);

create index idx_proveedor_empresa on proveedor (empresa_id);
create index idx_proveedor_nombre on proveedor (empresa_id, nombre);

create table compra
(
    compra_id    bigserial primary key,
    empresa_id   bigint not null references empresa (empresa_id) on delete cascade,
    proveedor_id bigint not null,

    fecha_hora   timestamptz not null default now(),
    total        numeric(12, 2) not null default 0,
    estado       text not null default 'CREADA',
    observacion  text,

    recibido_por_usuario_id bigint references usuario (usuario_id) on delete set null,
    recibido_en timestamptz,

    unique (empresa_id, compra_id),
    foreign key (empresa_id, proveedor_id) references proveedor (empresa_id, proveedor_id),

    check (total >= 0),
    check (estado in ('CREADA','RECIBIDA','ANULADA'))
);

create index idx_compra_empresa on compra (empresa_id);
create index idx_compra_proveedor on compra (empresa_id, proveedor_id);
create index idx_compra_estado on compra (empresa_id, estado);

create table compra_detalle
(
    compra_detalle_id bigserial primary key,
    empresa_id  bigint not null references empresa (empresa_id) on delete cascade,
    compra_id   bigint not null,
    producto_id bigint not null,

    cantidad    numeric(12, 3) not null,
    costo_unit  numeric(12, 2) not null default 0,
    subtotal    numeric(12, 2) not null default 0,

    unique (empresa_id, compra_detalle_id),

    foreign key (empresa_id, compra_id) references compra (empresa_id, compra_id) on delete cascade,
    foreign key (empresa_id, producto_id) references producto (empresa_id, producto_id),

    check (cantidad > 0),
    check (costo_unit >= 0),
    check (subtotal >= 0)
);

create index idx_compra_detalle_compra on compra_detalle (empresa_id, compra_id);
