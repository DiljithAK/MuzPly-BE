from pydantic import BaseModel, Field, HttpUrl, field_validator


YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
    "www.youtu.be",
}


class DownloadAudioRequest(BaseModel):
    url: HttpUrl = Field(..., description="Public YouTube video URL")

    @field_validator("url")
    @classmethod
    def validate_youtube_url(cls, value: HttpUrl) -> HttpUrl:
        if value.host not in YOUTUBE_HOSTS:
            raise ValueError("URL must belong to YouTube.")

        return value
