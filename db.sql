create table empresa (
                         empresa_id bigserial primary key,
                         nombre text not null,
                         nit text,
                         estado text not null default 'ACTIVA',
                         creado_en timestamptz not null default now()
);

create table empresa_config (
                                empresa_id bigint primary key references empresa(empresa_id) on delete cascade,
                                moneda text not null default 'BOB',
                                tasa_impuesto numeric(6,3) not null default 0,
                                logo_url text,
                                actualizado_en timestamptz not null default now()
);

create table plan (
                      plan_id bigserial primary key,
                      nombre text not null,
                      precio numeric(12,2) not null default 0,
                      periodo_cobro text not null
);

create table suscripcion (
                             suscripcion_id bigserial primary key,
                             empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                             plan_id bigint not null references plan(plan_id),
                             estado text not null,
                             inicio date not null,
                             fin date,
                             renovacion date,
                             unique (empresa_id, suscripcion_id)
);

create table suscripcion_pago (
                                  pago_suscripcion_id bigserial primary key,
                                  empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                                  suscripcion_id bigint not null,
                                  monto numeric(12,2) not null,
                                  moneda text not null default 'BOB',
                                  metodo text not null,
                                  referencia_qr text,
                                  estado text not null,
                                  pagado_en timestamptz,
                                  unique (empresa_id, pago_suscripcion_id),
                                  foreign key (empresa_id, suscripcion_id)
                                      references suscripcion(empresa_id, suscripcion_id)
                                      on delete cascade
);

create table usuario (
                         usuario_id bigserial primary key,
                         email text not null unique,
                         password_hash text not null,
                         activo boolean not null default true,
                         creado_en timestamptz not null default now(),
                         ultimo_login timestamptz
);

create table usuario_admin_plataforma (
                                          usuario_id bigint primary key references usuario(usuario_id) on delete cascade
);

create table empresa_usuario (
                                 empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                                 usuario_id bigint not null references usuario(usuario_id) on delete cascade,
                                 activo boolean not null default true,
                                 creado_en timestamptz not null default now(),
                                 primary key (empresa_id, usuario_id)
);

create table usuario_admin_empresa (
                                       empresa_id bigint not null,
                                       usuario_id bigint not null,
                                       primary key (empresa_id, usuario_id),
                                       foreign key (empresa_id, usuario_id)
                                           references empresa_usuario(empresa_id, usuario_id)
                                           on delete cascade
);

create table usuario_vendedor (
                                  empresa_id bigint not null,
                                  usuario_id bigint not null,
                                  primary key (empresa_id, usuario_id),
                                  foreign key (empresa_id, usuario_id)
                                      references empresa_usuario(empresa_id, usuario_id)
                                      on delete cascade
);

create table usuario_encargado_inventario (
                                              empresa_id bigint not null,
                                              usuario_id bigint not null,
                                              primary key (empresa_id, usuario_id),
                                              foreign key (empresa_id, usuario_id)
                                                  references empresa_usuario(empresa_id, usuario_id)
                                                  on delete cascade
);

create table categoria (
                           categoria_id bigserial primary key,
                           empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                           nombre text not null,
                           activo boolean not null default true,
                           unique (empresa_id, nombre),
                           unique (empresa_id, categoria_id)
);

create table producto (
                          producto_id bigserial primary key,
                          empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                          categoria_id bigint not null,
                          codigo text not null,
                          descripcion text not null,
                          precio numeric(12,2) not null default 0,
                          stock_min integer not null default 0,
                          activo boolean not null default true,
                          unique (empresa_id, codigo),
                          unique (empresa_id, producto_id),
                          foreign key (empresa_id, categoria_id)
                              references categoria(empresa_id, categoria_id)
);

create table existencia_producto (
                                     empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                                     producto_id bigint not null,
                                     cantidad_actual numeric(12,3) not null default 0,
                                     primary key (empresa_id, producto_id),
                                     foreign key (empresa_id, producto_id)
                                         references producto(empresa_id, producto_id)
                                         on delete cascade
);

create table movimiento_inventario (
                                       movimiento_id bigserial primary key,
                                       empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                                       producto_id bigint not null,
                                       tipo text not null,
                                       cantidad numeric(12,3) not null,
                                       ref_tabla text,
                                       ref_id bigint,
                                       fecha timestamptz not null default now(),
                                       realizado_por_usuario_id bigint not null references usuario(usuario_id),
                                       unique (empresa_id, movimiento_id),
                                       foreign key (empresa_id, producto_id)
                                           references producto(empresa_id, producto_id)
);

create table proveedor (
                           proveedor_id bigserial primary key,
                           empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                           nombre text not null,
                           telefono text,
                           email text,
                           datos_pago text,
                           activo boolean not null default true,
                           unique (empresa_id, proveedor_id)
);

create table compra (
                        compra_id bigserial primary key,
                        empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                        proveedor_id bigint not null,
                        fecha timestamptz not null default now(),
                        total numeric(12,2) not null default 0,
                        estado text not null,
                        unique (empresa_id, compra_id),
                        foreign key (empresa_id, proveedor_id)
                            references proveedor(empresa_id, proveedor_id)
);

create table compra_detalle (
                                compra_detalle_id bigserial primary key,
                                empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                                compra_id bigint not null,
                                producto_id bigint not null,
                                cantidad numeric(12,3) not null,
                                costo_unit numeric(12,2) not null,
                                subtotal numeric(12,2) not null,
                                unique (empresa_id, compra_detalle_id),
                                foreign key (empresa_id, compra_id)
                                    references compra(empresa_id, compra_id)
                                    on delete cascade,
                                foreign key (empresa_id, producto_id)
                                    references producto(empresa_id, producto_id)
);

create table cliente (
                         cliente_id bigserial primary key,
                         empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                         email text not null unique,
                         password_hash text not null,
                         nombre_razon text not null,
                         nit_ci text,
                         telefono text,
                         activo boolean not null default true,
                         creado_en timestamptz not null default now(),
                         ultimo_login timestamptz,
                         unique (empresa_id, cliente_id)
);

create table venta (
                       venta_id bigserial primary key,
                       empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                       cliente_id bigint not null,
                       fecha_hora timestamptz not null default now(),
                       total numeric(12,2) not null default 0,
                       descuento_total numeric(12,2) not null default 0,
                       estado text not null,
                       unique (empresa_id, venta_id),
                       foreign key (empresa_id, cliente_id)
                           references cliente(empresa_id, cliente_id)
);

create table venta_detalle (
                               venta_detalle_id bigserial primary key,
                               empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                               venta_id bigint not null,
                               producto_id bigint not null,
                               cantidad numeric(12,3) not null,
                               precio_unit numeric(12,2) not null,
                               descuento numeric(12,2) not null default 0,
                               subtotal numeric(12,2) not null,
                               unique (empresa_id, venta_detalle_id),
                               foreign key (empresa_id, venta_id)
                                   references venta(empresa_id, venta_id)
                                   on delete cascade,
                               foreign key (empresa_id, producto_id)
                                   references producto(empresa_id, producto_id)
);

create table venta_pago (
                            venta_pago_id bigserial primary key,
                            empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                            venta_id bigint not null,
                            metodo text not null,
                            monto numeric(12,2) not null,
                            referencia_qr text,
                            estado text not null,
                            pagado_en timestamptz,
                            unique (empresa_id, venta_pago_id),
                            foreign key (empresa_id, venta_id)
                                references venta(empresa_id, venta_id)
                                on delete cascade
);

create table venta_comprobante (
                                   comprobante_id bigserial primary key,
                                   empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                                   venta_id bigint not null,
                                   tipo text not null,
                                   numero text,
                                   url_pdf text,
                                   emitido_en timestamptz not null default now(),
                                   unique (empresa_id, comprobante_id),
                                   foreign key (empresa_id, venta_id)
                                       references venta(empresa_id, venta_id)
                                       on delete cascade
);

create table venta_envio (
                             envio_id bigserial primary key,
                             empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                             venta_id bigint not null,
                             departamento text not null,
                             ciudad text not null,
                             zona_barrio text,
                             direccion_linea text not null,
                             referencia text,
                             telefono_receptor text,
                             costo_envio numeric(12,2) not null default 0,
                             estado_envio text not null,
                             tracking text,
                             fecha_despacho timestamptz,
                             fecha_entrega timestamptz,
                             unique (empresa_id, venta_id),
                             unique (empresa_id, envio_id),
                             foreign key (empresa_id, venta_id)
                                 references venta(empresa_id, venta_id)
                                 on delete cascade
);

create table notificacion (
                              notificacion_id bigserial primary key,
                              empresa_id bigint not null references empresa(empresa_id) on delete cascade,
                              usuario_id bigint not null references usuario(usuario_id) on delete cascade,
                              canal text not null,
                              titulo text not null,
                              cuerpo text not null,
                              creado_en timestamptz not null default now(),
                              leido_en timestamptz,
                              unique (empresa_id, notificacion_id)
);

create index idx_empresa_nombre on empresa(nombre);
create index idx_plan_nombre on plan(nombre);

create index idx_suscripcion_empresa on suscripcion(empresa_id);
create index idx_suscripcion_pago_empresa on suscripcion_pago(empresa_id);

create index idx_empresa_usuario_usuario on empresa_usuario(usuario_id);

create index idx_categoria_empresa on categoria(empresa_id);
create index idx_producto_empresa on producto(empresa_id);

create index idx_cliente_empresa on cliente(empresa_id);
create index idx_venta_empresa on venta(empresa_id);
create index idx_compra_empresa on compra(empresa_id);

create table if not exists token_blocklist (
                                               jti text primary key,
                                               usuario_id bigint,
                                               revoked_at timestamptz not null default now()
    );

create index if not exists idx_token_blocklist_usuario_id
    on token_blocklist (usuario_id);
