from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(raw: str) -> str:
    return generate_password_hash(str(raw))


def verify_password(raw: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, str(raw))
