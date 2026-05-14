# ClearView FastAPI Backend

Production-style FastAPI backend skeleton with async SQLAlchemy, Pydantic, and dependency injection.

## Requirements

- Python 3.11+
- PostgreSQL (for async database support)

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your `DATABASE_URL` and other settings.

4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

   Or:
   ```bash
   python -m app.main
   ```

## Endpoints

- `GET /health` - Health check (returns `{"status": "ok"}`)
- `POST /workspaces` - Create a workspace
- `GET /workspaces` - List all workspaces
- `POST /sources/text` - Create a text source
- `POST /sources/url` - Fetch a webpage, extract readable text, and create a URL source
- `GET /sources?workspace_id=...` - List sources in a workspace
- `GET /sources/{id}` - Get source details with `chunk_count`
- `GET /chunks?source_id=...` - List chunks for a source
- `DELETE /sources/{id}` - Delete a source
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc documentation

## Testing Workspaces & Sources

1. Start PostgreSQL (e.g. via Docker):
   ```bash
   docker compose up -d
   ```

2. Ensure `.env` has:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/clearview
   ```

3. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```
   Tables are created automatically on startup via `init_db()`.

4. Run the test script:
   ```bash
   python scripts/test_workspaces_and_sources.py
   ```
   Or with curl + jq:
   ```bash
   chmod +x scripts/test_workspaces_and_sources.sh
   ./scripts/test_workspaces_and_sources.sh
   ```

## Project Structure

```
app/
├── main.py              # FastAPI app entry point
├── api/
│   └── routes.py        # API route definitions
├── core/
│   ├── config.py        # Pydantic settings from .env
│   ├── logging_config.py
│   └── deps.py          # Dependency injection
├── db/
│   ├── base.py          # SQLAlchemy declarative base
│   └── session.py       # Async engine & session factory
├── models/              # SQLAlchemy models
└── services/            # Business logic layer
```

## License

MIT
