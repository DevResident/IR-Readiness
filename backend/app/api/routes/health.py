from fastapi import APIRouter

from app.catalogs.attack import get_catalog
from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    catalog = get_catalog()
    settings = get_settings()
    return {
        "status": "ok",
        "attack_version": catalog.version,
        "attack_techniques": len(catalog),
        "llm_provider": settings.llm_provider,
        "llm_configured": settings.llm_configured,
    }
