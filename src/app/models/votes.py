from sqlalchemy import (
    Column,
    ForeignKey,
    Integer
)
from sqlalchemy.dialects.postgresql import UUID
from src.app.db.connection import Base

class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)