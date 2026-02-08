import logging
from fastapi import APIRouter, HTTPException, Depends, logger, status
from sqlalchemy.orm import Session
from app import models, schemas, utils
from app.db.session import get_db_session

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)
logger = logging.getLogger(__name__)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db_session)):
    """Create a new user in the database.
    """
    logger.info(f"Creating a new user with username: {user.username} and email: {user.email}")
    data = user.model_dump()
    data["hashed_password"] = utils.hash_password(data.pop("password"))

    new_user = models.User(**data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"Created new user with id: {new_user.id}")
    return new_user

@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db_session)):
    """Retrieve a user by their ID.
    """
    logger.info(f"Retrieving user with ID: {user_id}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user