# Migraine RAG Assistant for Teens – Project Writeup

## Purpose and Audience
The Migraine RAG Assistant for Teens provides a supportive virtual companion that helps teenagers learn about migraine care. The product blends retrieval-augmented generation (RAG) with a friendly chat interface so that young users receive context-backed, empathetic guidance while being reminded to seek professional medical advice.

## High-Level Architecture
The platform is split into a FastAPI backend and a Vite + React single-page application. The backend supplies authentication, chat orchestration, and knowledge retrieval, while the frontend manages account workflows and presents the chat experience. This separation allows each side to evolve independently and simplifies local development using the existing scripts and npm tooling.

```
Browser SPA (React)  <----REST/JSON---->  FastAPI service  <---->  SQLite & TF–IDF knowledge base
```

## Backend Responsibilities
The FastAPI service exposes endpoints for registration, login, profile lookup, chat querying, and chat history retrieval. Startup hooks initialize the SQLite database and load the cached knowledge base. Authenticated chat requests retrieve the most relevant passages, send them to the LLM helper, persist the exchange, and return the generated answer alongside the supporting snippets.

Key modules include:

- `main.py` defines the FastAPI routes, OAuth2 bearer authentication, and lifecycle hooks used throughout the backend.
- `models.py` stores `User` and `ChatMessage` records with creation timestamps.
- `schemas.py` (not shown) governs request and response validation for auth and chat payloads.

## Retrieval-Augmented Generation Pipeline
The RAG workflow indexes a curated JSON knowledge base with `TfidfVectorizer`. Each query transforms the incoming question into vector space, ranks documents by cosine similarity, and returns the top matches alongside their scores. The design ensures teens always see the evidence backing each answer and can review the underlying articles.

## LLM Orchestration and Safety Backstop
The `LLMClient` wraps optional OpenAI access. When an API key is configured it calls `ChatCompletion.create` using a system prompt tailored for compassionate teen-focused guidance. If no key is present, it synthesizes a deterministic summary from the retrieved context and appends a reminder to consult healthcare professionals, guaranteeing the assistant remains helpful in offline demos.

## Data and Persistence
The project uses SQLModel on top of SQLite for durable storage. Passwords are hashed before insertion, tokens carry user identifiers, and every chat message is recorded with the user relationship. Clearing the SQLite database resets the environment without altering the source-controlled assets.

## Frontend Experience
React Router gates routes behind an authentication provider that stores JWTs in `localStorage`. The chat page renders a two-panel layout: a conversation stream with auto-scrolling bubbles and a sidebar that highlights the evidence snippets returned from the backend. The layout gracefully adapts to smaller screens by collapsing the sidebar while preserving the chat workflow.

## Core User Flows
1. **Registration** – Teens provide their name, email, and password. Successful sign-up schedules a redirect to the login screen with a friendly confirmation toast.
2. **Login** – Credentials are sent via form-encoded POST to retrieve a JWT, which then drives authenticated API calls.
3. **Chatting** – The user composes a migraine-related question, the frontend calls the `/chat/query` endpoint, displays the answer, and shows the supporting passages with relevance scores. Errors surface inline so users can retry without refreshing.

## Quality and Testing
Backend functionality is exercised through pytest suites that simulate the full auth and chat flow. The tests replace external dependencies (database, knowledge base, LLM) with in-memory doubles so the entire pipeline runs deterministically and verifies critical behaviors such as duplicate registration rejection.

## Deployment and Local Development
Developers can bootstrap the backend with the provided virtualenv script and run the FastAPI server locally. The frontend starts with `npm run dev` and proxies API requests to the backend, allowing the entire experience to run on standard development ports. Environment variables configure JWT secrets, optional OpenAI credentials, and CORS origins for custom setups.

## Future Enhancements
- Swap the TF–IDF retriever for a vector database that supports semantic search.
- Enrich the knowledge base with clinically reviewed teen-friendly migraine resources.
- Add guardian accounts or consent workflows tailored to teenage users.
- Introduce automated accessibility tests and UX research with the target age group.
