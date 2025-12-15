from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def login_user():
    return {"message": "Hello World"}