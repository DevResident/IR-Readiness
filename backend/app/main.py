"""FastAPI entry point for IR Readiness Copilot."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.frameworks.attack import get_catalog

settings = get_settings()

app = FastAPI(
    title="IR Readiness Copilot",
    version="0.1.0",
    description="AI-assisted incident response readiness: plan assessment, tabletop exercises and after-action reports.",
)

# Only the frontend origin(s) may call the API from a browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict:
    catalog = get_catalog()
    return {
        "status": "ok",
        "attack_version": catalog.version,
        "attack_techniques": len(catalog),
        "llm_configured": settings.anthropic_api_key is not None,
    }


@app.get("/api/attack/techniques/{technique_id}")
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
