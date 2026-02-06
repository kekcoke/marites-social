from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from uuid import UUID
from .. import schemas
from .. import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=config.config.oauth_token_url)

def create_access_token_and_expiry(data: dict) -> tuple[str, int]:
    """Create a JWT access token.
    """

    try:
        SECRET_KEY = config.config.jwt_secret_key
        ALGORITHM = config.config.jwt_algorithm
        JWT_EXPIRATION_MINUTES = int(config.config.jwt_expires_minutes)

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
    
def verify_access_token(token: str, credentials_exception) -> UUID:
    """Verify a JWT access token."""
    try:
        SECRET_KEY = config.config.jwt_secret_key
        ALGORITHM = config.config.jwt_algorithm

        if not SECRET_KEY:
            raise RuntimeError("JWT_SECRET_KEY not set")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")

        if user_id is None:
            raise credentials_exception
        
        try:
            user_id = UUID(user_id)
        except (ValueError, TypeError) as e:
            raise credentials_exception
        
        return user_id

    except JWTError as e:
        raise credentials_exception from e

def get_current_user(token: str = Depends(oauth2_scheme)) -> UUID:
    """Get the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    return verify_access_token(token, credentials_exception)