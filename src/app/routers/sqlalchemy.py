import logging
import datetime
from fastapi import APIRouter, HTTPException, Depends, logger, status
from sqlalchemy.orm import Session
from .. import models
from ..db.session import get_db_session

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/sqlalchemy")
def test_sqlalchemy_posts(db: Session = Depends(get_db_session)):
    """Test SQLAlchemy ORM by retrieving all posts.
    """
    logger.info("Testing SQLAlchemy ORM by retrieving all posts.")
    result = db.query(models.Post).all()
    return {"data": result}

@router.get("/sqlalchemy-test")
def test_post_via_sqlalchemy(db: Session = Depends(get_db_session)):
    """Test SQLAlchemy ORM by creating and retrieving a Post.
    """
    logger.info("Testing SQLAlchemy ORM by creating a new post.")
    new_post = models.Post(
        title="Test Post",
        content="This is a test post created via SQLAlchemy ORM.",
        author="Tester",
        created_at=datetime.utcnow()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    retrieved_post = db.query(models.Post).filter(models.Post.id == new_post.id).first()
    if retrieved_post:
        return {"message": "SQLAlchemy ORM test successful", "post": {
            "id": retrieved_post.id,
            "title": retrieved_post.title,
            "content": retrieved_post.content
        }}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SQLAlchemy ORM test failed"
        )