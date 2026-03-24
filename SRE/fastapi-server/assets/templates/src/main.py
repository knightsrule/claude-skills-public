import os
import sys
import logging
import uuid
import time
import uvicorn
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from typing import Optional

# Load environment variables from .env
load_dotenv(Path(__file__).parent.parent / ".env")

# Configure logging
logger = logging.getLogger(__name__)


def configure_logging(level_name="INFO", log_to_file=False):
    """Configure logging with console and optional file output."""
    # Remove all handlers to avoid duplication
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_to_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_root = Path(__file__).parent.parent
        log_file = project_root / f"logs/server-{timestamp}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, mode="a"))

    # Map log levels
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    effective_level = log_levels.get(level_name, logging.INFO)

    # Configure root logger
    root_logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    for handler in handlers:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    # Set application logger level
    app_logger = logging.getLogger("src")
    app_logger.setLevel(effective_level)
    logger.info(f"Logging configured: Level={level_name}, File={log_to_file}")


def validate_environment():
    """Validate required environment variables on startup."""
    required_vars = []  # Add required env vars here, e.g., ["DATABASE_URL", "API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        error_msg = f"Missing required environment variables: {', '.join(missing)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    logger.info("Environment validation passed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    log_level = os.getenv("APP_LOG_LEVEL", "INFO").upper()
    log_to_file = os.getenv("APP_LOG_TO_FILE", "False").lower() == "true"

    configure_logging(log_level, log_to_file)
    logger.info("Application starting up...")

    # Validate environment
    try:
        validate_environment()
    except RuntimeError as e:
        logger.error(f"Startup validation failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Application shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="{{PROJECT_NAME}}",
    description="{{PROJECT_DESCRIPTION}}",
    version="1.0.0",
    lifespan=lifespan,
)


# Request ID Middleware (for request tracing)
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracing."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Add request ID to logs
    with logging.LoggerAdapter(logger, {"request_id": request_id}):
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests and responses."""
    # Skip logging for health checks
    if request.url.path == "/health":
        return await call_next(request)

    start_time = time.time()
    request_id = getattr(request.state, "request_id", "unknown")

    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={"request_id": request_id}
    )

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"Request completed: {request.method} {request.url.path} "
        f"status={response.status_code} duration={process_time:.3f}s",
        extra={"request_id": request_id}
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


# Configure CORS
cors_origins_env = os.getenv("CORS_ORIGINS", "").strip()
if cors_origins_env:
    allow_origins = [
        origin.strip() for origin in cors_origins_env.split(",") if origin.strip()
    ]
else:
    # Default development origins
    allow_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

cors_allow_all = os.getenv("CORS_ALLOW_ALL", "").lower() == "true"
allow_credentials = True

if cors_allow_all:
    logger.warning("CORS_ALLOW_ALL enabled - credentials disabled for security")
    allow_credentials = False
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*",
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    logger.info(f"CORS configured with origins: {allow_origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Global Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={"request_id": request_id}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "request_id": request_id
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"request_id": request_id}
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors(),
            "request_id": request_id
        }
    )


# Standard response models
class SuccessResponse:
    """Standard success response format."""
    @staticmethod
    def create(data=None, message: Optional[str] = None):
        response = {"success": True}
        if data is not None:
            response["data"] = data
        if message:
            response["message"] = message
        return response


class ErrorResponse:
    """Standard error response format."""
    @staticmethod
    def create(error: str, details=None):
        response = {"success": False, "error": error}
        if details is not None:
            response["details"] = details
        return response


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint."""
    return SuccessResponse.create(
        data={
            "name": "{{PROJECT_NAME}}",
            "version": "1.0.0",
            "endpoints": {
                "/": "API information",
                "/health": "Health check endpoint",
                "/docs": "API documentation",
            }
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Import and include routers
# from .routes import router
# app.include_router(router)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the {{PROJECT_NAME}} Server")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8000")),
        help="Port to run the server on (default: 8000 or PORT env variable)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to run the server on (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=os.getenv("LOG_LEVEL", "info"),
        choices=["debug", "info", "warning", "error", "critical"],
        help="Set the logging level (default: info)",
    )
    parser.add_argument(
        "--log-to-file",
        action="store_true",
        help="Log to file when set",
    )

    args = parser.parse_args()

    # Set environment variables from CLI args
    os.environ["APP_LOG_LEVEL"] = args.log_level.upper()
    os.environ["APP_LOG_TO_FILE"] = str(args.log_to_file)

    print(
        f"Starting {{PROJECT_NAME}} Server on {args.host}:{args.port} "
        f"with log level {args.log_level}"
    )

    uvicorn.run(
        "src.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level.lower(),
        proxy_headers=True,
    )
