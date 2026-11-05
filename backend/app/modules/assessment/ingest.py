"""Safe ingestion of an uploaded IR plan: validate the file, extract its text, keep nothing.

Threats this module defends against, and how:

* Wrong or disguised file types: the extension must be allowed AND the content must
  match it (magic bytes), so ``malware.exe`` renamed to ``plan.pdf`` is rejected.
* Oversized uploads: the request body is read with a hard byte limit, never fully
  trusted from Content-Length.
* Zip bombs in DOCX: the total uncompressed size and the entry count are checked
  before anything is decompressed.
* XML attacks in DOCX (billion laughs, external entities): XML is parsed with defusedxml.
* Huge PDFs: the page count is capped before extraction.
* Persistence of sensitive data: files are processed in memory only. Nothing is
  written to disk and nothing from the document is logged.
"""

from __future__ import annotations

import io
import logging
import zipfile
from dataclasses import dataclass
from enum import Enum

from defusedxml import ElementTree as SafeET
from pypdf import PdfReader
from pypdf.errors import PdfReadError

log = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 5 * 1024 * 1024            # 5 MB is plenty for a text IR plan
MAX_PDF_PAGES = 150
MAX_DOCX_UNCOMPRESSED_BYTES = 30 * 1024 * 1024
MAX_DOCX_ENTRIES = 2000
MAX_TEXT_CHARS = 400_000                     # about 100k tokens: keeps LLM cost bounded
MIN_TEXT_CHARS = 200                         # less than this is not a plan we can assess

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class DocumentKind(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"


EXTENSIONS = {".pdf": DocumentKind.PDF, ".docx": DocumentKind.DOCX, ".md": DocumentKind.MARKDOWN,
              ".markdown": DocumentKind.MARKDOWN, ".txt": DocumentKind.MARKDOWN}


class DocumentError(ValueError):
    """The upload was rejected. The message is safe to show to the user."""


class DocumentTooLargeError(DocumentError):
    """The upload, or its uncompressed content, exceeds a size limit."""


@dataclass(frozen=True)
class ExtractedDocument:
    kind: DocumentKind
    text: str
    pages: int | None
    truncated: bool


def detect_kind(filename: str, data: bytes) -> DocumentKind:
    name = (filename or "").lower()
    ext = name[name.rfind("."):] if "." in name else ""
    kind = EXTENSIONS.get(ext)
    if kind is None:
        raise DocumentError("Unsupported file type. Upload a PDF, DOCX or Markdown file.")
    if kind is DocumentKind.PDF and not data.startswith(b"%PDF-"):
        raise DocumentError("The file content is not a PDF.")
    if kind is DocumentKind.DOCX and not data.startswith(b"PK\x03\x04"):
        raise DocumentError("The file content is not a DOCX document.")
    if kind is DocumentKind.MARKDOWN and b"\x00" in data:
        raise DocumentError("The file content is not text.")
    return kind


def _normalize(text: str) -> str:
    lines = [" ".join(line.split()) for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    out: list[str] = []
    for line in lines:
        if line or (out and out[-1]):  # collapse runs of blank lines
            out.append(line)
    return "\n".join(out).strip()


def _extract_pdf(data: bytes) -> tuple[str, int]:
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise DocumentError("Encrypted PDFs are not supported. Remove the password and try again.")
        pages = len(reader.pages)
        if pages > MAX_PDF_PAGES:
            raise DocumentTooLargeError(f"The PDF has more than {MAX_PDF_PAGES} pages.")
        text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    except DocumentError:
        raise
    except (PdfReadError, ValueError, KeyError, TypeError) as exc:
        log.info("PDF rejected: %s", type(exc).__name__)  # exception type only, never content
        raise DocumentError("The PDF could not be read.") from exc
    return text, pages


def _extract_docx(data: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            infos = zf.infolist()
            if len(infos) > MAX_DOCX_ENTRIES:
                raise DocumentTooLargeError("The DOCX file has too many parts.")
            if sum(i.file_size for i in infos) > MAX_DOCX_UNCOMPRESSED_BYTES:
                raise DocumentTooLargeError("The DOCX file is too large when uncompressed.")
            try:
                xml = zf.read("word/document.xml")
            except KeyError as exc:
                raise DocumentError("The file is not a Word document.") from exc
        root = SafeET.fromstring(xml)
    except DocumentError:
        raise
    except (zipfile.BadZipFile, SafeET.ParseError, ValueError) as exc:
        log.info("DOCX rejected: %s", type(exc).__name__)
        raise DocumentError("The DOCX file could not be read.") from exc
    except Exception as exc:  # defusedxml raises its own types for entity/DTD attacks
        log.info("DOCX rejected: %s", type(exc).__name__)
        raise DocumentError("The DOCX file could not be read.") from exc

    paragraphs: list[str] = []
    for p in root.iter(f"{W_NS}p"):
        parts = []
        for node in p.iter():
            if node.tag == f"{W_NS}t" and node.text:
                parts.append(node.text)
            elif node.tag == f"{W_NS}tab":
                parts.append(" ")
            elif node.tag in (f"{W_NS}br", f"{W_NS}cr"):
                parts.append("\n")
        paragraphs.append("".join(parts))
    return "\n".join(paragraphs)


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-16"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise DocumentError("The text file must be UTF-8 encoded.")


def extract_document(filename: str, data: bytes) -> ExtractedDocument:
    if not data:
        raise DocumentError("The file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise DocumentTooLargeError(f"The file is larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.")

    kind = detect_kind(filename, data)
    pages: int | None = None
    if kind is DocumentKind.PDF:
        raw, pages = _extract_pdf(data)
    elif kind is DocumentKind.DOCX:
        raw = _extract_docx(data)
    else:
        raw = _decode_text(data)

    text = _normalize(raw)
    if len(text) < MIN_TEXT_CHARS:
        raise DocumentError(
            "Almost no text could be extracted. If this is a scanned PDF, export it with selectable text."
        )
    truncated = len(text) > MAX_TEXT_CHARS
    return ExtractedDocument(kind=kind, text=text[:MAX_TEXT_CHARS], pages=pages, truncated=truncated)
