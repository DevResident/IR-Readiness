import logging

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.assessment import ingest
from app.modules.assessment.ingest import (
    DocumentError,
    DocumentKind,
    DocumentTooLargeError,
    extract_document,
)
from tests.docs_factory import PLAN_TEXT, make_docx, make_pdf

client = TestClient(app)


def test_markdown_is_extracted_and_normalized():
    doc = extract_document("plan.md", ("# Plan\r\n\r\n\r\n" + PLAN_TEXT + "   \n").encode())
    assert doc.kind is DocumentKind.MARKDOWN
    assert doc.text.startswith("# Plan\n\nIncident Response Plan.")
    assert doc.pages is None and not doc.truncated


def test_utf8_bom_text_file():
    assert extract_document("plan.txt", ("﻿" + PLAN_TEXT).encode("utf-8")).text.startswith("Incident")


def test_pdf_text_and_page_count():
    doc = extract_document("plan.pdf", make_pdf(pages=2))
    assert doc.kind is DocumentKind.PDF
    assert doc.pages == 2
    assert "Incident Commander is the CISO" in doc.text


def test_docx_paragraphs_are_extracted():
    doc = extract_document("plan.docx", make_docx())
    assert doc.kind is DocumentKind.DOCX
    assert "Severity levels SEV1 to SEV4" in doc.text


@pytest.mark.parametrize("name", ["plan.exe", "plan", "plan.pdf.exe", "plan.doc"])
def test_unsupported_extensions(name):
    with pytest.raises(DocumentError, match="Unsupported file type"):
        extract_document(name, PLAN_TEXT.encode())


def test_renamed_file_is_rejected_by_content():
    with pytest.raises(DocumentError, match="not a PDF"):
        extract_document("plan.pdf", b"MZ\x90\x00" + PLAN_TEXT.encode())
    with pytest.raises(DocumentError, match="not a DOCX"):
        extract_document("plan.docx", make_pdf())
    with pytest.raises(DocumentError, match="not text"):
        extract_document("plan.md", b"MZ\x00\x00" + PLAN_TEXT.encode())


def test_zip_that_is_not_a_word_document():
    import io
    import zipfile

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("readme.txt", PLAN_TEXT)
    with pytest.raises(DocumentError, match="not a Word document"):
        extract_document("plan.docx", buf.getvalue())


def test_docx_entity_expansion_attack_is_rejected():
    billion_laughs = (
        '<?xml version="1.0"?><!DOCTYPE lolz [<!ENTITY lol "lol">'
        '<!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">]>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:p><w:r><w:t>&lol2;</w:t></w:r></w:p></w:body></w:document>"
    )
    with pytest.raises(DocumentError, match="could not be read"):
        extract_document("plan.docx", make_docx(document_xml=billion_laughs))


def test_docx_zip_bomb_is_rejected_before_decompression(monkeypatch):
    monkeypatch.setattr(ingest, "MAX_DOCX_UNCOMPRESSED_BYTES", 1_000_000)
    bomb = make_docx(extra={"word/media/padding.bin": b"\x00" * 2_000_000})
    with pytest.raises(DocumentTooLargeError, match="too large when uncompressed"):
        extract_document("plan.docx", bomb)


def test_size_limits(monkeypatch):
    monkeypatch.setattr(ingest, "MAX_UPLOAD_BYTES", 1000)
    with pytest.raises(DocumentTooLargeError):
        extract_document("plan.md", b"a" * 1001)
    monkeypatch.setattr(ingest, "MAX_UPLOAD_BYTES", 5_000_000)
    monkeypatch.setattr(ingest, "MAX_PDF_PAGES", 2)
    with pytest.raises(DocumentTooLargeError, match="more than 2 pages"):
        extract_document("plan.pdf", make_pdf(pages=3))


def test_empty_and_textless_files():
    with pytest.raises(DocumentError, match="empty"):
        extract_document("plan.md", b"")
    with pytest.raises(DocumentError, match="Almost no text"):
        extract_document("plan.pdf", make_pdf(text=" "))


def test_long_documents_are_truncated(monkeypatch):
    monkeypatch.setattr(ingest, "MAX_TEXT_CHARS", 250)
    doc = extract_document("plan.md", (PLAN_TEXT * 3).encode())
    assert doc.truncated and len(doc.text) == 250


def test_corrupt_pdf_gives_a_safe_message():
    with pytest.raises(DocumentError, match="could not be read"):
        extract_document("plan.pdf", b"%PDF-1.4\n" + b"garbage" * 100)


# ---------- API ----------

def test_upload_endpoint_summarizes_without_logging_content(caplog):
    caplog.set_level(logging.DEBUG)
    secret = "CANARY-7f3a SECRET VPN PASSWORD"
    body = (PLAN_TEXT + " " + secret).encode()
    res = client.post("/api/assessment/document", files={"file": ("plan.md", body, "text/markdown")})
    assert res.status_code == 200
    assert res.json()["kind"] == "markdown"
    assert res.json()["characters"] == len(body.decode())
    assert "CANARY-7f3a" not in caplog.text


def test_upload_endpoint_rejects_disguised_file():
    res = client.post("/api/assessment/document", files={"file": ("plan.pdf", b"MZ" + b"x" * 300, "application/pdf")})
    assert res.status_code == 422
    assert res.json()["detail"] == "The file content is not a PDF."


def test_upload_endpoint_rejects_oversized_file():
    big = b"a" * (ingest.MAX_UPLOAD_BYTES + 10)
    res = client.post("/api/assessment/document", files={"file": ("plan.md", big, "text/markdown")})
    assert res.status_code == 413


def test_checklist_endpoint():
    body = client.get("/api/assessment/checklist").json()
    assert len(body["controls"]) == 23


def test_upload_without_content_length_is_rejected():
    def chunks():
        yield b"--x\r\nContent-Disposition: form-data; name=\"file\"; filename=\"plan.md\"\r\n\r\n"
        yield PLAN_TEXT.encode() + b"\r\n--x--\r\n"

    res = client.post(
        "/api/assessment/document", content=chunks(), headers={"Content-Type": "multipart/form-data; boundary=x"}
    )
    assert res.status_code == 411


def test_fictional_example_plan_is_accepted():
    from app.catalogs.paths import EXAMPLES_DIR

    path = EXAMPLES_DIR / "ir-plan-fictional-meridian-logistics.md"
    doc = extract_document(path.name, path.read_bytes())
    assert "Incident Manager declares an incident" in doc.text
