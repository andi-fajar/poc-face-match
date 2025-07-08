"""
Face processing service for Face Matching API
Contains core face analysis business logic
"""

import logging
from typing import List, Dict, Any, Optional
from deepface import DeepFace

logger = logging.getLogger(__name__)

class FaceService:
    """Service class for face-related operations"""
    
    @staticmethod
    def verify_faces(img1_path: str, img2_path: str, model_name: str) -> Dict[str, Any]:
        """
        Verify if two face images belong to the same person
        
        Args:
            img1_path: Path to first image
            img2_path: Path to second image
            model_name: Name of the face recognition model to use
            
        Returns:
            Dict containing verification results
        """
        try:
            result = DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                model_name=model_name,
                enforce_detection=False
            )
            return result
        except Exception as e:
            logger.error(f"Error in face verification: {e}")
            raise
    
    @staticmethod
    def analyze_face_attributes(img_path: str, actions: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze facial attributes in an image
        
        Args:
            img_path: Path to the image
            actions: List of attributes to analyze
            
        Returns:
            List of dictionaries containing analysis results for each face
        """
        try:
            analysis = DeepFace.analyze(
                img_path=img_path,
                actions=actions,
                enforce_detection=False
            )
            
            # Ensure we always return a list
            if isinstance(analysis, list):
                return analysis
            else:
                return [analysis]
                
        except Exception as e:
            logger.error(f"Error in face attribute analysis: {e}")
            raise
    
    @staticmethod
    def detect_spoofing(img_path: str) -> List[Dict[str, Any]]:
        """
        Detect face spoofing in an image
        
        Args:
            img_path: Path to the image
            
        Returns:
            List of dictionaries containing face objects with spoofing information
        """
        try:
            face_objs = DeepFace.extract_faces(
                img_path=img_path,
                anti_spoofing=True
            )
            return face_objs
        except Exception as e:
            logger.error(f"Error in spoofing detection: {e}")
            raise
    
    @staticmethod
    def process_gender_data(gender_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Process gender prediction data
        
        Args:
            gender_data: Raw gender data from DeepFace
            
        Returns:
            Processed gender prediction with top prediction and confidence
        """
        if not gender_data:
            return {"prediction": None, "confidence": {}}
        
        prediction = max(gender_data.items(), key=lambda x: x[1])[0]
        return {
            "prediction": prediction,
            "confidence": gender_data
        }
    
    @staticmethod
    def process_emotion_data(emotion_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Process emotion prediction data
        
        Args:
            emotion_data: Raw emotion data from DeepFace
            
        Returns:
            Processed emotion prediction with top prediction and confidence
        """
        if not emotion_data:
            return {"prediction": None, "confidence": {}}
        
        prediction = max(emotion_data.items(), key=lambda x: x[1])[0]
        return {
            "prediction": prediction,
            "confidence": emotion_data
        }
    
    @staticmethod
    def process_race_data(race_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Process race prediction data
        
        Args:
            race_data: Raw race data from DeepFace
            
        Returns:
            Processed race prediction with top prediction and confidence
        """
        if not race_data:
            return {"prediction": None, "confidence": {}}
        
        prediction = max(race_data.items(), key=lambda x: x[1])[0]
        return {
            "prediction": prediction,
            "confidence": race_data
        }
    
    @staticmethod
    def calculate_comparison_summary(comparisons: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Calculate summary statistics for face comparisons
        
        Args:
            comparisons: List of comparison results
            
        Returns:
            Dictionary with match, no-match, and error counts
        """
        matches = len([c for c in comparisons if c.get("verified", False)])
        no_matches = len([c for c in comparisons if c.get("verified", False) == False and "error" not in c])
        errors = len([c for c in comparisons if "error" in c])
        
        return {
            "matches": matches,
            "no_matches": no_matches,
            "errors": errors
        }
    
    @staticmethod
    def calculate_spoofing_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary statistics for spoofing detection
        
        Args:
            results: List of spoofing detection results
            
        Returns:
            Dictionary with spoofing detection statistics
        """
        total_faces = sum(r.get("faces_detected", 0) for r in results)
        real_faces = sum(
            len([f for f in r.get("faces", []) if f.get("is_real") is True])
            for r in results
        )
        spoofed_faces = sum(
            len([f for f in r.get("faces", []) if f.get("is_real") is False])
            for r in results
        )
        
        detection_rate = f"{((real_faces + spoofed_faces) / max(total_faces, 1) * 100):.1f}%" if total_faces > 0 else "0%"
        
        return {
            "total_faces": total_faces,
            "real_faces": real_faces,
            "spoofed_faces": spoofed_faces,
            "detection_rate": detection_rate,
            "successful_analyses": len([r for r in results if "error" not in r]),
            "failed_analyses": len([r for r in results if "error" in r])
        }
    
    @staticmethod
    def extract_face_embeddings(img_path: str, model_name: str) -> List[Dict[str, Any]]:
        """
        Extract face embeddings from an image
        
        Args:
            img_path: Path to the image
            model_name: Name of the face recognition model to use
            
        Returns:
            List of dictionaries containing embedding vectors and facial areas
        """
        try:
            embeddings = DeepFace.represent(
                img_path=img_path,
                model_name=model_name,
                enforce_detection=False
            )
            
            # Ensure we always return a list
            if isinstance(embeddings, list):
                return embeddings
            else:
                return [embeddings]
                
        except Exception as e:
            logger.error(f"Error in face embedding extraction: {e}")
            raise
    
    @staticmethod
    def calculate_embedding_distance(embedding1: List[float], embedding2: List[float], metric: str = "cosine") -> float:
        """
        Calculate distance between two face embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            metric: Distance metric to use (cosine, euclidean)
            
        Returns:
            Distance value between the embeddings
        """
        try:
            import numpy as np
            from scipy.spatial.distance import cosine, euclidean
            
            if len(embedding1) != len(embedding2):
                raise ValueError("Embeddings must have the same dimensions")
            
            if metric == "cosine":
                return float(cosine(embedding1, embedding2))
            elif metric == "euclidean":
                return float(euclidean(embedding1, embedding2))
            else:
                raise ValueError(f"Unsupported distance metric: {metric}")
                
        except Exception as e:
            logger.error(f"Error in embedding distance calculation: {e}")
            raise
    
    @staticmethod
    def calculate_embeddings_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary statistics for face embeddings extraction
        
        Args:
            results: List of embedding extraction results
            
        Returns:
            Dictionary with embedding extraction statistics
        """
        total_faces = sum(r.get("faces_detected", 0) for r in results)
        total_embeddings = sum(len(r.get("embeddings", [])) for r in results)
        
        successful_extractions = len([r for r in results if "error" not in r])
        failed_extractions = len([r for r in results if "error" in r])
        
        # Get embedding dimensions from first successful result
        embedding_dimensions = 0
        for result in results:
            if "error" not in result and result.get("embeddings"):
                first_embedding = result["embeddings"][0]
                if first_embedding.get("embedding"):
                    embedding_dimensions = len(first_embedding["embedding"])
                    break
        
        return {
            "total_faces": total_faces,
            "total_embeddings": total_embeddings,
            "embedding_dimensions": embedding_dimensions,
            "successful_extractions": successful_extractions,
            "failed_extractions": failed_extractions,
            "extraction_rate": f"{(successful_extractions / max(len(results), 1) * 100):.1f}%" if len(results) > 0 else "0%"
        }