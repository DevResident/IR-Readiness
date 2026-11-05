"""FastAPI entry point for IR Readiness Copilot.

Layout:
    app/api/routes/   HTTP endpoints, one router per area
    app/core/         cross-cutting concerns (settings)
    app/catalogs/     loaders and validators for the data in /frameworks
    app/modules/      business logic per product module (tabletop, assessment, aar)
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import aar, assessment, attack, health, tabletop
from app.core.config import get_settings
from app.core.limits import BodySizeLimitMiddleware

settings = get_settings()

# Application logs (uvicorn configures only its own loggers). Never log prompts or model output.
logging.basicConfig(level=settings.log_level.upper(), format="%(levelname)s:     %(name)s - %(message)s")

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

# Reject oversized uploads before the body is parsed.
app.add_middleware(BodySizeLimitMiddleware)

app.include_router(health.router, prefix="/api")
app.include_router(attack.router, prefix="/api")
app.include_router(tabletop.router, prefix="/api")
app.include_router(assessment.router, prefix="/api")
app.include_router(aar.router, prefix="/api")
