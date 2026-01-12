import os

class Config:
    @staticmethod
    def db_uri() -> str:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "x")
        user = os.getenv("DB_USER", "x")
        pwd = os.getenv("DB_PASS", "x")
        return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}"

    @staticmethod
    def jwt_secret() -> str:
        return os.getenv("JWT_SECRET", "change_me")
