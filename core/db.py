from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import Settings, get_settings


class Base(DeclarativeBase):
    pass


def get_database_url(settings: Settings | None = None) -> str:
    config = settings or get_settings()
    return (
        f"postgresql+psycopg://{config.database_user}:{config.database_password}"
        f"@{config.database_host}:{config.database_port}/{config.database_name}"
    )


@lru_cache
def get_engine():
    return create_engine(get_database_url(), pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autocommit=False, autoflush=False, expire_on_commit=False)


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
