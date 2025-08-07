# Reader Backend

Backend API cho webapp đọc truyện với FastAPI và Supabase.

## Features

- FastAPI REST API
- Supabase integration
- OAuth authentication
- EPUB processing
- Caching with Redis
- Admin management

## Development

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn main:app --reload
```

## Production

```bash
# Build Docker image
docker build -t reader-backend .

# Run with Docker Compose
docker-compose up backend
```