"""
Main FastAPI application entry point.
"""

import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from api.routers import wovens, pantone, filters
from api.config import get_settings
from api.database import (
    engine,
    get_request_db_metrics,
    reset_request_db_metrics,
    start_request_db_metrics,
)
from api.models import Base, WovenInfo, VariantInfo, StockInfo, PantoneColor

settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Executes startup and shutdown logic.
    """
    # Startup: Verify database connection
    try:
        with engine.connect() as conn:
            logger.info("Database connection established")
    except Exception as e:
        logger.exception("Database connection failed: %s", e)
    
    yield
    
    # Shutdown
    engine.dispose()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Penelope Dataset API",
    description="API for accessing woven fabric, variant, stock and Pantone color data",
    version="2.0.0",
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


@app.middleware("http")
async def request_timing_middleware(request: Request, call_next):
    """Log total request time and aggregated DB query time for each request."""
    request_start = time.perf_counter()
    metrics_token = start_request_db_metrics()

    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        total_ms = (time.perf_counter() - request_start) * 1000
        db_metrics = get_request_db_metrics()
        status_code = response.status_code if response is not None else 500

        logger.info(
            "request_timing method=%s path=%s status=%s total_ms=%.2f db_query_ms=%.2f db_query_count=%d",
            request.method,
            request.url.path,
            status_code,
            total_ms,
            db_metrics["query_time_ms"],
            db_metrics["query_count"],
        )

        reset_request_db_metrics(metrics_token)


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
app.include_router(filters.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Penelope Dataset API",
        "version": "2.0.0",
        "endpoints": {
            "wovens": {
                "list": "GET /wovens"
            },
            "variants": {
                "list": "GET /variants",
                "detail": "GET /variants/{id}"
            },
            "stock": {
                "list": "GET /stock",
                "update_quantity": "PATCH /stock/{stock_id}/quantity"
            },
            "pantone_colors": {
                "list": "GET /pantone-colors",
                "detail": "GET /pantone-colors/detail?name={name}"
            },
            "filters": {
                "colors": "GET /filters/colors",
                "categories": "GET /filters/categories",
                "references": "GET /filters/references",
                "draws": "GET /filters/draws"
            }
        },
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    from sqlalchemy.orm import Session
    from api.database import SessionLocal
    
    try:
        db = SessionLocal()
        try:
            # Get counts for each table
            woven_count = db.query(WovenInfo).count()
            variant_count = db.query(VariantInfo).count()
            stock_count = db.query(StockInfo).count()
            pantone_count = db.query(PantoneColor).count()
            
            return {
                "status": "healthy",
                "database": "connected",
                "tables": {
                    "woven_info": woven_count,
                    "variant_info": variant_count,
                    "stock_info": stock_count,
                    "pantone_colors": pantone_count
                }
            }
        finally:
            db.close()
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
