import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import sys
from datetime import datetime
from passlib.context import CryptContext
from random import randrange

# FastAPI imports
from fastapi import FastAPI, Depends, HTTPException, Response, status
from fastapi.params import Body

# Import SQLAlchemy & Pydantic
from app.db.connection import engine
from sqlalchemy import text
from sqlalchemy.orm import Session
from . import models

# Env variables
from app.config import get_config
config = get_config()

from app.db import get_db_session
                           
# Automatically create the database tables if they do not exist
models.Base.metadata.create_all(bind=engine)


# Import routers
from .routers import post, user, sqlalchemy, auth, vote

# Logging configuration
LOG_LEVEL = config.log_level
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

# Add router objects
app.include_router(post.router)
app.include_router(user.router)
app.include_router(sqlalchemy.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/db-test")
def db_test(db: Session = Depends(get_db_session)):
    """Test database connection and return a success message if connected.
    """
    result = db.execute(text("SELECT 1")).fetchone()
    return {"message": "Database connection successful", "data": result[0]}
            

@app.get("/")
def root():
    return {"message": "welcome to my api"}
