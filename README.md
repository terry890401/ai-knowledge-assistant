# AI Knowledge Assistant

一個結合 RAG 技術的 AI 知識庫助手，支援多輪對話、文件上傳和串流輸出。

**Live Demo**: [https://ai-knowledge-assistant-production-815b.up.railway.app](https://ai-knowledge-assistant-production-815b.up.railway.app)

## 功能

- **JWT 認證**：註冊、登入、token 驗證
- **多輪對話**：對話記錄存入 PostgreSQL，支援歷史查詢
- **Streaming 輸出**：逐字輸出，像 ChatGPT 一樣的使用體驗
- **RAG 知識庫**：上傳文件（txt/pdf），AI 根據文件內容回答問題
- **Hybrid Search**：結合向量搜尋和 BM25 關鍵字搜尋，提升召回準確率
- **文件來源顯示**：AI 回答時標示資料來源的文件名稱
- **Prompt 管理**：自訂 AI 角色和行為，存入資料庫動態切換
- **Sliding Window**：自動控制對話 token 用量，保留最近 10 則訊息
- **Rate Limiting**：每分鐘最多 20 次聊天請求，防止濫用
- **健康檢查**：`/health` API 確認服務和資料庫狀態
- **非同步文件處理**：上傳文件立刻回傳，背景自動處理 embedding
- **Prompt Injection 防禦**：輸入驗證過濾可疑指令，輸出驗證檢查 AI 回覆

## 系統架構

```
請求流程：
Client
  │
  ▼
FastAPI（CORS + Logging + Rate Limiting）
  │
  ├── PostgreSQL（用戶、對話、訊息、文件、Prompt）
  │
  ├── Chroma Cloud（文件向量 + Hybrid Search）
  │
  └── OpenAI GPT-4o-mini（對話生成 + Embedding）

監控：LangSmith（追蹤每次 LLM 呼叫）
部署：Docker + Railway
CI/CD：GitHub Actions（自動測試 + 自動部署）
```

## 技術架構

| 類別 | 技術 |
|------|------|
| 後端框架 | FastAPI |
| 資料庫 | PostgreSQL + SQLAlchemy ORM |
| 資料庫遷移 | Alembic |
| 向量資料庫 | Chroma Cloud |
| AI 模型 | OpenAI GPT-4o-mini |
| Embedding | OpenAI text-embedding-3-small |
| 搜尋 | Hybrid Search（向量 + BM25） |
| 認證 | JWT (python-jose) |
| 密碼加密 | bcrypt (passlib) |
| Rate Limiting | slowapi |
| 監控 | LangSmith |
| 日誌 | Python logging + Middleware |
| 測試 | pytest + FastAPI TestClient |
| 部署 | Docker + Railway |
| CI/CD | GitHub Actions |

## 專案結構

```
ai-knowledge-assistant/
├── app/
│   ├── main.py          # FastAPI 入口、CORS、Logging、Rate Limiting
│   ├── database.py      # 資料庫連線設定
│   ├── models.py        # SQLAlchemy 資料表
│   ├── schemas.py       # Pydantic 資料格式
│   ├── dependencies.py  # JWT 驗證
│   ├── vector_store.py  # Chroma 向量資料庫操作、Hybrid Search
│   ├── static/
│   │   └── index.html   # 前端 Demo 頁面
│   └── routers/
│       ├── auth.py          # 認證 API
│       ├── conversations.py # 對話 API + 聊天 + Streaming + RAG
│       ├── documents.py     # 文件 API
│       └── prompts.py       # Prompt 管理 API
├── alembic/             # 資料庫遷移檔案
├── tests/               # pytest 測試
│   ├── test_auth.py
│   ├── test_conversations.py
│   └── test_documents.py
├── .github/workflows/   # CI/CD
│   └── ci.yml
├── Dockerfile
├── .env.example
└── requirements.txt
```

## 安裝步驟

### 1. 建立虛擬環境

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. 安裝套件

```bash
pip install -r requirements.txt
```

### 3. 設定環境變數

複製 `.env.example` 為 `.env` 並填入實際的值：

```bash
cp .env.example .env
```

### 4. 建立資料庫

用 pgAdmin 建立 `ai_assistant` 資料庫，或用 psql：

```sql
CREATE DATABASE ai_assistant;
```

### 5. 執行資料庫遷移

```bash
alembic upgrade head
```

### 6. 啟動伺服器

```bash
uvicorn app.main:app --reload
```

## 使用方式

### Demo 前端

打開瀏覽器：
```
http://localhost:8000
```

### API 文件（Swagger UI）

```
http://localhost:8000/docs
```

### 健康檢查

```
http://localhost:8000/health
```

## API 路由

### 認證
| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | `/auth/register` | 註冊 |
| POST | `/auth/login` | 登入，回傳 JWT token |
| GET | `/auth/me` | 取得目前用戶 |

### 對話
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/conversations/` | 取得所有對話 |
| POST | `/conversations/` | 新增對話 |
| GET | `/conversations/{id}` | 取得單一對話（含訊息） |
| DELETE | `/conversations/{id}` | 刪除對話 |
| POST | `/conversations/{id}/chat` | 聊天 |
| POST | `/conversations/{id}/chat/stream` | 串流聊天（Rate Limited） |

### 文件
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/documents/` | 取得文件列表 |
| POST | `/documents/` | 上傳文件（txt/pdf） |
| DELETE | `/documents/{id}` | 刪除文件 |

### Prompt 管理
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/prompts/` | 取得所有 Prompt |
| POST | `/prompts/` | 新增 Prompt |
| DELETE | `/prompts/{id}` | 刪除 Prompt |

## 測試

```bash
pytest tests/ -v
```

## Docker

```bash
# 建立 image
docker build -t ai-knowledge-assistant .

# 執行容器
docker run -p 8000:8000 --env-file .env ai-knowledge-assistant
```
