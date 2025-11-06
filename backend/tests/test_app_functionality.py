from contextlib import contextmanager
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, create_engine

sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.app import main, schemas  # noqa: E402


class DummyForm:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.scopes = []
        self.client_id = None
        self.client_secret = None


class DummyKnowledgeBase:
    def query(self, question: str, top_k: int = 3):
        documents = [
            {"title": "Hydration Tips", "content": "Drink plenty of water to stay hydrated."},
            {
                "title": "Identifying Triggers",
                "content": "Keep a diary to spot migraine triggers like stress or skipped meals.",
            },
        ]
        return [(doc, 0.9 - idx * 0.1) for idx, doc in enumerate(documents[:top_k])]


class DummyLLM:
    def generate(self, question: str, context_chunks: list[str]) -> str:
        joined_context = " ".join(context_chunks)
        return (
            f"Helpful guidance for '{question}': {joined_context} "
            "Always talk with a healthcare professional for personalized care."
        )


@pytest.fixture
def app_dependencies(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    @contextmanager
    def get_session_override():
        with Session(engine) as session:
            yield session

    def init_db_override():
        SQLModel.metadata.create_all(engine)

    def fake_hash(password: str) -> str:
        return f"hashed::{password}"

    def fake_verify(plain: str, hashed: str) -> bool:
        return hashed == fake_hash(plain)

    def fake_create_token(subject: str) -> str:
        return f"token::{subject}"

    def fake_decode_token(token: str) -> schemas.TokenPayload:
        if not token.startswith("token::"):
            raise ValueError("Invalid token")
        subject = token.split("::", 1)[1]
        return schemas.TokenPayload(sub=subject, exp=0)

    monkeypatch.setattr(main, "get_session", get_session_override)
    monkeypatch.setattr(main, "init_db", init_db_override)
    monkeypatch.setattr(main, "get_knowledge_base", lambda: DummyKnowledgeBase())
    monkeypatch.setattr(main, "get_llm_client", lambda: DummyLLM())
    monkeypatch.setattr(main.auth, "get_password_hash", fake_hash)
    monkeypatch.setattr(main.auth, "verify_password", fake_verify)
    monkeypatch.setattr(main.auth, "create_access_token", fake_create_token)
    monkeypatch.setattr(main.auth, "decode_access_token", fake_decode_token)

    yield


def _register_user(email: str = "teen@example.com", password: str = "StrongPass123"):
    payload = schemas.UserCreate(email=email, full_name="Test Teen", password=password)
    return main.register_user(payload)


def _login_user(email: str = "teen@example.com", password: str = "StrongPass123"):
    form = DummyForm(username=email, password=password)
    return main.login(form)


def test_full_auth_chat_flow(app_dependencies):
    registered_user = _register_user()
    assert registered_user.email == "teen@example.com"
    assert registered_user.full_name == "Test Teen"

    login_token = _login_user()
    assert login_token.access_token

    me = main.read_current_user(token=login_token.access_token)
    assert me.email == "teen@example.com"
    assert me.full_name == "Test Teen"

    chat_request = schemas.ChatRequest(question="What helps with migraine triggers?")
    chat_response = main.ask_question(chat_request, token=login_token.access_token)
    assert "Always talk with a healthcare professional" in chat_response.answer
    assert len(chat_response.context) == 2
    assert chat_response.context[0].title == "Hydration Tips"

    history = main.get_history(token=login_token.access_token)
    assert len(history) == 1
    assert history[0].question == chat_request.question
    assert history[0].answer == chat_response.answer


def test_duplicate_registration_rejected(app_dependencies):
    first_user = _register_user()
    assert first_user.email == "teen@example.com"

    with pytest.raises(HTTPException) as exc_info:
        _register_user()
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already registered"
