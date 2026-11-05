from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.api.deps import get_tabletop_service
from app.catalogs.ir_lifecycle import get_ir_lifecycle
from app.catalogs.scenarios import get_scenarios
from app.api.errors import llm_errors_as_http
from app.modules.tabletop.markdown import render_markdown
from app.modules.tabletop.schemas import Audience, Industry, OrgSize, TabletopExercise, TabletopRequest
from app.modules.tabletop.service import TabletopService

router = APIRouter(prefix="/tabletop", tags=["tabletop"])


@router.get("/options")
def options() -> dict:
    """Everything the frontend needs to build the tabletop form."""
    return {
        "industries": [i.value for i in Industry],
        "org_sizes": [s.value for s in OrgSize],
        "audiences": [a.value for a in Audience],
        "scenarios": [{"id": s.id, "name": s.name, "summary": s.summary} for s in get_scenarios().values()],
        "phases": [
            {"id": p.id, "name": p.name, "csf_functions": list(p.csf_functions), "rev2_equivalent": p.rev2_equivalent}
            for p in get_ir_lifecycle().phases
        ],
    }


@router.post("", response_model=TabletopExercise)
def generate_tabletop(request: TabletopRequest, service: TabletopService = Depends(get_tabletop_service)) -> TabletopExercise:
    # Error messages are generic on purpose: no provider details or model output leak to clients.
    with llm_errors_as_http("exercise"):
        return service.generate(request)


@router.post("/markdown", response_class=PlainTextResponse)
def export_markdown(exercise: TabletopExercise) -> PlainTextResponse:
    """Render an exercise (as returned by POST /api/tabletop) as Markdown. No LLM call."""
    return PlainTextResponse(render_markdown(exercise), media_type="text/markdown; charset=utf-8")
