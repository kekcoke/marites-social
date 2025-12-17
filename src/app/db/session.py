from contextlib import contextmanager
from .connection import get_db_connection, DatabaseConnectionError
import logging

logger = logging.getLogger(__name__)

@contextmanager
def get_db_session():
    """Context manager to get a database session.
    Ensures that the connection is properly closed after use.
    """
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except DatabaseConnectionError as exc:
        logger.error(
            "Database connection failed",
            extra={
                "exception_type": type(exc).__name__,
                # include only safe metadata
            },
            exc_info=True,
        )
        raise

    except Exception as exc:
        if conn:
            try:
                logger.warning(
                    "Exception during DB transaction, attempting rollback",
                    extra={
                        "exception_type": type(exc).__name__,
                    },
                )
                conn.rollback()
            except Exception as rollback_exc:
                logger.critical(
                    "Database rollback failed",
                    extra={
                        "original_exception": type(exc).__name__,
                        "rollback_exception": type(rollback_exc).__name__,
                    },
                    exc_info=True,
                )

        logger.error(
            "Unhandled exception during database session",
            extra={
                "exception_type": type(exc).__name__,
            },
            exc_info=True,
        )
        raise

    finally:
        if conn:
            try:
                conn.close()
                logger.debug("Database connection closed")
            except Exception:
                logger.error(
                    "Failed to close database connection",
                    exc_info=True,
                )