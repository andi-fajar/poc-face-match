"""
Face comparison endpoints for Face Matching API
Contains face verification and comparison logic
"""

from typing import List
import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from deepface import DeepFace

from config import (
    MAX_COMPARISON_FILES, MIN_COMPARISON_FILES, 
    SUPPORTED_CONTENT_TYPE, AVAILABLE_MODELS
)
from utils import (
    validate_image, save_temp_image, cleanup_temp_files,
    validate_file_count, validate_content_type, generate_temp_filename
)
from schemas import FaceComparisonResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/compare-faces", response_model=FaceComparisonResponse)
async def compare_faces(
    files: List[UploadFile] = File(...),
    model: str = Form("Facenet")
):
    """Compare faces in uploaded images using specified model"""
    
    # Validate number of files
    file_count_error = validate_file_count(
        len(files), MIN_COMPARISON_FILES, MAX_COMPARISON_FILES, "comparison"
    )
    if file_count_error:
        raise HTTPException(status_code=400, detail=file_count_error)
    
    # Validate model
    if model not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=400, 
            detail=f"Model {model} not supported. Available models: {AVAILABLE_MODELS}"
        )
    
    temp_files = []
    results = []
    
    try:
        # Save uploaded files temporarily
        for i, file in enumerate(files):
            if not validate_content_type(file.content_type, SUPPORTED_CONTENT_TYPE):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} is not an image"
                )
            
            content = await file.read()
            
            if not validate_image(content):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} is not a valid image"
                )
            
            temp_path = save_temp_image(
                content, 
                generate_temp_filename("temp_image", i, file.filename)
            )
            temp_files.append(temp_path)
        
        # Perform face comparisons
        comparisons = []
        
        for i in range(len(temp_files)):
            for j in range(i + 1, len(temp_files)):
                try:
                    # Use DeepFace to compare faces
                    result = DeepFace.verify(
                        img1_path=temp_files[i],
                        img2_path=temp_files[j],
                        model_name=model,
                        enforce_detection=False  # Allow comparison even if face detection fails
                    )
                    
                    comparison = {
                        "image1": files[i].filename,
                        "image2": files[j].filename,
                        "verified": result["verified"],
                        "distance": result["distance"],
                        "threshold": result["threshold"],
                        "model": result.get("model", model),
                        "similarity_metric": result.get("similarity_metric", "cosine"),
                        "detector_backend": result.get("detector_backend", "opencv"),
                        "facial_areas": result.get("facial_areas", {}),
                        "time": result.get("time", 0)
                    }
                    
                    comparisons.append(comparison)
                    
                except Exception as e:
                    logger.error(f"Error comparing {files[i].filename} and {files[j].filename}: {e}")
                    comparisons.append({
                        "image1": files[i].filename,
                        "image2": files[j].filename,
                        "error": str(e),
                        "model": model
                    })
        
        # Prepare response
        response = {
            "model_used": model,
            "total_images": len(files),
            "total_comparisons": len(comparisons),
            "comparisons": comparisons,
            "summary": {
                "matches": len([c for c in comparisons if c.get("verified", False)]),
                "no_matches": len([c for c in comparisons if c.get("verified", False) == False and "error" not in c]),
                "errors": len([c for c in comparisons if "error" in c])
            }
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    finally:
        # Clean up temporary files
        cleanup_temp_files(temp_files)