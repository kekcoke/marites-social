import os
import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
from typing import Optional
from models.post import Post

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

def get_db_connection():
    """Establish a connection to the database using environment variables.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT"),
            connect_timeout=os.getenv("CONNECT_TIMEOUT"),
            sslmode=os.getenv("SSL_MODE")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail="Database connection error")

@app.get("/db-test")
def db_test():
    """Test database connection and return a success message if connected.
    """
    conn = get_db_connection()
    if isinstance(conn, HTTPException):
        raise conn
    cursor = conn.cursor()
    cursor.execute("SELECT 1;")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result and result[0] == 1:
        return {"message": "Database connection successful!"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Database test query failed")

posts: list[Post] = []

@app.get("/")
def root():
    return {"message": "welcome to my api"}

@app.post("/createposts", status_code=status.HTTP_201_CREATED)
def create_posts(new_post: Post):
    post_dict = new_post.dict()
    post_dict['id'] = range(1, 1000000)  # Simulating ID assignment
    posts.append(post_dict)
    return {"data": post_dict}

@app.get("/posts/latest")
def get_latest_post():
    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts available"
        )
    latest_post = posts[-1]
    return {"latest_post": latest_post}
    

@app.get("/posts")
def get_posts():
    if not posts or len(posts) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts available"
        )
    return {"data": posts}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found"
        )
    return {"post_detail": post}

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )
    post_dict = post.dict()
    post_dict['id'] = id
    posts[index] = post_dict
    return {"data": post_dict}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )
    posts.pop(index)

    # Do not include any content in the response body when using a 204 status code, as this might cause errors related to the declared Content-Length.
    return Response(status_code=status.HTTP_204_NO_CONTENT)

def find_post(id: int):
    for post in posts:
        if post["id"] == id:
            return post
    return None

def find_index_post(id: int):
    for index, post in enumerate(posts):
        if post["id"] == id.str():
            return index
    return None