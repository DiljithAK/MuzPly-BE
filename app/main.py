import time

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes.downloads import router as downloads_router
from app.core.config import get_settings
from app.core.logging_config import configure_logging

settings = get_settings()
logger = configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API for downloading YouTube audio as MP3 and returning it as a "
        "temporary downloadable file."
    ),
)

app.include_router(downloads_router, prefix=settings.api_prefix)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started_at = time.perf_counter()
    logger.info("Request started: %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled error for %s %s", request.method, request.url.path)
        raise

    elapsed_ms = (time.perf_counter() - started_at) * 1000
    logger.info(
        "Request completed: %s %s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.exception_handler(RequestValidationError)
async def log_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning(
        "Request validation failed: %s %s errors=%s",
        request.method,
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(exc.errors())},
    )


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

