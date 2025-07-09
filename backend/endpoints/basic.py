"""
Basic endpoints for Face Matching API
Contains root, health check, and models endpoints
"""

import psutil
import os
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
    """Health check endpoint with memory usage monitoring"""
    # Get memory usage
    memory_info = psutil.virtual_memory()
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info()
    
    # Memory usage in MB
    total_memory_mb = memory_info.total / (1024 * 1024)
    available_memory_mb = memory_info.available / (1024 * 1024)
    used_memory_mb = memory_info.used / (1024 * 1024)
    process_memory_mb = process_memory.rss / (1024 * 1024)
    
    # Calculate memory usage percentage
    memory_usage_percent = (used_memory_mb / total_memory_mb) * 100
    
    # Determine health status based on memory usage
    if memory_usage_percent > 90:
        status = "critical"
    elif memory_usage_percent > 80:
        status = "warning"
    else:
        status = "healthy"
    
    return {
        "status": status,
        "memory": {
            "total_mb": round(total_memory_mb, 2),
            "used_mb": round(used_memory_mb, 2),
            "available_mb": round(available_memory_mb, 2),
            "usage_percent": round(memory_usage_percent, 2),
            "process_memory_mb": round(process_memory_mb, 2)
        }
    }

@router.get("/models", response_model=ModelsResponse)
async def get_available_models():
    """Get list of available face recognition models"""
    return {"models": AVAILABLE_MODELS}