"""
Main FastAPI Application
Entry point for the AI Booking Assistant
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.routes import chat
from app.routes import voice
from app.routes import admin
# Create FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered lead capture and appointment booking system",
    docs_url="/docs",  # Swagger UI documentation
    redoc_url="/redoc"  # ReDoc documentation
)

# CORS Configuration
# Allows frontend apps to connect to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(admin.router)
# Health Check Endpoint
@app.get("/")
async def root():
    """
    Root endpoint - confirms server is running
    """
    return {
        "message": "AI Booking Assistant API is running!",
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Health Check Endpoint (standard naming)
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    Used by hosting platforms to check if app is alive
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }


# Startup Event
@app.on_event("startup")
async def startup_event():
    """
    Runs when the server starts
    Good place for initialization tasks
    """
    from app.config.settings import get_ai_provider_info
    
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    print(f"📚 API Documentation: http://localhost:{settings.PORT}/docs")
    
    # Show AI provider info
    ai_info = get_ai_provider_info()
    print(f"🤖 AI Provider: {ai_info['provider'].upper()}")
    print(f"🧠 AI Model: {ai_info['model']}")
    print(f"✅ AI Configured: {ai_info['configured']}")

# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs when the server stops
    Good place for cleanup tasks
    """
    print(f"🛑 {settings.APP_NAME} shutting down...")


# This runs when you execute: python -m uvicorn app.main:app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True  # Auto-restart on code changes (development only)
    )