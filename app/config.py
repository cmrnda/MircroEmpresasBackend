import os
from sqlalchemy.engine import URL

def _env_required(name: str) -> str:
    v = os.getenv(name)
    if v is None or str(v).strip() == "":
        raise RuntimeError(f"Falta la variable de entorno {name}. No voy a usar defaults.")
    return v

def _db_uri() -> str:
    host = _env_required("DB_HOST")
    port = int(os.getenv("DB_PORT", "5432"))
    sslmode = os.getenv("DB_SSLMODE")

    # Default inteligente:
    # - RDS => require
    # - local => prefer (para no romper si tu Postgres local no tiene SSL)
    if not sslmode:
        sslmode = "prefer" if host in ("localhost", "127.0.0.1") else "require"

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=_env_required("DB_USER"),
        password=_env_required("DB_PASS"),
        host=host,
        port=port,
        database=_env_required("DB_NAME"),
        query={
            "sslmode": sslmode,
            "connect_timeout": "5",
        },
    )
    return url.render_as_string(hide_password=False)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change_me")
    SQLALCHEMY_DATABASE_URI = _db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "change_me")

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 240,
        "pool_size": 5,
        "max_overflow": 10,
    }
