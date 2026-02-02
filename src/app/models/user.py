from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    func,
    text,
    Uuid
)
from src.app.db.connection import Base

class User(Base):
    """SQLAlchemy model for users table"""
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, autoincrement=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, server_default="true", nullable=False)    
    created_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"), #auto-update timestamp on modification
        nullable=False,
    ),
    last_login = Column(
        DateTime(timezone=True),
        nullable=True,
    ),
    last_activity = Column(
        DateTime(timezone=True),
        nullable=True,
    ),
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self):
        return f"<Users(id={self.id}, username='{self.username}', email='{self.email}')>"