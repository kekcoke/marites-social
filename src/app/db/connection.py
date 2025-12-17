import logging
import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()
logger = logging.getLogger(__name__)

class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass

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
            sslmode=os.getenv("SSL_MODE"),
            cursor_factory=RealDictCursor
        )
        logger.info("Database connection established.")
        return conn
    except Exception as e:
        logger.error("Error connecting to the database", exc_info=True)
        raise DatabaseConnectionError("Failed to connect to the database") from e

# Build SQLAlchemy engine and session
DATABASE_URL = os.getenv("DATABASE_URL") 

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 10,
        "application_name": "marites-social-app",
        "check_same_thread": False
    },
)

Session_Local = sessionmaker(
    autocommit=False, 
    autoflush=False,
    expire_on_commit=False,
    bind=engine)

# Base class for declarative models
Base = declarative_base()

def get_db_session():
    """Provide a transactional scope around a series of operations."""
    db = Session_Local()
    try:
        yield db
    finally:
        db.close()