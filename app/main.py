from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routers import auth, conversations,documents

app = FastAPI()
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(documents.router)

Base.metadata.create_all(bind=engine)