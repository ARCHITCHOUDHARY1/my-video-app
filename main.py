# main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import uvicorn
import os

from config import settings
from models import HealthResponse, VideoGenerationRequest, VideoJobResponse, ScriptRequest, ScriptResponse
from api.routes import router
from api.websocket import manager, websocket_endpoint
from utils.logger_config import setup_logger
from database import engine, Base

logger = setup_logger('main')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Verify directories
    os.makedirs(settings.output_dir, exist_ok=True)
    os.makedirs(settings.temp_dir, exist_ok=True)
    logger.info("Directories verified")
    
    yield
    
    logger.info("Shutting down application")

app = FastAPI(
    title="Video Synthesis System API",
    description="AI-powered video generation with style analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["video"])

# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_route(websocket: WebSocket, client_id: str):
    await websocket_endpoint(websocket, client_id)

# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        services = {
            "database": True,
            "mistral": bool(settings.mistral_api_key),
            "ollama": True,  # Local, always available
            "ffmpeg": os.path.exists(settings.ffmpeg_path) if hasattr(settings, 'ffmpeg_path') and settings.ffmpeg_path else False
        }
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            services=services
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Video Synthesis System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )