from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Text, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import UserDefinedType

from core.db import Base
from core.embeddings import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL


class VectorType(UserDefinedType):
    cache_ok = True

    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    def get_col_spec(self, **_: object) -> str:
        return f"vector({self.dimensions})"


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    embedding_record: Mapped["Embedding | None"] = relationship(
        back_populates="chunk",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Embedding(Base):
    __tablename__ = "embeddings"

    chunk_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        ForeignKey("chunks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    embedding: Mapped[object] = mapped_column(VectorType(EMBEDDING_DIMENSIONS), nullable=False)
    model: Mapped[str] = mapped_column(
        Text,
        server_default=text(f"'{EMBEDDING_MODEL}'"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    chunk: Mapped[Chunk] = relationship(back_populates="embedding_record")
