from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

DATABASE_URL = "sqlite:///" + str(Path(__file__).resolve().parent.parent / "app.db")

def get_engine():
    return create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def init_db() -> None:
    engine = get_engine()
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    engine = get_engine()
    return Session(engine)
