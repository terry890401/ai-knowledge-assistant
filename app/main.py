from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import engine
from app.models import Base
from app.routers import auth, conversations, documents, prompts
import logging
import time
import os

# LangSmith 追蹤設定
langsmith_key = os.getenv("LANGSMITH_API_KEY")
if langsmith_key:
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = langsmith_key
    os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "ai-knowledge-assistant")

app = FastAPI()

# CORS 設定，允許前端跨域呼叫
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting 設定，用 IP 限制呼叫頻率
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Logging 設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 記錄每個 request 的方法、路徑、狀態碼、耗時
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    return response

# 掛載路由
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(documents.router)
app.include_router(prompts.router)

# 靜態檔案（前端 Demo）
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 啟動時自動建立資料表
Base.metadata.create_all(bind=engine)

# 首頁
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("app/static/index.html", encoding="utf-8") as f:
        return f.read()

# 健康檢查，確認資料庫和 Chroma 連線狀態
@app.get("/health")
def health_check():
    health = {
        "status": "healthy",
        "database": "unknown",
        "chroma": "unknown"
    }

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health["database"] = "connected"
    except Exception:
        health["database"] = "disconnected"
        health["status"] = "unhealthy"

    try:
        from app.vector_store import collection
        collection.count()
        health["chroma"] = "connected"
    except Exception:
        health["chroma"] = "disconnected"
        health["status"] = "unhealthy"

    return health