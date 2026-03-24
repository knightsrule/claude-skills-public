# Advanced FastAPI Patterns and Best Practices

This document contains optional features and advanced patterns you can add to your FastAPI server.

## Rate Limiting

Protect endpoints from abuse with rate limiting.

**Using slowapi:**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/limited")
@limiter.limit("5/minute")
async def limited_endpoint(request: Request):
    return {"message": "This endpoint is rate limited"}
```

**Dependencies:**
```bash
pip install slowapi
```

## Database Integration

### SQLAlchemy with Async Support

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
```

**Dependencies:**
```bash
pip install sqlalchemy asyncpg
```

## Authentication & Authorization

### JWT Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta

security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
async def protected_route(user_id: str = Depends(get_current_user)):
    return {"message": f"Hello user {user_id}"}
```

**Dependencies:**
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

## Background Tasks

For long-running operations without blocking the response.

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Simulate sending email
    logger.info(f"Sending email to {email}: {message}")

@app.post("/send-notification")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Hello!")
    return {"message": "Notification will be sent"}
```

## Prometheus Metrics

Add monitoring with Prometheus metrics.

```python
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()

@app.on_event("startup")
async def startup():
    instrumentator.instrument(app).expose(app)

# Metrics available at /metrics
```

**Dependencies:**
```bash
pip install prometheus-fastapi-instrumentator
```

## Request Timeout

Add global request timeout to prevent hanging requests.

```python
from fastapi import Request
import asyncio

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=30.0)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"error": "Request timeout"}
        )
```

## API Versioning

Structure your API with versioning.

```python
# src/api/v1/routes.py
v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

@v1_router.get("/items")
async def get_items_v1():
    return {"version": "1.0", "items": []}

# src/api/v2/routes.py
v2_router = APIRouter(prefix="/api/v2", tags=["v2"])

@v2_router.get("/items")
async def get_items_v2():
    return {"version": "2.0", "items": [], "metadata": {}}

# In main.py
app.include_router(v1_router)
app.include_router(v2_router)
```

## Dependency Injection Patterns

### Configuration Dependency

```python
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

@app.get("/config")
async def get_config(settings: Settings = Depends(get_settings)):
    return {"database": settings.database_url}
```

## Testing

### Test Setup

```python
# tests/test_main.py
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_endpoint():
    response = client.post("/api/v1/example", json={"name": "test"})
    assert response.status_code == 200
    assert response.json()["success"] is True
```

**Dependencies:**
```bash
pip install pytest pytest-asyncio httpx
```

## WebSocket Support

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
```

## Static Files

Serve static files (images, CSS, JS).

```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

## CORS Advanced Configuration

More granular CORS control per route.

```python
from fastapi.middleware.cors import CORSMiddleware

# Different CORS for different route groups
public_router = APIRouter(prefix="/public")
# Public routes allow all origins

private_router = APIRouter(prefix="/private")
# Private routes have strict CORS

# Apply different middleware to sub-applications if needed
```

## Custom OpenAPI Documentation

Customize Swagger/ReDoc appearance.

```python
app = FastAPI(
    title="My API",
    description="Detailed API description with examples",
    version="2.0.0",
    openapi_tags=[
        {"name": "users", "description": "User management"},
        {"name": "items", "description": "Item operations"},
    ],
    docs_url="/documentation",  # Custom docs URL
    redoc_url="/redocumentation",  # Custom ReDoc URL
)
```

## Structured Logging with Context

Add request context to all logs.

```python
import contextvars
from logging import LoggerAdapter

request_id_var = contextvars.ContextVar('request_id', default=None)

class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True

# Add filter to all handlers
for handler in logging.getLogger().handlers:
    handler.addFilter(RequestContextFilter())

# In middleware
request_id_var.set(request_id)
```
