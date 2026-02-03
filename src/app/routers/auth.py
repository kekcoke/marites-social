from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from .. import models, schemas, utils, db
import logging

router = APIRouter(
    tags=["Authentication"]
)

logger = logging.getLogger(__name__)
@router.post("/login", response_model=schemas.Token)
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

    access_token = utils.create_access_token(data={"user_id": str(user.id)})
    logger.info(f"User {user_credentials.username} logged in successfully.")

    return {"access_token": access_token, "token_type": "bearer"}