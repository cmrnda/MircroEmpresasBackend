import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "sinpapel")
    DB_USER = os.getenv("DB_USER", "sinpapel")
    DB_PASS = os.getenv("DB_PASS", "sinpapel")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
