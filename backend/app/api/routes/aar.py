from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse, Response

from app.api.deps import get_aar_service
from app.api.errors import llm_errors_as_http
from app.modules.aar.export import to_docx, to_markdown
from app.modules.aar.schemas import AARRequest, AfterActionReport
from app.modules.aar.service import AARService

router = APIRouter(prefix="/aar", tags=["after-action report"])

DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@router.post("", response_model=AfterActionReport)
def generate_aar(request: AARRequest, service: AARService = Depends(get_aar_service)) -> AfterActionReport:
    """Turn exercise or incident notes into an After-Action Report. Notes are never logged."""
    with llm_errors_as_http("report"):
        return service.generate(request)


@router.post("/markdown", response_class=PlainTextResponse)
def export_markdown(report: AfterActionReport) -> PlainTextResponse:
    return PlainTextResponse(to_markdown(report), media_type="text/markdown; charset=utf-8")


@router.post("/docx")
def export_docx(report: AfterActionReport) -> Response:
    return Response(
        to_docx(report),
        media_type=DOCX_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="after-action-report.docx"'},
    )
