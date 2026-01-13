import os
from urllib.parse import quote_plus

class Config:
    @staticmethod
    def db_uri() -> str:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "microempresa")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASS", "postgres")
        password_q = quote_plus(password)
        return f"postgresql+psycopg2://{user}:{password_q}@{host}:{port}/{name}"

    @staticmethod
    def jwt_secret() -> str:
        return os.getenv("JWT_SECRET", "change_me")

    @staticmethod
    def reset_token_minutes() -> int:
        v = os.getenv("RESET_TOKEN_MINUTES", "30")
        try:
            return int(v)
        except Exception:
            return 30
