from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class ChatRequest(BaseModel):
    question: str


class ContextSnippet(BaseModel):
    title: str
    content: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    context: list[ContextSnippet]


class ChatHistoryItem(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime


class AuthResponse(BaseModel):
    user: UserRead
    token: Token
