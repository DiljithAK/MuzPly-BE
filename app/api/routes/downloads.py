from fastapi import APIRouter, HTTPException, status
from starlette.background import BackgroundTask
from fastapi.responses import FileResponse

from app.core.logging_config import configure_logging
from app.schemas.download import DownloadAudioRequest
from app.services.youtube_audio import AudioDownloadError, YouTubeAudioDownloader

router = APIRouter(prefix="/downloads", tags=["downloads"])
logger = configure_logging()


@router.post(
    "/audio",
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
    summary="Download YouTube audio as MP3",
)
async def download_audio(
    payload: DownloadAudioRequest,
) -> FileResponse:
    logger.info("Audio download requested")
    downloader = YouTubeAudioDownloader()

    try:
        audio_file = downloader.download_audio(str(payload.url))
    except AudioDownloadError as exc:
        logger.warning("Audio download rejected or failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    logger.info("Audio prepared successfully: %s", audio_file.file_name)

    return FileResponse(
        path=str(audio_file.file_path),
        media_type="audio/mpeg",
        filename=audio_file.file_name,
        background=BackgroundTask(downloader.cleanup, audio_file.cleanup_dir),
    )
