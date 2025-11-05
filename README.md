# Migraine RAG Assistant for Teens

This project provides a full-stack reference implementation of a migraine-focused virtual assistant designed for teenagers. It offers account registration, login, and a chat interface that retrieves migraine education snippets and forwards them to an LLM using a lightweight Retrieval-Augmented Generation (RAG) workflow.

## Project structure

```
.
├── backend/        # FastAPI application, database models, and RAG pipeline
└── frontend/       # Vite + React single-page application
```

## Backend

### Features

- **Authentication** – Register and sign in with email/password credentials. Passwords are hashed using bcrypt and tokens are issued as JWTs.
- **Chat endpoint** – Authenticated users can submit migraine care questions. The server retrieves relevant passages from curated content and forwards them to an LLM helper.
- **Knowledge base** – A starter dataset (`backend/data/migraine_articles.json`) supplies the domain context for RAG.

### Setup

```bash
# from the repository root
./scripts/setup_venv.sh
source .venv/bin/activate  # On Windows use `.venv\\Scripts\\activate`
uvicorn backend.app.main:app --reload
```

Environment variables:

- `JWT_SECRET` – secret key for signing JWT tokens (defaults to a development-safe string).
- `OPENAI_API_KEY` – optional OpenAI key to enable live LLM calls. Without it, the server returns a context summary and safety reminder.
- `LLM_MODEL` – optional model name when using OpenAI (defaults to `gpt-3.5-turbo`).
- `CORS_ORIGINS` – comma-separated list of allowed web origins (defaults to `http://localhost:5173`).

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The React SPA includes registration, login, and a chat page inspired by modern AI assistants. It automatically attaches JWT tokens to chat requests and displays the retrieved migraine passages next to the conversation.

## Development notes

- The RAG pipeline uses TF–IDF similarity (via scikit-learn) over the bundled migraine knowledge base. For production, replace this with a vector database and clinically validated content.
- The backend persists users and chat transcripts in a SQLite database (`backend/app.db`). Remove `app.db` to reset the environment.
- When running locally, start the backend on port 8000 and the frontend on port 5173. The Vite dev server proxies `/auth` and `/chat` requests to the FastAPI service.
