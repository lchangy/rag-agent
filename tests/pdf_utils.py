def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(pages: list[str]) -> bytes:
    if not pages:
        raise ValueError("at least one page is required")

    font_id = 3
    next_object_id = 4
    page_ids: list[int] = []
    content_ids: list[int] = []
    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        font_id: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }

    for page_text in pages:
        content_id = next_object_id
        page_id = next_object_id + 1
        next_object_id += 2

        content_lines = ["BT", "/F1 12 Tf", "72 720 Td"]
        lines = page_text.splitlines() or [page_text]
        for index, line in enumerate(lines):
            if index:
                content_lines.append("0 -18 Td")
            content_lines.append(f"({_escape_pdf_text(line)}) Tj")
        content_lines.append("ET")
        content_stream = "\n".join(content_lines).encode("latin-1") + b"\n"
        objects[content_id] = (
            f"<< /Length {len(content_stream)} >>\nstream\n".encode("latin-1")
            + content_stream
            + b"endstream"
        )
        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {content_id} 0 R "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> >>"
        ).encode("latin-1")
        content_ids.append(content_id)
        page_ids.append(page_id)

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[2] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("latin-1")

    object_ids = sorted(objects)
    output = bytearray(b"%PDF-1.4\n")
    offsets = {0: 0}

    for object_id in object_ids:
        offsets[object_id] = len(output)
        output.extend(f"{object_id} 0 obj\n".encode("latin-1"))
        output.extend(objects[object_id])
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {max(object_ids) + 1}\n".encode("latin-1"))
    output.extend(b"0000000000 65535 f \n")
    for object_id in range(1, max(object_ids) + 1):
        output.extend(f"{offsets[object_id]:010d} 00000 n \n".encode("latin-1"))
    output.extend(
        (
            f"trailer\n<< /Size {max(object_ids) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("latin-1")
    )
    return bytes(output)
