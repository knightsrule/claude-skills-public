---
name: fastapi-server
description: "Template-based FastAPI server creation with production-ready defaults. Use when building new FastAPI servers or APIs with standardized patterns including: (1) configurable logging (console and file), (2) CORS configuration with environment-based origins, (3) request ID tracking, (4) global exception handling, (5) health check endpoints, (6) structured response formats, and (7) CLI argument support. Triggers on requests to create a FastAPI server, scaffold an API, build a REST API, or similar server initialization tasks."
---

# FastAPI Server Template

This skill provides a production-ready FastAPI server template with enterprise-grade features pre-configured. Use this skill to quickly scaffold new FastAPI projects with consistent patterns for logging, error handling, CORS, and request tracking.

## Quick Start

Initialize a new FastAPI project:

1. Run the initialization script with your project details:
```bash
python scripts/init_project.py <project-name> \
    --description "Your project description" \
    --template-dir assets/templates \
    --output-dir <output-directory>
```

2. The script creates a complete project structure with all template files, replacing `{{PROJECT_NAME}}` and `{{PROJECT_DESCRIPTION}}` placeholders.

3. Follow the post-initialization steps to set up the virtual environment and install dependencies.

## Project Structure Created

```
project-name/
├── src/
│   ├── __init__.py
│   ├── main.py          # Main application with all middleware
│   └── routes.py        # Example API routes
├── logs/                # Created at runtime for log files
├── .env                 # Environment configuration
├── .env.example         # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

## Included Features

The template includes these production-ready features:

**Core Functionality:**
- FastAPI application with lifespan management
- Configurable logging (console and file output)
- Environment-based configuration via .env
- CLI argument parsing for flexible deployment
- Health check endpoint

**Middleware Stack:**
- Request ID tracking for distributed tracing
- Request/response logging with timing
- CORS with environment-configurable origins
- Global exception handlers

**Error Handling:**
- Structured error responses
- Request validation error handling
- Unexpected exception catching with logging
- Standard response format (success/error)

**Configuration:**
- Environment variable validation on startup
- Support for multiple CORS origins
- Configurable log levels and output
- Port and host configuration

## Configuration Options

### Environment Variables

Key variables in `.env`:

```bash
# Server
PORT=8000
LOG_LEVEL=info
APP_LOG_LEVEL=INFO
APP_LOG_TO_FILE=false

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_ALLOW_ALL=false  # Development only

# Environment
ENVIRONMENT=development
```

### CLI Arguments

```bash
python -m src.main [options]

Options:
  --port PORT           Server port (default: 8000)
  --host HOST           Bind host (default: 0.0.0.0)
  --reload              Enable auto-reload for development
  --log-level LEVEL     Logging level (debug|info|warning|error|critical)
  --log-to-file         Enable file logging
```

## Customization Points

After initialization, customize these areas:

1. **Environment validation** in `main.py`:
   - Add required environment variables to `validate_environment()`

2. **API routes** in `routes.py`:
   - Replace example endpoints with your business logic
   - Add request/response models

3. **CORS origins**:
   - Update `CORS_ORIGINS` in `.env` for your domains
   - Add default origins in `main.py` if needed

4. **Dependencies**:
   - Uncomment needed packages in `requirements.txt`
   - Add project-specific dependencies

5. **Response models**:
   - Extend `SuccessResponse` and `ErrorResponse` classes
   - Add domain-specific response types

## Standard Response Format

All endpoints should use the standard format:

**Success:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error description",
  "details": { ... },
  "request_id": "uuid"
}
```

## Advanced Patterns

For additional features beyond the base template, see `references/advanced_patterns.md`:

- Rate limiting with slowapi
- Database integration (SQLAlchemy async)
- JWT authentication
- Background tasks
- Prometheus metrics
- Request timeouts
- API versioning
- WebSocket support
- Testing patterns

Load these patterns only when specifically needed for the project.

## Example Usage

**Basic server:**
```bash
# Initialize
python scripts/init_project.py my-api \
    --description "My REST API" \
    --template-dir assets/templates \
    --output-dir .

cd my-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python -m src.main --reload
```

**Production deployment:**
```bash
# Set production environment
export ENVIRONMENT=production
export CORS_ORIGINS=https://myapp.com,https://api.myapp.com
export APP_LOG_TO_FILE=true
export APP_LOG_LEVEL=INFO

# Run with gunicorn
gunicorn src.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

## Adding Custom Features

When users request additional features:

1. Check if the pattern exists in `references/advanced_patterns.md`
2. If yes, read that section and implement it
3. If no, implement from scratch following FastAPI best practices
4. Maintain consistency with existing middleware stack
5. Update the project's README.md with new features

## Common Modifications

**Add database:**
- Read `references/advanced_patterns.md` → Database Integration
- Add SQLAlchemy dependency
- Create database models
- Add connection to lifespan

**Add authentication:**
- Read `references/advanced_patterns.md` → Authentication & Authorization
- Add JWT dependencies
- Create auth middleware
- Protect routes with dependencies

**Add rate limiting:**
- Read `references/advanced_patterns.md` → Rate Limiting
- Add slowapi dependency
- Configure limiter in main.py
- Apply to endpoints

## Notes

- Template uses placeholders `{{PROJECT_NAME}}` and `{{PROJECT_DESCRIPTION}}`
- Initialization script automatically replaces placeholders
- All paths assume project root as working directory
- Logging configuration happens in lifespan for proper worker process setup
- Request ID middleware must come before logging middleware
- Environment validation runs on startup to fail fast
