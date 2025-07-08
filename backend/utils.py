"""
Utility functions for Face Matching API
Contains file handling, validation, and common helper functions
"""

import os
import tempfile
import logging
from typing import List
from PIL import Image
import io

logger = logging.getLogger(__name__)

def validate_image(file_content: bytes) -> bool:
    """
    Validate if the uploaded file is a valid image
    
    Args:
        file_content: Bytes content of the uploaded file
        
    Returns:
        bool: True if valid image, False otherwise
    """
    try:
        image = Image.open(io.BytesIO(file_content))
        image.verify()
        return True
    except Exception:
        return False

def save_temp_image(file_content: bytes, filename: str) -> str:
    """
    Save uploaded image to temporary file
    
    Args:
        file_content: Bytes content of the image
        filename: Name for the temporary file
        
    Returns:
        str: Path to the saved temporary file
    """
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, filename)
    
    with open(temp_path, 'wb') as f:
        f.write(file_content)
    
    return temp_path

def cleanup_temp_files(file_paths: List[str]) -> None:
    """
    Clean up temporary files
    
    Args:
        file_paths: List of file paths to remove
    """
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.debug(f"Removed temporary file: {path}")
        except Exception as e:
            logger.warning(f"Could not remove temp file {path}: {e}")

def validate_file_count(file_count: int, min_files: int, max_files: int, operation_name: str) -> str:
    """
    Validate the number of uploaded files for a specific operation
    
    Args:
        file_count: Number of files uploaded
        min_files: Minimum required files
        max_files: Maximum allowed files
        operation_name: Name of the operation for error messages
        
    Returns:
        str: Error message if validation fails, empty string if valid
    """
    if file_count < min_files:
        return f"At least {min_files} image{'s' if min_files > 1 else ''} {'are' if min_files > 1 else 'is'} required for {operation_name}"
    
    if file_count > max_files:
        return f"Maximum {max_files} images are allowed for {operation_name}"
    
    return ""

def validate_content_type(content_type: str, supported_type: str) -> bool:
    """
    Validate if the content type is supported
    
    Args:
        content_type: MIME type of the uploaded file
        supported_type: Required content type prefix
        
    Returns:
        bool: True if content type is supported, False otherwise
    """
    return content_type.startswith(supported_type)

def generate_temp_filename(prefix: str, index: int, original_filename: str) -> str:
    """
    Generate a temporary filename with prefix and index
    
    Args:
        prefix: Prefix for the temporary file
        index: Index number for the file
        original_filename: Original filename from upload
        
    Returns:
        str: Generated temporary filename
    """
    return f"{prefix}_{index}_{original_filename}"

def calculate_confidence_level(score: float) -> str:
    """
    Calculate confidence level based on a numerical score
    
    Args:
        score: Numerical confidence score (0.0 to 1.0)
        
    Returns:
        str: Confidence level ('high', 'medium', 'low', 'unknown')
    """
    if score is None:
        return "unknown"
    
    if score >= 0.8:
        return "high"
    elif score >= 0.6:
        return "medium"
    else:
        return "low"