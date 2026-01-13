"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from api.routers import wovens, pantone
from api.config import get_settings
from api.database import engine
from api.models import Base

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Executes startup and shutdown logic.
    """
    # Startup: Verify database connection
    try:
        with engine.connect() as conn:
            print("✓ Database connection established")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
    
    yield
    
    # Shutdown
    engine.dispose()
    print("✓ Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Penelope Dataset API",
    description="API for accessing woven fabric and Pantone color data",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "error": str(exc)
        }
    )


# Include routers
app.include_router(wovens.router)
app.include_router(pantone.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Penelope Dataset API",
        "version": "1.0.0",
        "endpoints": {
            "wovens": {
                "list": "GET /wovens",
                "detail": "GET /wovens/{id}"
            },
            "pantone_colors": {
                "list": "GET /pantone-colors",
                "detail": "GET /pantone-colors/detail?name={name}"
            }
        },
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        with engine.connect() as conn:
            return {
                "status": "healthy",
                "database": "connected"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
