from typing import Annotated
from pydantic import BaseModel, Field
class Vote(BaseModel):
    post_id: int
    dir: Annotated[int, Field(le=1)]