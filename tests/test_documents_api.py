from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
import api.routes.documents as documents_route
from core.db import Base, get_db_session
from tests.pdf_utils import build_pdf


def _make_client() -> TestClient:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    def override_db_session():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = override_db_session
    return TestClient(app)


def test_upload_txt_returns_document_and_chunk_metadata() -> None:
    client = _make_client()
    text = " ".join(["alpha"] * 2000).encode("utf-8")

    response = client.post("/documents", files={"file": ("sample.txt", text, "text/plain")})

    assert response.status_code == 200
    payload = response.json()
    assert UUID(payload["document_id"])
    assert payload["filename"] == "sample.txt"
    assert payload["chunks_created"] > 0


def test_upload_pdf_creates_expected_number_of_chunks() -> None:
    client = _make_client()
    pages = [" ".join([f"page{page_index}"] * 400) for page_index in range(10)]
    pdf_bytes = build_pdf(pages)

    response = client.post("/documents", files={"file": ("sample.pdf", pdf_bytes, "application/pdf")})

    assert response.status_code == 200
    assert response.json()["chunks_created"] >= 15


def test_upload_rejects_unsupported_file_type() -> None:
    client = _make_client()

    response = client.post("/documents", files={"file": ("sample.md", b"# nope", "text/markdown")})

    assert response.status_code == 400
    assert response.json() == {"detail": "Unsupported file type. Use .pdf or .txt"}


def test_upload_rejects_empty_file() -> None:
    client = _make_client()

    response = client.post("/documents", files={"file": ("empty.txt", b"", "text/plain")})

    assert response.status_code == 400
    assert response.json() == {"detail": "File is empty"}


def test_upload_rejects_file_too_large(monkeypatch) -> None:
    client = _make_client()
    monkeypatch.setattr(documents_route, "MAX_FILE_SIZE_BYTES", 8)

    response = client.post("/documents", files={"file": ("big.txt", b"012345678", "text/plain")})

    assert response.status_code == 413


def test_upload_rejects_invalid_pdf_content() -> None:
    client = _make_client()

    response = client.post("/documents", files={"file": ("bad.pdf", b"not a pdf", "application/pdf")})

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid PDF file"}


def test_upload_rejects_non_utf8_text() -> None:
    client = _make_client()

    response = client.post("/documents", files={"file": ("bad.txt", b"\xff\xfe\xff", "text/plain")})

    assert response.status_code == 400
    assert response.json() == {"detail": "Text file must be UTF-8"}


def test_upload_rejects_extracted_text_that_is_too_large(monkeypatch) -> None:
    client = _make_client()
    monkeypatch.setattr(documents_route, "MAX_EXTRACTED_CHARS", 10)

    response = client.post("/documents", files={"file": ("big.txt", b"01234567890", "text/plain")})

    assert response.status_code == 413
    assert response.json() == {"detail": "Extracted text too large"}


def test_get_document_returns_metadata_and_chunks() -> None:
    client = _make_client()
    text = " ".join(["alpha"] * 2000).encode("utf-8")
    create_response = client.post("/documents", files={"file": ("sample.txt", text, "text/plain")})

    response = client.get(f"/documents/{create_response.json()['document_id']}")

    assert response.status_code == 200
    payload = response.json()
    assert UUID(payload["document_id"])
    assert payload["filename"] == "sample.txt"
    assert payload["chunks"]
    assert "content" in payload["chunks"][0]
    assert "token_count" in payload["chunks"][0]


def test_get_document_returns_404_for_missing_id() -> None:
    client = _make_client()

    response = client.get(f"/documents/{uuid4()}")

    assert response.status_code == 404


def test_zero_chunk_document_returns_empty_array() -> None:
    client = _make_client()
    blank_pdf = build_pdf([""])

    create_response = client.post("/documents", files={"file": ("blank.pdf", blank_pdf, "application/pdf")})

    assert create_response.status_code == 200
    assert create_response.json()["chunks_created"] == 0

    fetch_response = client.get(f"/documents/{create_response.json()['document_id']}")

    assert fetch_response.status_code == 200
    assert fetch_response.json()["chunks"] == []
