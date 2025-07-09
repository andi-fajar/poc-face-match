"""
Model management module for Face Matching API
Provides model validation utilities
"""

import logging
from config import AVAILABLE_MODELS

logger = logging.getLogger(__name__)


def validate_model(model_name: str) -> bool:
    """
    Validate if a model name is supported
    
    Args:
        model_name: Name of the model to validate
        
    Returns:
        bool: True if model is in available models list, False otherwise
    """
    return model_name in AVAILABLE_MODELS