# Architecture Notes

## Design Goals

- Keep routing, validation, and download logic separated
- Minimize temporary storage lifetime
- Make testing straightforward by isolating the downloader service

## Layers

- `app/main.py`: FastAPI application bootstrap
- `app/api/routes/`: HTTP route definitions
- `app/schemas/`: Request models
- `app/services/`: Business logic and external tool interaction
- `app/core/`: Configuration and shared internals

## Temporary File Lifecycle

1. A request is received with a YouTube URL.
2. The request model validates that the submitted value is a proper YouTube URL.
3. The downloader inspects the video metadata and rejects anything over 15 minutes, live streams, and non-public videos.
4. The downloader creates a dedicated temporary directory for that request.
5. `yt-dlp` downloads and converts the video audio to MP3.
6. FastAPI returns the MP3 as a file download to the client.
7. A background cleanup task deletes the request-specific temporary directory.

## Future Improvements

- Add structured logging
- Add rate limiting and authentication
- Add observability metrics
- Add async job handling for large downloads if the API needs to scale
