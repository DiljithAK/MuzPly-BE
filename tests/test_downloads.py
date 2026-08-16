from pathlib import Path

import pytest

from app.schemas.download import DownloadAudioRequest
from app.services.youtube_audio import AudioDownloadError
from app.services.youtube_audio import YouTubeAudioDownloader


def test_cleanup_removes_request_temp_directory(tmp_path: Path) -> None:
    temp_dir = tmp_path / "request"
    nested_file = temp_dir / "sample.mp3"
    temp_dir.mkdir()
    nested_file.write_bytes(b"fake-mp3")

    assert temp_dir.exists()
    assert nested_file.exists()

    YouTubeAudioDownloader.cleanup(temp_dir)

    assert not temp_dir.exists()


def test_download_request_rejects_non_youtube_url() -> None:
    with pytest.raises(ValueError, match="URL must belong to YouTube."):
        DownloadAudioRequest(url="https://example.com/audio-track")


def test_download_request_accepts_youtube_url() -> None:
    payload = DownloadAudioRequest(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    assert str(payload.url) == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_validate_duration_rejects_long_video() -> None:
    downloader = YouTubeAudioDownloader()

    with pytest.raises(
        AudioDownloadError,
        match="Video is too long. Maximum allowed duration is 15 minutes.",
    ):
        downloader._validate_metadata(
            {
                "duration": 901,
                "title": "Sample",
                "extractor_key": "Youtube",
            }
        )


def test_validate_duration_requires_known_duration() -> None:
    downloader = YouTubeAudioDownloader()

    with pytest.raises(
        AudioDownloadError,
        match="Unable to determine video duration.",
    ):
        downloader._validate_metadata(
            {
                "title": "Sample",
                "extractor_key": "Youtube",
            }
        )


def test_validate_metadata_rejects_live_videos() -> None:
    downloader = YouTubeAudioDownloader()

    with pytest.raises(
        AudioDownloadError,
        match="Live streams are not supported for MP3 downloads.",
    ):
        downloader._validate_metadata(
            {
                "duration": 300,
                "title": "Live Stream",
                "extractor_key": "Youtube",
                "is_live": True,
            }
        )


def test_validate_metadata_rejects_private_videos() -> None:
    downloader = YouTubeAudioDownloader()

    with pytest.raises(
        AudioDownloadError,
        match="This video is not publicly available for download.",
    ):
        downloader._validate_metadata(
            {
                "duration": 300,
                "title": "Private Video",
                "extractor_key": "Youtube",
                "availability": "private",
            }
        )


def test_validate_metadata_rejects_non_youtube_extractor() -> None:
    downloader = YouTubeAudioDownloader()

    with pytest.raises(
        AudioDownloadError,
        match="The supplied URL is not recognized as a YouTube video.",
    ):
        downloader._validate_metadata(
            {
                "duration": 300,
                "title": "Sample",
                "extractor_key": "Vimeo",
            }
        )
