import logging
from fastapi import APIRouter, HTTPException, Depends, logger, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
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

        Args:
        user: User creation data (username, email, password)
        db: Database session
        
        Returns:
            Created user object
            
        Raises:
            HTTPException 409: If email or username already exists
            HTTPException 422: If validation fails
            HTTPException 500: If database error occurs
    """
    logger.info(f"Attempting to create a new user with username: {user.username} and email: {user.email}")
    try:
        # Check if email exists
        existing_email = db.query(models.User).filter(models.User.email == user.email).first()

        if existing_email:
            logger.warning(f"Email already exists: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {user.email} already exists"
            )
        
        # Check if username exists
        existing_username = db.query(models.User).filter(models.User.username == user.username).first()

        if existing_username:
            logger.warning(f"Username already exists: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {user.username} already exists"
            )
        
        # Validate password 
        if (len(user.password) < 8):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Password must be at least 8 characters long"
            )
        
        # Create user
        data = user.model_dump()
        data["hashed_password"] = utils.hash_password(data.pop("password"))

        new_user = models.User(**data)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"Successfully created user with id: {new_user.id}")
        return new_user
    
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or username already exists"
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating user: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user"
        )
    

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