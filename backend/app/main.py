"""FastAPI entry point for IR Readiness Copilot.

Layout:
    app/api/routes/   HTTP endpoints, one router per area
    app/core/         cross-cutting concerns (settings)
    app/catalogs/     loaders and validators for the data in /frameworks
    app/modules/      business logic per product module (tabletop, assessment, aar)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import attack, health, tabletop
from app.core.config import get_settings

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

app.include_router(health.router, prefix="/api")
app.include_router(attack.router, prefix="/api")
app.include_router(tabletop.router, prefix="/api")
