from tests.pdf_utils import build_pdf

from services.loaders import load_pdf_text, load_txt_text


def test_txt_loader_reads_uploaded_text() -> None:
    assert load_txt_text(b"hello\nworld") == "hello\nworld"


def test_pdf_loader_extracts_non_empty_text() -> None:
    text = load_pdf_text(build_pdf(["Hello from PDF loader"]))

    assert "Hello from PDF loader" in text
