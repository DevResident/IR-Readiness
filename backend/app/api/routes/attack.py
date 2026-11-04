from fastapi import APIRouter

from app.catalogs.attack import get_catalog

router = APIRouter(prefix="/attack", tags=["attack"])


@router.get("/techniques/{technique_id}")
def validate_technique(technique_id: str) -> dict:
    """Debug/demo endpoint: shows exactly how the validator treats an ID."""
    result = get_catalog().validate(technique_id)
    tech = result.technique
    return {
        "input": result.input_id,
        "status": result.status.value,
        "accepted": result.accepted,
        "technique": None if tech is None else {
            "id": tech.id, "name": tech.name, "tactics": list(tech.tactics), "url": tech.url,
        },
        "note": result.note,
    }
