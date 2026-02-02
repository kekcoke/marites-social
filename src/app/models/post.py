from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Float,
    Integer,
    Text,
    func,
    text
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    published = Column(Boolean, server_default="true", nullable=False)    
    author = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    rating = Column(Float, nullable=True)
    likes = Column(Integer, server_default="0", nullable=False)
    comments = Column(Text, nullable=True)
