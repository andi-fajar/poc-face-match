"""
Basic endpoints for Face Matching API
Contains root, health check, and models endpoints
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from config import AVAILABLE_MODELS
from schemas import BasicResponse, HealthResponse, ModelsResponse

router = APIRouter()

@router.get("/", response_model=BasicResponse)
async def root():
    """Root endpoint returning API status"""
    return {"message": "Face Matching API is running"}

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy"
    }

@router.get("/models", response_model=ModelsResponse)
async def get_available_models():
    """Get list of available face recognition models"""
    return {"models": AVAILABLE_MODELS}