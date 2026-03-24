# {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── main.py          # Main FastAPI application
│   └── routes.py        # API routes
├── logs/                # Log files (created at runtime)
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Running the Server

**Development mode (with auto-reload):**
```bash
python -m src.main --reload
```

**Production mode:**
```bash
python -m src.main --port 8000 --log-level info
```

**With file logging:**
```bash
python -m src.main --log-to-file --log-level debug
```

## CLI Options

- `--port PORT` - Port to run on (default: 8000)
- `--host HOST` - Host to bind to (default: 0.0.0.0)
- `--reload` - Enable auto-reload for development
- `--log-level LEVEL` - Set logging level (debug, info, warning, error, critical)
- `--log-to-file` - Enable logging to file

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `PORT` - Server port
- `LOG_LEVEL` - Logging level
- `CORS_ORIGINS` - Comma-separated allowed origins
- `CORS_ALLOW_ALL` - Allow all origins (dev only)

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/v1/example` - Example endpoint

## Development

The server includes:
- ✅ Request ID tracking for distributed tracing
- ✅ Request/response logging middleware
- ✅ Global exception handling
- ✅ CORS configuration
- ✅ Health check endpoint
- ✅ Structured logging
- ✅ Environment-based configuration
- ✅ Standard response formats
