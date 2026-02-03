from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import os


def create_access_token_and_expiry(data: dict) -> tuple[str, int]:
    """Create a JWT access token.
    """

    try:
        SECRET_KEY = os.environ["JWT_SECRET_KEY"]
        ALGORITHM = os.environ["JWT_ALGORITHM"]
        JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 30))

        if not SECRET_KEY:
            raise RuntimeError("JWT_SECRET_KEY not set")

        utc_now = datetime.now(timezone.utc)
        expires_in = JWT_EXPIRATION_MINUTES * 60
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        to_encode = data.copy()
        to_encode.update({
            "sub": str(data.get("user_id")),
            "iat": utc_now,
            "exp": expire
        })

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, expires_in

    except JWTError as e:
        raise ValueError("Failed to create JWT token") from e