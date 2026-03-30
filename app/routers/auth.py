from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserRegister, UserResponse, TokenResponse
from app.models import User
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["認證"])
pwd_context = CryptContext(schemes=["bcrypt"]) # 使用 bcrypt 密碼加密演算法

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
