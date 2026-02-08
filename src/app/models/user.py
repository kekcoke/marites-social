import uuid
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    func
)
from sqlalchemy.dialects.postgresql import UUID
from app.db.connection import Base
from sqlalchemy.orm import relationship

class User(Base):
    """SQLAlchemy model for users table"""
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        autoincrement=False, 
        default=uuid.uuid4
    )
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(), #auto-update timestamp on modification
        nullable=False
    )
    last_login = Column(
        DateTime(timezone=True),
        nullable=True
    )
    last_activity = Column(
        DateTime(timezone=True),
        nullable=True
    )
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    posts = relationship(
        "Post",
        back_populates="user",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Users(id={self.id}, username='{self.username}', email='{self.email}')>"