"""
Endpoints package for Face Matching API
Contains organized API endpoint modules
"""

from .basic import router as basic_router
from .face_comparison import router as face_comparison_router
from .face_analysis import router as face_analysis_router
from .anti_spoofing import router as anti_spoofing_router

__all__ = [
    "basic_router",
    "face_comparison_router", 
    "face_analysis_router",
    "anti_spoofing_router"
]