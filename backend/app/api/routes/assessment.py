from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.catalogs.checklists import get_checklist
from app.modules.assessment.ingest import (
    MAX_UPLOAD_BYTES,
    DocumentError,
    DocumentKind,
    DocumentTooLargeError,
    extract_document,
)

router = APIRouter(prefix="/assessment", tags=["assessment"])


class DocumentSummary(BaseModel):
    kind: DocumentKind
    pages: int | None
    characters: int
    truncated: bool
    preview: str


@router.get("/checklist")
def checklist() -> dict:
    """The controls a plan is assessed against, with their framework references."""
    return get_checklist().model_dump()


@router.post("/document", response_model=DocumentSummary)
async def inspect_document(file: UploadFile = File(...)) -> DocumentSummary:
    """Validate an IR plan upload and report what text could be extracted.

    Oversized bodies are rejected by BodySizeLimitMiddleware before parsing. The file
    is processed in memory and discarded when the request ends; nothing is stored and
    nothing from the document is logged.
    """
    try:
        data = await file.read(MAX_UPLOAD_BYTES + 1)  # never read more than the limit
        doc = extract_document(file.filename or "", data)
    except DocumentError as exc:
        status = 413 if isinstance(exc, DocumentTooLargeError) else 422
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    finally:
        await file.close()  # releases Starlette's temporary spool file, if one was created
    return DocumentSummary(
        kind=doc.kind, pages=doc.pages, characters=len(doc.text), truncated=doc.truncated, preview=doc.text[:600]
    )
