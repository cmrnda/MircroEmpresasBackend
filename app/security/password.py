from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(raw_password: str) -> str:
    return generate_password_hash(raw_password, method="pbkdf2:sha256", salt_length=16)

def verify_password(raw_password: str, hashed_password: str) -> bool:
    try:
        return check_password_hash(hashed_password or "", raw_password or "")
    except Exception:
        return False
