from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routers import auth, conversations

app = FastAPI()
app.include_router(auth.router)
app.include_router(conversations.router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def test_fastapi():
    return {"message":"測試成功"}