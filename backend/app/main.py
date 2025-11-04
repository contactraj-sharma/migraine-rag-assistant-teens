from __future__ import annotations

import os
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select

from . import auth
from .database import get_session, init_db
from .llm import get_llm_client
from .models import ChatMessage, User
from .rag import get_knowledge_base
from .schemas import ChatHistoryItem, ChatRequest, ChatResponse, Token, UserCreate, UserRead

app = FastAPI(title="Migraine RAG Assistant for Teens")

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    get_knowledge_base()


@app.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate):
    with get_session() as session:
        existing = session.exec(select(User).where(User.email == payload.email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=auth.get_password_hash(payload.password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        token = auth.create_access_token(str(user.id))
        return Token(access_token=token)


@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with get_session() as session:
        user = session.exec(select(User).where(User.email == form_data.username)).first()
        if not user or not auth.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = auth.create_access_token(str(user.id))
        return Token(access_token=token)


@app.get("/auth/me", response_model=UserRead)
def read_current_user(token: str = Depends(oauth2_scheme)):
    user = _get_user_from_token(token)
    return UserRead(id=user.id, email=user.email, full_name=user.full_name, created_at=user.created_at)


def _get_user_from_token(token: str) -> User:
    try:
        token_payload = auth.decode_access_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    with get_session() as session:
        user = session.get(User, int(token_payload.sub))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user


@app.post("/chat/query", response_model=ChatResponse)
def ask_question(request: ChatRequest, token: str = Depends(oauth2_scheme)):
    user = _get_user_from_token(token)

    kb = get_knowledge_base()
    results = kb.query(request.question)
    context_entries = [
        {"title": doc["title"], "content": doc["content"], "score": score}
        for doc, score in results
    ]
    context_chunks = [entry["content"] for entry in context_entries]

    llm_client = get_llm_client()
    answer = llm_client.generate(request.question, context_chunks)

    with get_session() as session:
        message = ChatMessage(user_id=user.id, question=request.question, answer=answer)
        session.add(message)
        session.commit()

    return ChatResponse(answer=answer, context=context_entries)


@app.get("/chat/history", response_model=List[ChatHistoryItem])
def get_history(token: str = Depends(oauth2_scheme)):
    user = _get_user_from_token(token)
    with get_session() as session:
        statement = select(ChatMessage).where(ChatMessage.user_id == user.id).order_by(ChatMessage.created_at.desc())
        records = session.exec(statement).all()
    return [
        ChatHistoryItem(id=item.id, question=item.question, answer=item.answer, created_at=item.created_at)
        for item in records
    ]
