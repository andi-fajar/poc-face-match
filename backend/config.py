"""
Configuration module for Face Matching API
Contains environment variables, constants, and application settings
"""

import os
import logging

# Set legacy Keras environment variable for TensorFlow 2.16+ compatibility
os.environ["TF_USE_LEGACY_KERAS"] = "1"

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

# CORS settings
CORS_ORIGINS = ["http://localhost:3000"]  # React dev server
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# Application settings
APP_TITLE = "Face Matching API"
APP_VERSION = "1.0.0"
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# File upload settings
MAX_COMPARISON_FILES = 4
MIN_COMPARISON_FILES = 2
MAX_ANALYSIS_FILES = 10
MIN_ANALYSIS_FILES = 1
MAX_SPOOFING_FILES = 10
MIN_SPOOFING_FILES = 1

# Supported image formats
SUPPORTED_IMAGE_TYPES = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
SUPPORTED_CONTENT_TYPE = 'image/'

# Valid facial attribute actions
VALID_ACTIONS = ['age', 'gender', 'emotion', 'race']

# Logging configuration
def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add memory monitoring logs
    logger = logging.getLogger(__name__)
    
    # Log memory usage at startup
    try:
        import psutil
        memory_info = psutil.virtual_memory()
        logger.info(f"System memory: {memory_info.total / (1024**3):.2f} GB total, "
                   f"{memory_info.available / (1024**3):.2f} GB available")
        
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info()
        logger.info(f"Process memory usage: {process_memory.rss / (1024**2):.2f} MB")
        
    except ImportError:
        logger.warning("psutil not available - memory monitoring disabled")
    
    return logger