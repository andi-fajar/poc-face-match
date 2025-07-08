"""
Face Matching API - Main Application
Refactored version with improved organization and modularity
Created by @andi-fajar & Claude.ai
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import (
    APP_TITLE, APP_VERSION, SERVER_HOST, SERVER_PORT,
    CORS_ORIGINS, CORS_CREDENTIALS, CORS_METHODS, CORS_HEADERS,
    setup_logging
)
from models import preload_models
from endpoints import (
    basic_router,
    face_comparison_router,
    face_analysis_router,
    anti_spoofing_router,
    face_embeddings_router
)

# Set up logging
logger = setup_logging()

# Create FastAPI application
app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# Include routers
app.include_router(basic_router)
app.include_router(face_comparison_router)
app.include_router(face_analysis_router)
app.include_router(anti_spoofing_router)
app.include_router(face_embeddings_router)

@app.on_event("startup")
async def startup_event():
    """FastAPI startup event to preload models"""
    logger.info("Application startup: Beginning model preloading...")
    preload_models()
    logger.info("Application startup completed.")

if __name__ == "__main__":
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)