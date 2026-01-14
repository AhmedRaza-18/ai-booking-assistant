"""
Main FastAPI Application
Entry point for the AI Booking Assistant
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routes import chat, voice, admin
from app.services.conversation_service import conversation_manager

import logging
import os

logger = logging.getLogger("uvicorn.error")

# --- FastAPI App ---
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered lead capture and appointment booking system",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for demo / Render free
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(admin.router)

# --- Health Check Endpoints ---
@app.get("/")
async def root():
    return {
        "message": "AI Booking Assistant API is running!",
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    """
    Runs when the server starts
    """
    from app.config.settings import get_ai_provider_info

    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    logger.info(f"📝 Environment: {settings.ENVIRONMENT}")
    logger.info(f"📚 API Docs: /docs")

    ai_info = get_ai_provider_info()
    logger.info(f"🤖 AI Provider: {ai_info['provider'].upper()}")
    logger.info(f"🧠 AI Model: {ai_info['model']}")
    logger.info(f"✅ AI Configured: {ai_info['configured']}")

# --- Shutdown Event ---
@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs when the server stops
    Persist remaining sessions
    """
    logger.info(f"🛑 {settings.APP_NAME} shutting down...")
    for session in conversation_manager.sessions.values():
        conversation_manager.persist_session(session)
    logger.info("✅ Remaining sessions persisted")

# --- Run with uvicorn ---
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
