from passlib.hash import bcrypt

def hash_password(raw: str):
    return bcrypt.hash(str(raw))

def verify_password(raw: str, password_hash: str):
    try:
        return bcrypt.verify(str(raw), str(password_hash))
    except Exception:
        return False
