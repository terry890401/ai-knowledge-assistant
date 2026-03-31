# AI Knowledge Assistant

一個結合 RAG 技術的 AI 知識庫助手，支援多輪對話、文件上傳和串流輸出。

## 功能

- **JWT 認證**：註冊、登入、token 驗證
- **多輪對話**：對話記錄存入 PostgreSQL，支援歷史查詢
- **Streaming 輸出**：逐字輸出，像 ChatGPT 一樣的使用體驗
- **RAG 知識庫**：上傳文件（txt/pdf），AI 根據文件內容回答問題
- **向量搜尋**：使用 Chroma 向量資料庫 + OpenAI Embedding

## 技術架構

| 類別 | 技術 |
|------|------|
| 後端框架 | FastAPI |
| 資料庫 | PostgreSQL + SQLAlchemy ORM |
| 向量資料庫 | Chroma |
| AI 模型 | OpenAI GPT-4o-mini |
| Embedding | OpenAI text-embedding-3-small |
| 認證 | JWT (python-jose) |
| 密碼加密 | bcrypt (passlib) |

## 專案結構

```
ai-knowledge-assistant/
├── app/
│   ├── main.py          # FastAPI 入口
│   ├── database.py      # 資料庫連線設定
│   ├── models.py        # SQLAlchemy 資料表
│   ├── schemas.py       # Pydantic 資料格式
│   ├── dependencies.py  # JWT 驗證
│   ├── vector_store.py  # Chroma 向量資料庫操作
│   ├── static/
│   │   └── index.html   # 前端 Demo 頁面
│   └── routers/
│       ├── auth.py          # 認證 API
│       ├── conversations.py # 對話 API
│       └── documents.py     # 文件 API
├── .env
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

建立 `.env` 檔案：

```bash
DATABASE_URL=postgresql://postgres:你的密碼@localhost:5432/ai_assistant
SECRET_KEY=你的隨機字串
OPENAI_API_KEY=你的OpenAI金鑰
```

產生 SECRET_KEY：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. 建立資料庫

用 pgAdmin 建立 `ai_assistant` 資料庫，或用 psql：

```sql
CREATE DATABASE ai_assistant;
```

### 5. 啟動伺服器

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
| POST | `/conversations/{id}/chat/stream` | 串流聊天 |

### 文件
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/documents/` | 取得文件列表 |
| POST | `/documents/` | 上傳文件 |
| DELETE | `/documents/{id}` | 刪除文件 |
