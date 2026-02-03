from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    class Config:
        orm_mode = True

class TokenData(BaseModel):
    user_name: Optional[str] = None
    class Config:
        orm_mode = True