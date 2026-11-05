from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.api.deps import get_assessment_service
from app.api.errors import llm_errors_as_http
from app.catalogs.checklists import get_checklist
from app.modules.assessment.ingest import (
    MAX_UPLOAD_BYTES,
    DocumentError,
    DocumentKind,
    DocumentTooLargeError,
    ExtractedDocument,
    extract_document,
)
from app.modules.assessment.schemas import AssessmentReport
from app.modules.assessment.service import AssessmentService

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
    doc = await _read_upload(file)
    return DocumentSummary(
        kind=doc.kind, pages=doc.pages, characters=len(doc.text), truncated=doc.truncated, preview=doc.text[:600]
    )


@router.post("", response_model=AssessmentReport)
async def assess_plan(
    file: UploadFile = File(...), service: AssessmentService = Depends(get_assessment_service)
) -> AssessmentReport:
    """Assess an IR plan against the readiness checklist.

    The plan text exists only for the duration of this request: it is sent to the
    model, the report is built, and the text is discarded. It is never logged.
    """
    doc = await _read_upload(file)
    with llm_errors_as_http("assessment"):
        return service.assess(doc)


async def _read_upload(file: UploadFile) -> ExtractedDocument:
    try:
        data = await file.read(MAX_UPLOAD_BYTES + 1)  # never read more than the limit
        return extract_document(file.filename or "", data)
    except DocumentError as exc:
        status = 413 if isinstance(exc, DocumentTooLargeError) else 422
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    finally:
        await file.close()  # releases Starlette's temporary spool file, if one was created
