from pydantic import BaseModel, EmailStr
from datetime import datetime


# 註冊 pydantic
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

# 登入 pydantic
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 對話 pydantic
class ConversationCreate(BaseModel):
    title: str | None = "新對話"

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: list[MessageResponse]

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    content: str