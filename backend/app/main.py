"""FastAPI Application entry point for The Lenny Growth Assistant."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.api import health, sessions, chat

# Structured Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("lenny_assistant.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hook: initializes DB schema and models on startup."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    try:
        await init_db()
        logger.info("Database and vector schema verified.")
    except Exception as e:
        logger.error(f"Error during startup DB initialization: {e}")
    yield
    logger.info("Shutting down Lenny Growth Assistant.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise-grade RAG and Content Engine unlocking operational knowledge from Lenny's Podcast transcripts.",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits localhost:3000, preview URLs, etc.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(sessions.router, prefix=settings.API_PREFIX)
app.include_router(chat.router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health",
        "chat": f"{settings.API_PREFIX}/chat",
        "sessions": f"{settings.API_PREFIX}/sessions",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Server Error", "detail": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
