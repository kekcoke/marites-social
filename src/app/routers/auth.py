from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from .. import models, schemas, utils, db
from ..auth.oauth2 import create_access_token_and_expiry
import logging

router = APIRouter(
    tags=["Authentication"]
)

logger = logging.getLogger(__name__)

@router.post("/login", response_model=schemas.Token, status_code=status.HTTP_200_OK)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(db.get_db_session)):
    """Authenticate user and return a JWT token upon successful login.
    """
    logger.info(f"Attempting to log in user: {user_credentials.username}")
    user = db.query(models.User).filter(models.User.username == user_credentials.username).first()

    if not user:
        logger.warning(f"Login failed: User {user_credentials.username} not found.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )

    if not utils.verify_password(user_credentials.password, user.hashed_password):
        logger.warning(f"Login failed: Incorrect password for user {user_credentials.username}.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )

    access_token, expires_in = create_access_token_and_expiry(
        data={"user_id": str(user.id)}
    )

    logger.info(f"User {user_credentials.username} logged in successfully.")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }

@router.post("/logout")
def logout(response: Response):
    """Logout user by clearing the authentication token.
    """
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax",
    )
    logger.info("Logout requested")
    return {"message": "Successfully logged out"}