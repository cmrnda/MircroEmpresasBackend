import os
from urllib.parse import quote_plus

def _db_uri() -> str:
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "microempresa")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS", "postgres")
    password_q = quote_plus(password)
    return f"postgresql+psycopg2://{user}:{password_q}@{host}:{port}/{name}"

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
        "connect_args": {
            "sslmode": os.getenv("DB_SSLMODE", "prefer")
        }
    }
