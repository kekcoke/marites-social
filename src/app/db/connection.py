import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

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
        logger.error(f"Error connecting to the database: {e}")
        raise DatabaseConnectionError("Failed to connect to the database.") from e