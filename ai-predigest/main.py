"""
MyZodiaq Marriage API - Main Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.routes import router
from app.api.realtime_routes import router as realtime_router
from app.services.db_service import db_service
from app.services.event_manager import event_manager
from config import get_settings

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    
    # Initialize database
    if settings.DATABASE_URL:
        logger.info("Initializing PostgreSQL database...")
        await db_service.initialize()
        logger.info("Database initialized successfully")
    else:
        logger.warning("DATABASE_URL not configured - using in-memory storage")
    
    # Start event manager for real-time SSE/WebSocket
    logger.info("Starting Event Manager for real-time updates...")
    await event_manager.start()
    logger.info("Event Manager started successfully")
    
    yield
    
    # Cleanup
    logger.info("Stopping Event Manager...")
    await event_manager.stop()
    
    if settings.DATABASE_URL:
        logger.info("Closing database connection...")
        await db_service.close()
    
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## MyZodiaq Marriage Astrology API

Provides Vedic and KP astrology predictions for marriage domain analysis.

### Features
- **Single Person Analysis**: Marriage prospects, timing, partner traits, remedies
- **Two Person Compatibility**: Comprehensive compatibility analysis between two charts
- **Real-time Updates**: SSE and WebSocket support for live progress tracking

### API Flow
```
1. POST /api/v1/predict  →  Get response_id
2. Connect to real-time updates (choose one):
   - SSE: GET /api/v1/realtime/sse/{response_id}
   - WebSocket Single: WS /api/v1/realtime/ws/{response_id}
   - WebSocket Multi: WS /api/v1/realtime/ws
3. GET /api/v1/result/{response_id}  →  Get full result (or receive via events)
```

### Real-time Event Types
- `connection`: Initial connection established
- `progress`: Progress update (percentage + message)
- `completed`: Prediction finished with result
- `failed`: Prediction failed with error
- `keepalive`: Connection health heartbeat

### SSE Example (JavaScript)
```javascript
const eventSource = new EventSource('/api/v1/realtime/sse/' + responseId);
eventSource.addEventListener('progress', (e) => console.log(JSON.parse(e.data)));
eventSource.addEventListener('completed', (e) => {
  console.log('Done!', JSON.parse(e.data));
  eventSource.close();
});
```

### WebSocket Example (JavaScript)
```javascript
const ws = new WebSocket('ws://host/api/v1/realtime/ws');
ws.onopen = () => ws.send(JSON.stringify({command: 'subscribe', response_id: '...'}));
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

### Supported Domains
- Marriage (Marriage Prospects, Marital Stability, Compatibility)
- Love_Life (Love Prospects, Compatibility)

### LLM Providers Supported
- Groq (default)
- OpenAI
- Azure OpenAI
- Anthropic
- Google Gemini
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["Predictions"])
app.include_router(realtime_router, prefix="/api/v1", tags=["Real-time Events"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health",
        "api_flow": {
            "1_submit": "POST /api/v1/predict",
            "2a_sse": "GET /api/v1/realtime/sse/{response_id}",
            "2b_ws_single": "WS /api/v1/realtime/ws/{response_id}",
            "2c_ws_multi": "WS /api/v1/realtime/ws",
            "3_result": "GET /api/v1/result/{response_id}"
        },
        "realtime_events": {
            "sse_endpoint": "/api/v1/realtime/sse/{response_id}",
            "websocket_single": "/api/v1/realtime/ws/{response_id}",
            "websocket_multi": "/api/v1/realtime/ws",
            "event_history": "/api/v1/realtime/events/{response_id}/history",
            "connection_stats": "/api/v1/realtime/stats"
        }
    }


def custom_openapi():
    """Custom OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=app.description,
        routes=app.routes,
    )
    
    # Add example requests
    openapi_schema["info"]["x-logo"] = {
        "url": "https://myzodiaq.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
