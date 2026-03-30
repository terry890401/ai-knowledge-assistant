from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True # 讓 ORM 物件可以轉成 Pydantic

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"