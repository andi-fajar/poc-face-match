"""
Face analysis endpoints for Face Matching API
Contains facial attributes analysis logic
"""

from typing import List
import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from deepface import DeepFace

from config import (
    MAX_ANALYSIS_FILES, MIN_ANALYSIS_FILES,
    SUPPORTED_CONTENT_TYPE, VALID_ACTIONS
)
from utils import (
    validate_image, save_temp_image, cleanup_temp_files,
    validate_file_count, validate_content_type, generate_temp_filename
)
from schemas import FacialAttributesResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze-attributes", response_model=FacialAttributesResponse)
async def analyze_attributes(
    files: List[UploadFile] = File(...),
    actions: str = Form("age,gender,emotion,race")
):
    """Analyze facial attributes in uploaded images"""
    
    # Validate number of files
    file_count_error = validate_file_count(
        len(files), MIN_ANALYSIS_FILES, MAX_ANALYSIS_FILES, "analysis"
    )
    if file_count_error:
        raise HTTPException(status_code=400, detail=file_count_error)
    
    # Parse actions - support single action to reduce memory usage
    action_list = [action.strip() for action in actions.split(',')]
    
    # Enforce single action limit for memory optimization
    if len(action_list) > 1:
        raise HTTPException(
            status_code=400,
            detail="Only one attribute can be analyzed per request to reduce memory usage. Please select a single attribute."
        )
    
    for action in action_list:
        if action not in VALID_ACTIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid action: {action}. Valid actions: {VALID_ACTIONS}"
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
                generate_temp_filename("temp_analyze", i, file.filename)
            )
            temp_files.append(temp_path)
        
        # Analyze each image
        for i, temp_path in enumerate(temp_files):
            try:
                # Use DeepFace to analyze facial attributes
                analysis = DeepFace.analyze(
                    img_path=temp_path,
                    actions=action_list,
                    enforce_detection=False  # Allow analysis even if face detection fails
                )
                
                # Handle both single face and multiple faces results
                if isinstance(analysis, list):
                    face_results = analysis
                else:
                    face_results = [analysis]
                
                # Process each detected face
                processed_faces = []
                for face_idx, face_data in enumerate(face_results):
                    face_result = {
                        "face_index": face_idx,
                        "filename": files[i].filename,
                        "region": face_data.get("region", {}),
                    }
                    
                    # Add requested attributes
                    if 'age' in action_list:
                        face_result["age"] = face_data.get("age", None)
                    
                    if 'gender' in action_list:
                        gender_data = face_data.get("gender", {})
                        face_result["gender"] = {
                            "prediction": max(gender_data.items(), key=lambda x: x[1])[0] if gender_data else None,
                            "confidence": gender_data
                        }
                    
                    if 'emotion' in action_list:
                        emotion_data = face_data.get("emotion", {})
                        face_result["emotion"] = {
                            "prediction": max(emotion_data.items(), key=lambda x: x[1])[0] if emotion_data else None,
                            "confidence": emotion_data
                        }
                    
                    if 'race' in action_list:
                        race_data = face_data.get("race", {})
                        face_result["race"] = {
                            "prediction": max(race_data.items(), key=lambda x: x[1])[0] if race_data else None,
                            "confidence": race_data
                        }
                    
                    processed_faces.append(face_result)
                
                results.append({
                    "image_index": i,
                    "filename": files[i].filename,
                    "faces_detected": len(processed_faces),
                    "faces": processed_faces
                })
                
            except Exception as e:
                logger.error(f"Error analyzing {files[i].filename}: {e}")
                results.append({
                    "image_index": i,
                    "filename": files[i].filename,
                    "error": str(e)
                })
        
        # Prepare response
        response = {
            "actions_performed": action_list,
            "total_images": len(files),
            "total_faces_detected": sum(r.get("faces_detected", 0) for r in results),
            "results": results,
            "summary": {
                "successful_analyses": len([r for r in results if "error" not in r]),
                "failed_analyses": len([r for r in results if "error" in r])
            }
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Unexpected error in analyze_attributes: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    finally:
        # Clean up temporary files
        cleanup_temp_files(temp_files)