from fastapi import FastAPI, Body, HTTPException, Response, status
from pydantic import BaseModel
from typing import Optional
from models.post import Post

app = FastAPI()

posts = [{
    "id": "1",
    "title": "First Post",
    "content": "Content of the first post",
    "published": True,
    "author": "Alice"
},
{
    "id": "2",
    "title": "Second Post",
    "content": "Content of the second post",
    "published": False,
    "author": "Bob"
}]

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
    return {"data": "This is your latest post"}

@app.get("/posts")
def get_posts():
    return {"data": "This is your posts"}

@app.get("/posts/{id}")
def get_post(id: str, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found"
        )
    return {"post_detail": post}

@app.put("/posts/{id}")
def update_post(id: str, updated_post: Post = Body(...)):
    return {"data": f"Post with id: {id} has been updated"}

@app.delete("/posts/{id}")
def delete_post(id: str):
    return {"data": f"Post with id: {id} has been deleted"}

def find_post(id: str):
    for post in posts:
        if post["id"] == id:
            return post
    return None