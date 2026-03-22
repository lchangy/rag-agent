from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

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
def get_session_factory():
    return sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
