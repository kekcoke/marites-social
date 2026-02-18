from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import UUID


class CommentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    content: str = Field(..., min_length=1)
    commentable_type: str = Field(..., max_length=50, pattern="^(post|event)$")
    commentable_id: UUID
    parent_comment_id: Optional[UUID] = None


class CommentCreate(CommentBase):
    attachments: Optional[Dict[str, Any]] = None


class CommentUpdate(BaseModel):
    content: str
    attachments: Optional[Dict[str, Any]] = None


class CommentResponse(CommentBase):
    id: UUID
    user_id: UUID
    is_deleted: bool
    is_edited: bool
    attachments: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime