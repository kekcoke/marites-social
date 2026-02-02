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
from src.app.models.post import Base, PostModel
from src.app.schemas.post import PostSchema

from src.app.db.session import get_db_session
from pydantic import BaseModel
# from sqlalchemy.orm import Session

# Automatically create the database tables if they do not exist
Base.metadata.create_all(bind=engine)

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
    result = db.query(PostModel).all()
    return {"data": result}

@app.get("/sqlalchemy-test")
def test_post_via_sqlalchemy(db: Session = Depends(get_db_session)):
    """Test SQLAlchemy ORM by creating and retrieving a Post.
    """
    new_post = PostModel(
        title="Test Post",
        content="This is a test post created via SQLAlchemy ORM.",
        author="Tester",
        created_at=datetime.utcnow()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    retrieved_post = db.query(PostModel).filter(PostModel.id == new_post.id).first()
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
def create_posts(post: PostSchema, db: Session = Depends(get_db_session)):
    """Create a new post in the database.
    """
    # **post.model_dump() next
    new_post = PostModel(
        **post.model_dump()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}

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
def get_posts(db: Session = Depends(get_db_session)):
    posts = db.query(Post).all()  # ORM-based query to retrieve all posts.
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
def update_post(id: int, post: PostSchema):
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

# @app.get("/users/", response_model=List[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users

# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db_session)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user

# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db_session)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db=db, user=user)

# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db_session)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)

# @app.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items