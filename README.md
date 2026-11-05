# RAG Chatbot — Production-Ready Application

A secure, multi-user **Retrieval-Augmented Generation (RAG) chatbot** that lets each user upload PDF documents and ask AI-powered questions about them using Google Gemini.

Transformed from a single-file Streamlit prototype into a full production architecture.

## Architecture

```
┌─────────────────────────────────────────┐
│             CLIENT LAYER                │
│  React SPA  ←→  Android WebView (APK)  │
└────────────────────┬────────────────────┘
                     │ HTTPS
┌────────────────────▼────────────────────┐
│         FastAPI Backend (Python)        │
│  ┌────────┐ ┌──────────┐ ┌──────────┐  │
│  │  Auth  │ │Documents │ │   Chat   │  │
│  └───┬────┘ └────┬─────┘ └────┬─────┘  │
│      └───────────┼────────────┘        │
│            Services Layer              │
│      ┌────────────┴──────────┐         │
│  ┌───▼───────┐    ┌──────────▼──────┐  │
│  │  SQLite/  │    │   ChromaDB      │  │
│  │ Postgres  │    │ (Vector Store)  │  │
│  └───────────┘    └────────┬────────┘  │
│                            │           │
│                   ┌────────▼────────┐  │
│                   │  Gemini API     │  │
│                   │  LLM + Embed    │  │
│                   └─────────────────┘  │
└─────────────────────────────────────────┘
```

## Quick Start (Docker)

```bash
# 1. Copy and configure environment
cp backend/.env.example backend/.env
# Edit backend/.env — add GOOGLE_API_KEY and SECRET_KEY

# 2. Generate a strong SECRET_KEY:
python -c "import secrets; print(secrets.token_hex(64))"

# 3. Start everything
docker-compose up --build

# API:  http://localhost:8000
# Docs: http://localhost:8000/docs  (only when DEBUG=true)
```

## Manual Setup

### Backend

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env — fill GOOGLE_API_KEY and SECRET_KEY

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | No | Create account |
| POST | `/api/v1/auth/login` | No | Login, get JWT tokens |
| POST | `/api/v1/auth/logout` | Yes | Logout |
| POST | `/api/v1/auth/refresh` | No | Refresh access token |
| GET | `/api/v1/users/me` | Yes | Get own profile |
| POST | `/api/v1/documents/upload` | Yes | Upload & process PDF |
| GET | `/api/v1/documents/` | Yes | List own documents |
| DELETE | `/api/v1/documents/{id}` | Yes | Delete own document |
| POST | `/api/v1/chat/` | Yes | RAG chat query |
| GET | `/api/v1/chat/conversations` | Yes | List conversations |
| GET | `/api/v1/chat/conversations/{id}` | Yes | Get conversation + messages |
| DELETE | `/api/v1/chat/conversations/{id}` | Yes | Delete conversation |
| GET | `/health` | No | Health check |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing secret (64+ chars) |
| `GOOGLE_API_KEY` | Google AI Studio API key |
| `DATABASE_URL` | SQLAlchemy DB URL (SQLite or PostgreSQL) |
| `GEMINI_LLM_MODEL` | Chat model (`gemini-2.0-flash`) |
| `GEMINI_EMBEDDING_MODEL` | Embedding model (`models/text-embedding-004`) |
| `MAX_UPLOAD_SIZE_MB` | Max file size (default: 20) |
| `ALLOWED_ORIGINS` | CORS origins (comma-separated) |
| `DEBUG` | Show API docs — ALWAYS `false` in production |

## Running Tests

```bash
cd backend
pytest tests/ -v --tb=short
```

## Security Features

- ✅ bcrypt password hashing (passlib)
- ✅ JWT access tokens (15 min) + refresh tokens (7 days)
- ✅ Per-user vector isolation — `user_id` filter on every ChromaDB query
- ✅ UUID-based file storage — no path traversal possible
- ✅ File type + MIME type + size validation
- ✅ Ownership checks on all document/conversation endpoints
- ✅ Rate limiting (60 req/min per IP via slowapi)
- ✅ CORS locked to configured origins
- ✅ No secrets in code — all via `.env`
- ✅ Global error handler — no internal details leaked
- ✅ Non-root Docker user
- ✅ API docs hidden in production (`DEBUG=false`)

## Project Structure

```
RagPDF1/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app + CORS + rate limiting
│   │   ├── config/           # Pydantic settings (reads .env)
│   │   ├── api/v1/           # REST endpoints
│   │   ├── core/             # JWT + bcrypt security
│   │   ├── database/         # SQLAlchemy engine + session
│   │   ├── models/           # ORM models (User, Document, Conversation)
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── repositories/     # DB access layer (no raw SQL)
│   │   ├── services/         # Business logic layer
│   │   └── rag/              # RAG pipeline (preserved + secured)
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # React + Vite SPA
├── mobile/android/           # Play Store roadmap
├── data/uploads/             # User-uploaded PDFs
├── vector_db/chroma/         # ChromaDB vector storage
├── scripts/                  # Init scripts
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Android / Play Store

See [mobile/android/README.md](mobile/android/README.md) for the complete 20-phase roadmap.

## License

MIT
