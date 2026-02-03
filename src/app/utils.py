from passlib.context import CryptContext
import hashlib
pwd_context = CryptContext(schemes=["argon2",], deprecated="auto")

def hash_password(password: str) -> str:
    # Pre-hash the password using "argon2"
    digest = pwd_context.hash(password.encode("utf-8"))

    return digest

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Pre-hash the plain password using sha256
    is_valid = pwd_context.verify(plain_password.encode("utf-8"), hashed_password)

    return is_valid