import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import get_config

logger = logging.getLogger(__name__)

# Define a standard naming convention
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Central base for declarative models
Base = declarative_base()

class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass

def get_db_connection():
    """Establish a connection to the database using environment variables.
    """
    try:
        config = get_config()
        conn = psycopg2.connect(
            host=config.db_host,
            database=config.db_name,
            user=config.db_username,
            password=config.db_password,
            port=config.db_port,
            connect_timeout=config.db_connect_timeout,
            sslmode=config.db_ssl_mode,
            cursor_factory=RealDictCursor
        )
        logger.info("Database connection established.")
        return conn
    except Exception as e:
        logger.error("Error connecting to the database", exc_info=True)
        raise DatabaseConnectionError("Failed to connect to the database") from e

# Build SQLAlchemy engine and session
DATABASE_URL = get_config().get_db_database_url()

connect_args={
    "connect_timeout": 10,
    "application_name": "marites-social-app"
}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False,
    expire_on_commit=False,
    bind=engine)

def get_db_session() -> Session:
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()