from uuid import UUID
from pydantic import BaseModel, Field
from pydantic.types import conint
from datetime import datetime
from typing import Optional

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)