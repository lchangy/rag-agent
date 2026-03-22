from io import BytesIO

import pdfplumber
from pdfplumber.utils.exceptions import PdfminerException


class InvalidTextFileError(ValueError):
    pass


class InvalidPdfFileError(ValueError):
    pass


def load_txt_text(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidTextFileError("Text file must be UTF-8") from exc


def load_pdf_text(file_bytes: bytes) -> str:
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except (PdfminerException, OSError, ValueError) as exc:
        raise InvalidPdfFileError("Invalid PDF file") from exc
