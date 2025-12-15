from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional
from models.post import Post

app = FastAPI()

@app.get("/")
def root():
    return {"message": "welcome to my api"}

@app.post("/createposts")
def create_posts(new_post: Post):
    print(new_post)
    print(new_post.dict())
    return {"data": new_post.dict()}

@app.get("/posts")
def get_posts():
    return {"data": "This is your posts"}

@app.get("/posts/{id}")
def get_post(id: str):
    return {"data": f"This is your post with id: {id}"}

@app.put("/posts/{id}")
def update_post(id: str, updated_post: Post = Body(...)):
    return {"data": f"Post with id: {id} has been updated"}

@app.delete("/posts/{id}")
def delete_post(id: str):
    return {"data": f"Post with id: {id} has been deleted"}