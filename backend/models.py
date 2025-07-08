"""
Model management module for Face Matching API
Handles DeepFace model preloading and management
"""

import time
import logging
from typing import Dict, Any
from deepface import DeepFace
from config import AVAILABLE_MODELS

logger = logging.getLogger(__name__)

# Global variable to store preloaded models
preloaded_models: Dict[str, Any] = {}

def preload_models() -> None:
    """
    Preload all face recognition models to avoid first-time download latency
    
    This function iterates through all available models and preloads them
    into memory. Failed model loads are logged but don't stop the process.
    """
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

def get_loaded_models() -> Dict[str, Any]:
    """
    Get the dictionary of preloaded models
    
    Returns:
        Dict[str, Any]: Dictionary of model names to model objects
    """
    return preloaded_models

def get_model_status() -> Dict[str, Any]:
    """
    Get the current status of model loading
    
    Returns:
        Dict containing model loading statistics
    """
    loaded_model_names = list(preloaded_models.keys())
    missing_models = [model for model in AVAILABLE_MODELS if model not in preloaded_models]
    
    return {
        "total_models": len(AVAILABLE_MODELS),
        "loaded_models": len(preloaded_models),
        "loaded_model_names": loaded_model_names,
        "missing_models": missing_models
    }

def is_model_available(model_name: str) -> bool:
    """
    Check if a specific model is available in the preloaded models
    
    Args:
        model_name: Name of the model to check
        
    Returns:
        bool: True if model is available, False otherwise
    """
    return model_name in preloaded_models

def validate_model(model_name: str) -> bool:
    """
    Validate if a model name is supported
    
    Args:
        model_name: Name of the model to validate
        
    Returns:
        bool: True if model is in available models list, False otherwise
    """
    return model_name in AVAILABLE_MODELS