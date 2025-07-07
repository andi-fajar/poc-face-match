import os
# Set legacy Keras environment variable for TensorFlow 2.16+ compatibility
os.environ["TF_USE_LEGACY_KERAS"] = "1"

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
import tempfile
import time
from deepface import DeepFace
import cv2
import numpy as np
from PIL import Image
import io
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Face Matching API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Available models in DeepFace
AVAILABLE_MODELS = [
    "Facenet",
    "VGG-Face",
    "Facenet512", 
    "OpenFace",
    "DeepFace",
    "DeepID",
    "ArcFace",
    "Dlib",
    "SFace"
]

# Global variable to store preloaded models
preloaded_models = {}

def preload_models():
    """Preload all face recognition models to avoid first-time download latency"""
    logger.info("Starting model preloading process...")
    
    for model_name in AVAILABLE_MODELS:
        try:
            logger.info(f"Loading model: {model_name}")
            start_time = time.time()
            
            # Build and cache the model
            model = DeepFace.build_model(model_name)
            preloaded_models[model_name] = model
            
            load_time = time.time() - start_time
            logger.info(f"Successfully loaded {model_name} in {load_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            # Continue loading other models even if one fails
            continue
    
    logger.info(f"Model preloading completed. Loaded {len(preloaded_models)}/{len(AVAILABLE_MODELS)} models.")

@app.on_event("startup")
async def startup_event():
    """FastAPI startup event to preload models"""
    logger.info("Application startup: Beginning model preloading...")
    preload_models()
    logger.info("Application startup completed.")

def validate_image(file_content: bytes) -> bool:
    """Validate if the uploaded file is a valid image"""
    try:
        image = Image.open(io.BytesIO(file_content))
        image.verify()
        return True
    except Exception:
        return False

def save_temp_image(file_content: bytes, filename: str) -> str:
    """Save uploaded image to temporary file"""
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, filename)
    
    with open(temp_path, 'wb') as f:
        f.write(file_content)
    
    return temp_path

def cleanup_temp_files(file_paths: List[str]):
    """Clean up temporary files"""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.warning(f"Could not remove temp file {path}: {e}")

@app.get("/")
async def root():
    return {"message": "Face Matching API is running"}

@app.get("/models")
async def get_available_models():
    """Get list of available face recognition models"""
    return {"models": AVAILABLE_MODELS}

@app.get("/health")
async def health_check():
    """Health check endpoint with model loading status"""
    return {
        "status": "healthy",
        "total_models": len(AVAILABLE_MODELS),
        "loaded_models": len(preloaded_models),
        "loaded_model_names": list(preloaded_models.keys()),
        "missing_models": [model for model in AVAILABLE_MODELS if model not in preloaded_models]
    }

@app.post("/compare-faces")
async def compare_faces(
    files: List[UploadFile] = File(...),
    model: str = Form("Facenet")
):
    """Compare faces in uploaded images using specified model"""
    
    # Validate number of files
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 images are required for comparison")
    
    if len(files) > 4:
        raise HTTPException(status_code=400, detail="Maximum 4 images are allowed")
    
    # Validate model
    if model not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Model {model} not supported. Available models: {AVAILABLE_MODELS}")
    
    temp_files = []
    results = []
    
    try:
        # Save uploaded files temporarily
        for i, file in enumerate(files):
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not an image")
            
            content = await file.read()
            
            if not validate_image(content):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a valid image")
            
            temp_path = save_temp_image(content, f"temp_image_{i}_{file.filename}")
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)