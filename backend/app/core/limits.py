"""Request body size limits, enforced before FastAPI parses the body.

A ``File(...)`` parameter makes Starlette parse the whole multipart body before the
endpoint runs, so a size check inside the endpoint is too late to stop a huge upload.
This middleware rejects oversized uploads using Content-Length, and rejects uploads
that do not declare a length (chunked encoding), which could otherwise bypass it.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.modules.assessment.ingest import MAX_UPLOAD_BYTES

# Path prefix -> (maximum body size in bytes, message). Multipart framing adds a little overhead.
UPLOAD_LIMITS = {
    "/api/assessment": (MAX_UPLOAD_BYTES + 64 * 1024, f"The file is larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB."),
    "/api/aar": (512 * 1024, "The request body is too large."),  # notes (30k chars max) or a report to export
}


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method == "POST":
            for prefix, (limit, message) in UPLOAD_LIMITS.items():
                if request.url.path.startswith(prefix):
                    declared = request.headers.get("content-length")
                    if declared is None or not declared.isdigit():
                        return JSONResponse({"detail": "A Content-Length header is required."}, status_code=411)
                    if int(declared) > limit:
                        return JSONResponse({"detail": message}, status_code=413)
        return await call_next(request)
