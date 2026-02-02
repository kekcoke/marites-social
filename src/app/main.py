import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import sys
from datetime import datetime
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
from . import models, schemas

from src.app.db.session import get_db_session
from pydantic import BaseModel
# from sqlalchemy.orm import Session

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

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: schemas.CreatePost, db: Session = Depends(get_db_session)):
    """Create a new post in the database.
    """
    new_post = models.Post(
        **post.model_dump()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {"data": new_post}

@app.get("/posts/latest")
def get_latest_post(db: Session = Depends(get_db_session)):
    """Get the most recently created post from the database."""
    post = db.query(models.Post).order_by(models.Post.created_at.desc()).first()

    return {"data": post}
    
@app.get("/posts")
def get_posts(db: Session = Depends(get_db_session)):
    """ Get all posts from the database."""
    posts = db.query(models.Post).all()  # ORM-based query to retrieve all posts.

    return {"data": posts}

@app.get("/posts/{id}")
def get_post(id: int):
    """Get a specific post by ID from the database."""
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")

    return {"data": post}

@app.put("/posts/{id}")
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

    return {"data": existing_post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db_session)):
    """Delete a specific post by ID from the database."""
    post_query = db.query(models.Post).filter(models.Post.id == id)

    if post_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
