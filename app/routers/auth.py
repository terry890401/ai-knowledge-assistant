from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserRegister, UserResponse, TokenResponse, UserLogin
from app.models import User
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(prefix="/auth", tags=["認證"])
pwd_context = CryptContext(schemes=["bcrypt"]) # 使用 bcrypt 密碼加密演算法

# 產生 JWT token
def create_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# 註冊
@router.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=409,detail="此 email 已經被註冊")
    
    # 加密密碼
    hashed_pw = pwd_context.hash(user.password)

    new_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# 登入
@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="帳號或密碼錯誤")
    
    if not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    
    token = create_token(db_user.id)
    return {"access_token": token}