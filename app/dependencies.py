from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from dotenv import load_dotenv
import os
from app.models import User
from jose import jwt, JWTError

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

bearer_scheme = HTTPBearer()

# 驗證 token 並回傳目前登入的用戶，需要登入的 API 都用 Depends(get_current_user)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    credentials_exception = HTTPException(status_code=401, detail="token 無效或已過期")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user