from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from core.db import get_db_session
from core.models import Chunk, Document
from services.chunking import chunk_text
from services.loaders import InvalidPdfFileError, InvalidTextFileError, load_pdf_text, load_txt_text

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024
MAX_EXTRACTED_CHARS = 5_000_000
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}

router = APIRouter()


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    filename: str
    chunks_created: int


class ChunkResponse(BaseModel):
    id: UUID
    chunk_index: int
    content: str
    start_char: int
    end_char: int
    token_count: int


class DocumentResponse(BaseModel):
    document_id: UUID
    filename: str
    file_size: int | None
    chunks: list[ChunkResponse]


def _extract_text(file_bytes: bytes, filename: str) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Use .pdf or .txt",
        )
    if extension == ".txt":
        try:
            return load_txt_text(file_bytes)
        except InvalidTextFileError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if not file_bytes.startswith(b"%PDF"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PDF file")
    try:
        return load_pdf_text(file_bytes)
    except InvalidPdfFileError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
) -> DocumentUploadResponse:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Use .pdf or .txt",
        )

    file_bytes = await file.read(MAX_FILE_SIZE_BYTES + 1)
    await file.close()

    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail="File too large")

    text = _extract_text(file_bytes, filename)
    if len(text) > MAX_EXTRACTED_CHARS:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail="Extracted text too large")
    chunk_specs = chunk_text(text)

    document = Document(filename=filename, file_size=len(file_bytes))
    document.chunks = [
        Chunk(
            chunk_index=chunk_spec["chunk_index"],
            content=chunk_spec["content"],
            start_char=chunk_spec["start_char"],
            end_char=chunk_spec["end_char"],
            token_count=chunk_spec["token_count"],
        )
        for chunk_spec in chunk_specs
    ]

    db.add(document)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return DocumentUploadResponse(
        document_id=document.id,
        filename=document.filename,
        chunks_created=len(document.chunks),
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: UUID, db: Session = Depends(get_db_session)) -> DocumentResponse:
    statement = (
        select(Document)
        .options(selectinload(Document.chunks))
        .where(Document.id == document_id)
    )
    document = db.execute(statement).scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return DocumentResponse(
        document_id=document.id,
        filename=document.filename,
        file_size=document.file_size,
        chunks=[
            ChunkResponse(
                id=chunk.id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                token_count=chunk.token_count,
            )
            for chunk in document.chunks
        ],
    )
