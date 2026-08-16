# Development Guide

## Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## Run In Development

```bash
uvicorn app.main:app --reload
```

## Run Tests

```bash
pytest
```

## Coding Conventions

- Keep route handlers thin
- Put external integration logic in services
- Use Pydantic models for request validation
- Prefer small, focused modules with clear names
- Keep request validation and download safety limits explicit and configurable
- Prefer validating video metadata before any download begins

## Operational Notes

- Ensure FFmpeg is installed on the host server
- Monitor temporary storage usage if download volume increases
- Consider reverse-proxy request size and timeout settings in deployment
