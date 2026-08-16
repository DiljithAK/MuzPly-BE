from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from app.core.config import get_settings


class AudioDownloadError(Exception):
    pass


@dataclass(slots=True)
class DownloadedAudioFile:
    file_path: Path
    file_name: str
    cleanup_dir: Path


class YouTubeAudioDownloader:
    def __init__(self) -> None:
        self.settings = get_settings()

    def download_audio(self, url: str) -> DownloadedAudioFile:
        if shutil.which("ffmpeg") is None:
            raise AudioDownloadError("FFmpeg is not installed or not available in PATH.")

        metadata = self._fetch_metadata(url)
        self._validate_metadata(metadata)

        temp_dir = Path(tempfile.mkdtemp(prefix="muzply-audio-"))
        output_template = str(temp_dir / "%(title)s.%(ext)s")

        options = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "restrictfilenames": True,
            "windowsfilenames": True,
            "socket_timeout": self.settings.download_timeout_seconds,
            "retries": 3,
            "fragment_retries": 3,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": str(self.settings.mp3_audio_quality_kbps),
                }
            ],
        }

        try:
            with YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                prepared_name = ydl.prepare_filename(info)
        except DownloadError as exc:
            self.cleanup(temp_dir)
            raise AudioDownloadError(
                f"Unable to download audio from the supplied URL: {exc}"
            ) from exc
        except Exception as exc:
            self.cleanup(temp_dir)
            raise AudioDownloadError(
                f"Unexpected error while downloading audio: {exc}"
            ) from exc

        mp3_path = Path(prepared_name).with_suffix(".mp3")
        if not mp3_path.exists():
            self.cleanup(temp_dir)
            raise AudioDownloadError(
                "Audio conversion completed unsuccessfully. Ensure FFmpeg is installed."
            )

        return DownloadedAudioFile(
            file_path=mp3_path,
            file_name=mp3_path.name,
            cleanup_dir=temp_dir,
        )

    def _fetch_metadata(self, url: str) -> dict:
        options = {
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": self.settings.download_timeout_seconds,
        }

        try:
            with YoutubeDL(options) as ydl:
                return ydl.extract_info(url, download=False)
        except DownloadError as exc:
            raise AudioDownloadError(
                f"Unable to inspect the supplied URL before download: {exc}"
            ) from exc
        except Exception as exc:
            raise AudioDownloadError(
                f"Unexpected error while inspecting the supplied URL: {exc}"
            ) from exc

    def _validate_metadata(self, metadata: dict) -> None:
        if not metadata:
            raise AudioDownloadError("No video metadata was returned for the supplied URL.")

        if metadata.get("is_live"):
            raise AudioDownloadError("Live streams are not supported for MP3 downloads.")

        if metadata.get("was_live"):
            raise AudioDownloadError("Previously live videos are not supported for MP3 downloads.")

        if metadata.get("availability") in {"private", "subscriber_only", "needs_auth"}:
            raise AudioDownloadError("This video is not publicly available for download.")

        if not metadata.get("title"):
            raise AudioDownloadError("Unable to determine the video title from the supplied URL.")

        extractor = str(metadata.get("extractor_key", "")).lower()
        if "youtube" not in extractor:
            raise AudioDownloadError("The supplied URL is not recognized as a YouTube video.")

        duration = metadata.get("duration")
        if duration is None:
            raise AudioDownloadError("Unable to determine video duration.")

        if duration > self.settings.max_audio_duration_seconds:
            max_minutes = self.settings.max_audio_duration_seconds // 60
            raise AudioDownloadError(
                f"Video is too long. Maximum allowed duration is {max_minutes} minutes."
            )

    @staticmethod
    def cleanup(path: Path) -> None:
        shutil.rmtree(path, ignore_errors=True)
