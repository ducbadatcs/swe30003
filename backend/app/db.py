from __future__ import annotations

from pathlib import Path
from typing import Generator

from sqlmodel import Session, create_engine


DB_PATH = Path(__file__).with_name("restaurant_api.sqlite3")
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
)

def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session
        

