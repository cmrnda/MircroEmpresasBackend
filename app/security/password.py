from passlib.hash import bcrypt

def hash_password(raw_password: str) -> str:
    return bcrypt.hash(raw_password)

def verify_password(raw_password: str, password_hash: str) -> bool:
    return bcrypt.verify(raw_password, password_hash)
