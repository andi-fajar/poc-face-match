"""
Face embeddings endpoints for Face Matching API
Contains face embeddings extraction and comparison logic
"""

from typing import List
import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse

from config import (
    MAX_COMPARISON_FILES, MIN_COMPARISON_FILES, 
    SUPPORTED_CONTENT_TYPE, AVAILABLE_MODELS
)
from utils import (
    validate_image, save_temp_image, cleanup_temp_files,
    validate_file_count, validate_content_type, generate_temp_filename
)
from schemas import FaceEmbeddingsResponse
from services.face_service import FaceService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/extract-embeddings", response_model=FaceEmbeddingsResponse)
async def extract_embeddings(
    files: List[UploadFile] = File(...),
    model: str = Form("Facenet")
):
    """Extract face embeddings from uploaded images using specified model"""
    
    # Validate number of files
    file_count_error = validate_file_count(
        len(files), MIN_COMPARISON_FILES, MAX_COMPARISON_FILES, "embedding extraction"
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
    all_embeddings = []
    
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
                generate_temp_filename("temp_embedding", i, file.filename)
            )
            temp_files.append(temp_path)
        
        # Extract embeddings for each image
        for i, temp_path in enumerate(temp_files):
            try:
                # Use FaceService to extract embeddings
                embedding_data = FaceService.extract_face_embeddings(temp_path, model)
                
                # Process embeddings for this image
                embeddings = []
                for j, embedding_obj in enumerate(embedding_data):
                    embedding_vector = embedding_obj.get("embedding", [])
                    facial_area = embedding_obj.get("facial_area", {})
                    
                    embedding_result = {
                        "face_index": j,
                        "embedding": embedding_vector,
                        "embedding_dimensions": len(embedding_vector),
                        "region": {
                            "x": facial_area.get("x", 0),
                            "y": facial_area.get("y", 0),
                            "w": facial_area.get("w", 0),
                            "h": facial_area.get("h", 0)
                        } if facial_area else None
                    }
                    embeddings.append(embedding_result)
                    all_embeddings.append({
                        "image_index": i,
                        "face_index": j,
                        "embedding": embedding_vector,
                        "filename": files[i].filename
                    })
                
                image_result = {
                    "image_index": i,
                    "filename": files[i].filename,
                    "faces_detected": len(embedding_data),
                    "embeddings": embeddings
                }
                
                results.append(image_result)
                
            except Exception as e:
                logger.error(f"Error extracting embeddings from {files[i].filename}: {e}")
                results.append({
                    "image_index": i,
                    "filename": files[i].filename,
                    "faces_detected": 0,
                    "embeddings": None,
                    "error": str(e)
                })
        
        # Calculate pairwise comparisons if multiple embeddings exist
        comparisons = []
        if len(all_embeddings) > 1:
            try:
                for i in range(len(all_embeddings)):
                    for j in range(i + 1, len(all_embeddings)):
                        emb1 = all_embeddings[i]
                        emb2 = all_embeddings[j]
                        
                        # Calculate distances
                        cosine_dist = FaceService.calculate_embedding_distance(
                            emb1["embedding"], emb2["embedding"], "cosine"
                        )
                        euclidean_dist = FaceService.calculate_embedding_distance(
                            emb1["embedding"], emb2["embedding"], "euclidean"
                        )
                        
                        # Calculate similarity percentage (1 - cosine distance)
                        similarity_percentage = max(0, (1 - cosine_dist) * 100)
                        
                        comparison = {
                            "image1": emb1["filename"],
                            "image2": emb2["filename"],
                            "face1_index": emb1["face_index"],
                            "face2_index": emb2["face_index"],
                            "cosine_distance": cosine_dist,
                            "euclidean_distance": euclidean_dist,
                            "similarity_percentage": similarity_percentage
                        }
                        
                        comparisons.append(comparison)
                        
            except Exception as e:
                logger.error(f"Error calculating embedding comparisons: {e}")
        
        # Calculate summary
        summary = FaceService.calculate_embeddings_summary(results)
        
        # Prepare response
        response = {
            "model_used": model,
            "total_images": len(files),
            "total_embeddings": summary["total_embeddings"],
            "results": results,
            "comparisons": comparisons if comparisons else None,
            "summary": summary
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    finally:
        # Clean up temporary files
        cleanup_temp_files(temp_files)