import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import sys
from datetime import datetime
from passlib.context import CryptContext
from random import randrange

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# FastAPI imports
from fastapi import FastAPI, Depends, HTTPException, Response, status
from fastapi.params import Body

# Import SQLAlchemy & Pydantic
from src.app.db.connection import engine
from sqlalchemy import text
from sqlalchemy.orm import Session
from . import models, schemas, utils

from src.app.db import get_db_session
                           
# Automatically create the database tables if they do not exist
models.Base.metadata.create_all(bind=engine)

# For generating random data in tests
from random import randrange
from typing import List, Optional

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = ("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True,  # IMPORTANT: overrides uvicorn defaults
)
logger = logging.getLogger(__name__)
logger.info("Logging is configured.")

# Initialize FastAPI app
app = FastAPI()

@app.get("/db-test")
def db_test(db: Session = Depends(get_db_session)):
    """Test database connection and return a success message if connected.
    """
    result = db.execute(text("SELECT 1")).fetchone()
    return {"message": "Database connection successful", "data": result[0]}
            
@app.get("/sqlalchemy")
def test_sqlalchemy_posts(db: Session = Depends(get_db_session)):
    """Test SQLAlchemy ORM by retrieving all posts.
    """
    result = db.query(models.Post).all()
    return {"data": result}

@app.get("/sqlalchemy-test")
def test_post_via_sqlalchemy(db: Session = Depends(get_db_session)):
    """Test SQLAlchemy ORM by creating and retrieving a Post.
    """
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

@app.get("/")
def root():
    return {"message": "welcome to my api"}

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
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

@app.get("/posts/latest")
def get_latest_post(db: Session = Depends(get_db_session)):
    """Get the most recently created post from the database."""
    post = db.query(models.Post).order_by(models.Post.created_at.desc()).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts found"
        )

    return post
    
@app.get("/posts", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db_session), limit: int = 100, skip: int = 0):
    """ Get all posts from the database."""
    posts = db.query(models.Post).offset(skip).limit(limit).all()  # ORM-based query to retrieve all posts.

    return posts

@app.get("/posts/{id}", response_model=schemas.PostResponse)
def get_post(id: int, db: Session = Depends(get_db_session)):
    """Get a specific post by ID from the database."""
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")

    return post

@app.put("/posts/{id}", response_model=schemas.PostResponse)
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

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
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

@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db_session)):
    """Create a new user in the database.
    """
    data = user.model_dump()
    data["hashed_password"] = utils.hash_password(data.pop("password"))

    new_user = models.User(**data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user