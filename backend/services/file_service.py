"""
File handling service for Face Matching API
Contains file upload and processing business logic
"""

import logging
from typing import List, Tuple
from fastapi import UploadFile, HTTPException

from utils import (
    validate_image, save_temp_image, 
    validate_content_type, generate_temp_filename
)
from config import SUPPORTED_CONTENT_TYPE

logger = logging.getLogger(__name__)

class FileService:
    """Service class for file-related operations"""
    
    @staticmethod
    async def process_uploaded_files(
        files: List[UploadFile], 
        file_prefix: str
    ) -> List[str]:
        """
        Process uploaded files and save them temporarily
        
        Args:
            files: List of uploaded files
            file_prefix: Prefix for temporary filenames
            
        Returns:
            List of temporary file paths
            
        Raises:
            HTTPException: If file validation fails
        """
        temp_files = []
        
        try:
            for i, file in enumerate(files):
                # Validate content type
                if not validate_content_type(file.content_type, SUPPORTED_CONTENT_TYPE):
                    raise HTTPException(
                        status_code=400, 
                        detail=f"File {file.filename} is not an image"
                    )
                
                # Read file content
                content = await file.read()
                
                # Validate image content
                if not validate_image(content):
                    raise HTTPException(
                        status_code=400, 
                        detail=f"File {file.filename} is not a valid image"
                    )
                
                # Save to temporary file
                temp_path = save_temp_image(
                    content, 
                    generate_temp_filename(file_prefix, i, file.filename)
                )
                temp_files.append(temp_path)
                
        except Exception as e:
            # If an error occurs, we should clean up any files that were already created
            from utils import cleanup_temp_files
            cleanup_temp_files(temp_files)
            raise e
            
        return temp_files
    
    @staticmethod
    def validate_file_types(files: List[UploadFile]) -> List[str]:
        """
        Validate file types for a list of uploaded files
        
        Args:
            files: List of uploaded files
            
        Returns:
            List of error messages (empty if all valid)
        """
        errors = []
        
        for file in files:
            if not validate_content_type(file.content_type, SUPPORTED_CONTENT_TYPE):
                errors.append(f"File {file.filename} is not an image")
                
        return errors
    
    @staticmethod
    def get_file_info(files: List[UploadFile]) -> List[dict]:
        """
        Get basic information about uploaded files
        
        Args:
            files: List of uploaded files
            
        Returns:
            List of dictionaries with file information
        """
        file_info = []
        
        for i, file in enumerate(files):
            info = {
                "index": i,
                "filename": file.filename,
                "content_type": file.content_type,
                "size": file.size if hasattr(file, 'size') else None
            }
            file_info.append(info)
            
        return file_info