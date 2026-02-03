import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends, logger, Response, status
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..db.session import get_db_session

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)
logger = logging.getLogger(__name__)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.CreatePost, db: Session = Depends(get_db_session)):
    """Create a new post in the database.
    """
    logger.info(f"Creating a new post with title: {post.title}")
    new_post = models.Post(
        **post.model_dump()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    logger.info(f"Created new post with id: {new_post.id}")
    return new_post

@router.get("/latest", response_model=schemas.PostResponse)
def get_latest_post(db: Session = Depends(get_db_session)):
    """Get the most recently created post from the database."""
    post = db.query(models.Post).order_by(models.Post.created_at.desc()).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts found"
        )

    return post
    
@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db_session), limit: int = 100, skip: int = 0):
    """ Get all posts from the database."""
    posts = db.query(models.Post).offset(skip).limit(limit).all()  # ORM-based query to retrieve all posts.

    return posts

@router.get("/{id}", response_model=schemas.PostResponse)
def get_post(id: int, db: Session = Depends(get_db_session)):
    """Get a specific post by ID from the database."""
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")

    return post

@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.UpdatePost, db: Session = Depends(get_db_session)):
    """Update a specific post by ID in the database."""
    post_query = db.query(models.Post).filter(models.Post.id == id)
    existing_post = post_query.first()

    if existing_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )

    post_query.update(post.model_dump(exclude_unset=True))

    for key, value in post.model_dump().items():
        setattr(existing_post, key, value)
    existing_post.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(existing_post)
    logger.info(f"Updated post with id: {id}")

    return existing_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db_session)):
    """Delete a specific post by ID from the database."""
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )

    post_query.delete(synchronize_session=False)
    db.commit()
    logger.info(f"Deleted post with id: {id}")

    return Response(status_code=status.HTTP_204_NO_CONTENT)