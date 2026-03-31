from fastapi import FastAPI, Request
from app.database import engine
from app.models import Base
from app.routers import auth, conversations,documents
import logging
import time

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response

app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(documents.router)

Base.metadata.create_all(bind=engine)