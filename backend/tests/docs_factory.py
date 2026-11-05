"""Build small PDF and DOCX files in memory for tests (no binary fixtures in the repo)."""

import io
import zipfile

PLAN_TEXT = (
    "Incident Response Plan. The Incident Commander is the CISO, who can declare an incident. "
    "Severity levels SEV1 to SEV4 are defined in Appendix B. Escalate SEV1 incidents to the CEO within 30 minutes. "
    "Preserve evidence: collect logs and disk images and record the chain of custody."
)


def make_pdf(text: str = PLAN_TEXT, pages: int = 1) -> bytes:
    """A valid PDF with one Helvetica text line per page."""
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    objects: list[bytes] = []
    page_ids = [4 + 2 * i for i in range(pages)]
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {pages} >>".encode())
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for pid in page_ids:
        stream = f"BT /F1 9 Tf 20 700 Td ({safe}) Tj ET".encode()
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 2000 792] /Contents {pid + 1} 0 R "
            f"/Resources << /Font << /F1 3 0 R >> >> >>".encode()
        )
        objects.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(out.tell())
        out.write(f"{i} 0 obj\n".encode() + body + b"\nendobj\n")
    xref = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for off in offsets:
        out.write(f"{off:010d} 00000 n \n".encode())
    out.write(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return out.getvalue()


def make_docx(text: str = PLAN_TEXT, document_xml: str | None = None, extra: dict[str, bytes] | None = None) -> bytes:
    paragraphs = "".join(f"<w:p><w:r><w:t>{line}</w:t></w:r></w:p>" for line in text.split(". "))
    xml = document_xml or (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{paragraphs}</w:body></w:document>"
    )
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        zf.writestr("word/document.xml", xml)
        for name, data in (extra or {}).items():
            zf.writestr(name, data)
    return out.getvalue()
