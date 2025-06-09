from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """令牌模式"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """令牌数据模式"""
    username: Optional[str] = None
