from .connection import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

def get_db_session():
    """
    FastAPI dependency that provides a SQLAlchemy session.
    It automatically handles commits, rollbacks, and closing.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback() # Rollback on any database-specific error
        logger.error(f"Database error: {type(exc).__name__}", exc_info=True)
        raise
    except Exception as exc:
        db.rollback()  # Rollback on any other exceptions
        logger.error(f"Unexpected error: {type(exc).__name__}", exc_info=True)
        raise
    finally:
        db.close()