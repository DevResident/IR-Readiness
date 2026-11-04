from fastapi import APIRouter

from app.catalogs.ir_lifecycle import get_ir_lifecycle
from app.catalogs.scenarios import get_scenarios
from app.modules.tabletop.schemas import Audience, Industry, OrgSize

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
