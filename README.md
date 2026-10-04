# Muzply YouTube Audio API

A maintainable FastAPI service that accepts a YouTube video URL, converts the audio to MP3, returns it as a downloadable file to the requesting client, and removes the temporary server file after the response is completed.

## Features

- FastAPI application with versioned API routing
- Request validation using Pydantic
- YouTube-only URL validation
- Pre-download duration check with a 15-minute maximum
- Better handling for unavailable, private, and live-video cases
- Dedicated service layer for YouTube audio download logic
- Temporary file cleanup after the file has been sent
- Simple test suite for health and download flow
- Clear project documentation for future maintenance

## Project Structure

```text
.
├── app
│   ├── api
│   │   └── routes
│   ├── core
│   ├── schemas
│   ├── services
│   └── main.py
├── docs
├── tests
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Prerequisites

- Python 3.11 or newer
- FFmpeg installed and available in the system `PATH`

`yt-dlp` can download the source media, but MP3 conversion requires FFmpeg.

## Local Setup

```bash
python3 -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell (if script execution is blocked)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## Run The API

```bash
uvicorn app.main:app --reload
```

Open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

## Example Request

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/downloads/audio" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}' \
  --output audio.mp3
```

The response is an `audio/mpeg` download. The server deletes the temporary file after the response has been sent.

## Validation Rules

- The `url` field must be a valid text URL in JSON
- The URL must belong to YouTube
- Videos longer than 15 minutes are rejected before download starts
- Live and non-public videos are rejected before download starts

## Audio Quality

The API requests the best available source audio from YouTube and then converts it to MP3 using the configured target bitrate. The default export target is `320 kbps`, which is the practical maximum for MP3 output, but the final quality can never exceed the original source audio quality provided by YouTube.

## Testing

```bash
pytest
```

## Documentation

- [API Guide](docs/API.md)
- [Architecture Notes](docs/ARCHITECTURE.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Contributing Guide](docs/CONTRIBUTING.md)
