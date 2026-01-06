import os
import psycopg2
import logging
import sys
from datetime import datetime

from db.session import get_db_session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# FastAPI imports
from fastapi import FastAPI, Depends, HTTPException, Response, status
from fastapi.params import Body

# Import SQLAlchemy & Pydantic
from src.app.db.connection import engine, get_db_connection
from src.app.models import post
from src.app.models.post import Base

from src.app.db.session import get_db_session
# from pydantic import BaseModel
# from sqlalchemy.orm import Session

# Automatically create the database tables if they do not exist
Base.metadata.create_all(bind=engine)

# For generating random data in tests
from random import randrange
from typing import List


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
def db_test():
    """Test database connection and return a success message if connected.
    """
    with get_db_session() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            if result and result[0] == 1:
                return {"message": "Database connection successful"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database connection test failed"
                )

@app.get("/sqlalchemy-test")
def test_post_via_sqlalchemy(db: Session = Depends(get_db_session)):
    """Test SQLAlchemy ORM by creating and retrieving a Post.
    """
    new_post = models.Posts(
        title="Test Post",
        content="This is a test post created via SQLAlchemy ORM.",
        author="Tester",
        created_at=datetime.utcnow()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    retrieved_post = db.query(models.Posts).filter(models.Posts.id == new_post.id).first()
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

@app.post("/createposts", status_code=status.HTTP_201_CREATED)
def create_posts(new_post: Post):
    """Create a new post in the database.
    """
    with get_db_session() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *;",
            (new_post.title, new_post.content, new_post.published))
        post = cursor.fetchone()
        conn.commit()
        return {"data": dict(post)}


@app.get("/posts/latest")
def get_latest_post():
    """Get the most recently created post from the database."""
    with get_db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 1;")
        post = cursor.fetchone()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No posts available"
            )
        return {"latest_post": dict(post)}
    
@app.get("/posts")
def get_posts():
    """Get all posts from the database."""
    posts = []
    with get_db_session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM posts;")
            posts = cursor.fetchall()
            return {"data": posts}

@app.get("/posts/{id}")
def get_post(id: int):
    """Get a specific post by ID from the database."""
    with get_db_session() as conn:
            cursor = conn.cursor()
            # Be sure to include an extra comma in the tuple (i.e., (str(id),)) to prevent unexpected issues with parameter tuple assignment.
            cursor.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
            post = cursor.fetchone()
            
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Post with id: {id} was not found"
                )
            return {"data": post}

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    """Update a specific post by ID in the database."""
    with get_db_session() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *;",
            (post.title, post.content, post.published, id)
        )
        updated_post = cursor.fetchone()
        conn.commit()
        if not updated_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {id} does not exist"
            )
        return {"data": dict(updated_post)}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    """Delete a specific post by ID from the database."""
    with get_db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *;", (id,))
        deleted_post = cursor.fetchone()
        conn.commit()
        if not deleted_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {id} does not exist"
            )
    # Do not include any content in the response body when using a 204 status code, as this might cause errors related to the declared Content-Length.
    return Response(status_code=status.HTTP_204_NO_CONTENT)
