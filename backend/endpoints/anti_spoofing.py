"""
Anti-spoofing endpoints for Face Matching API
Contains face spoofing detection logic
"""

from typing import List
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from deepface import DeepFace

from config import (
    MAX_SPOOFING_FILES, MIN_SPOOFING_FILES,
    SUPPORTED_CONTENT_TYPE
)
from utils import (
    validate_image, save_temp_image, cleanup_temp_files,
    validate_file_count, validate_content_type, generate_temp_filename,
    calculate_confidence_level
)
from schemas import AntiSpoofingResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/anti-spoofing", response_model=AntiSpoofingResponse)
async def detect_spoofing(
    files: List[UploadFile] = File(...)
):
    """Detect face spoofing/liveness in uploaded images"""
    
    # Validate number of files
    file_count_error = validate_file_count(
        len(files), MIN_SPOOFING_FILES, MAX_SPOOFING_FILES, "spoof detection"
    )
    if file_count_error:
        raise HTTPException(status_code=400, detail=file_count_error)
    
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
                generate_temp_filename("temp_spoof", i, file.filename)
            )
            temp_files.append(temp_path)
        
        # Perform spoof detection on each image
        for i, temp_path in enumerate(temp_files):
            try:
                # Use DeepFace extract_faces with anti_spoofing enabled
                face_objs = DeepFace.extract_faces(
                    img_path=temp_path,
                    anti_spoofing=True
                )
                
                # Process each detected face
                processed_faces = []
                for face_idx, face_obj in enumerate(face_objs):
                    is_real = face_obj.get("is_real", None)
                    antispoofing_score = face_obj.get("antispoofing_score", None)
                    region = face_obj.get("region", {})
                    
                    # Determine confidence level based on score
                    confidence = calculate_confidence_level(antispoofing_score)
                    
                    face_result = {
                        "face_index": face_idx,
                        "is_real": is_real,
                        "antispoofing_score": antispoofing_score,
                        "confidence": confidence,
                        "region": region,
                        "status": "real" if is_real else "spoofed" if is_real is not None else "unknown"
                    }
                    
                    processed_faces.append(face_result)
                
                results.append({
                    "image_index": i,
                    "filename": files[i].filename,
                    "faces_detected": len(processed_faces),
                    "faces": processed_faces
                })
                
            except ValueError as e:
                # Handle DeepFace ValueError for spoof detection
                if "Spoof detected" in str(e):
                    results.append({
                        "image_index": i,
                        "filename": files[i].filename,
                        "faces_detected": 0,
                        "spoof_detected": True,
                        "error": str(e)
                    })
                else:
                    raise e
                    
            except Exception as e:
                logger.error(f"Error analyzing {files[i].filename}: {e}")
                results.append({
                    "image_index": i,
                    "filename": files[i].filename,
                    "faces_detected": 0,
                    "error": str(e)
                })
        
        # Calculate summary statistics
        total_faces = sum(r.get("faces_detected", 0) for r in results)
        real_faces = sum(
            len([f for f in r.get("faces", []) if f.get("is_real") is True])
            for r in results
        )
        spoofed_faces = sum(
            len([f for f in r.get("faces", []) if f.get("is_real") is False])
            for r in results
        )
        
        # Prepare response
        response = {
            "total_images": len(files),
            "results": results,
            "summary": {
                "total_faces": total_faces,
                "real_faces": real_faces,
                "spoofed_faces": spoofed_faces,
                "detection_rate": f"{((real_faces + spoofed_faces) / max(total_faces, 1) * 100):.1f}%" if total_faces > 0 else "0%",
                "successful_analyses": len([r for r in results if "error" not in r]),
                "failed_analyses": len([r for r in results if "error" in r])
            }
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Unexpected error in anti_spoofing: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    finally:
        # Clean up temporary files
        cleanup_temp_files(temp_files)