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
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)