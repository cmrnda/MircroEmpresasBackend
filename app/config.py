import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL",
                                        "postgresql+psycopg://postgres:postgres@localhost:5432/sinpape1")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "86400"))
