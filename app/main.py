from fastapi import FastAPI

from app.api.routes.downloads import router as downloads_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API for downloading YouTube audio as MP3 and returning it as a "
        "temporary downloadable file."
    ),
)

app.include_router(downloads_router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

