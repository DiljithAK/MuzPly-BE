# API Guide

## Endpoint

`POST /api/v1/downloads/audio`

## Request Body

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

## Success Response

- Status: `200 OK`
- Content-Type: `audio/mpeg`
- Content-Disposition: attachment with generated MP3 filename

## Error Response

- Status: `400 Bad Request`
- Returned when the media cannot be inspected, downloaded, or converted
- Returned when the video is private, live, unavailable, or longer than the allowed limit
- Status: `422 Unprocessable Entity`
- Returned when the request body is invalid, the URL is not a valid text URL, or the URL is not a YouTube URL

## Notes

- The API is synchronous from the client perspective: it waits for download and MP3 conversion, then sends the file in the same request.
- The API checks video metadata before download and rejects videos longer than 15 minutes.
- Temporary server storage is removed in a background task after the file response completes.
- FFmpeg must be available on the server for MP3 extraction.
