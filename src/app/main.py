from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional
from models import Post

app = FastAPI()


@app.get("/")
def root():
    return {"message": "welcome to my api"}

@app.get("/posts")
def get_posts():
    return {"data": "This is your posts"}

@app.post("/createposts")
def create_posts(new_post: Post):
    print(new_post)
    print(new_post.dict())
    return {"data": new_post.dict()}