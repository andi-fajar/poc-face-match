"""
Pydantic schemas for Face Matching API
Contains request and response models for validation and documentation
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel

# Common Models
class FacialArea(BaseModel):
    x: int
    y: int
    w: int
    h: int

class BaseResponse(BaseModel):
    total_images: int

# Face Comparison Models
class FacialAreas(BaseModel):
    img1: Optional[FacialArea] = None
    img2: Optional[FacialArea] = None

class ComparisonResult(BaseModel):
    image1: str
    image2: str
    verified: Optional[bool] = None
    distance: Optional[float] = None
    threshold: Optional[float] = None
    model: str
    similarity_metric: Optional[str] = None
    detector_backend: Optional[str] = None
    facial_areas: Optional[FacialAreas] = None
    time: Optional[float] = None
    error: Optional[str] = None

class ComparisonSummary(BaseModel):
    matches: int
    no_matches: int
    errors: int

class FaceComparisonResponse(BaseResponse):
    model_used: str
    total_comparisons: int
    comparisons: List[ComparisonResult]
    summary: ComparisonSummary

# Facial Attributes Models
class GenderPrediction(BaseModel):
    prediction: Optional[str] = None
    confidence: Dict[str, float]

class EmotionPrediction(BaseModel):
    prediction: Optional[str] = None
    confidence: Dict[str, float]

class RacePrediction(BaseModel):
    prediction: Optional[str] = None
    confidence: Dict[str, float]

class FaceAttributes(BaseModel):
    face_index: int
    filename: str
    region: Optional[FacialArea] = None
    age: Optional[int] = None
    gender: Optional[GenderPrediction] = None
    emotion: Optional[EmotionPrediction] = None
    race: Optional[RacePrediction] = None

class AttributesImageResult(BaseModel):
    image_index: int
    filename: str
    faces_detected: int
    faces: Optional[List[FaceAttributes]] = None
    error: Optional[str] = None

class AttributesSummary(BaseModel):
    successful_analyses: int
    failed_analyses: int

class FacialAttributesResponse(BaseResponse):
    actions_performed: List[str]
    total_faces_detected: int
    results: List[AttributesImageResult]
    summary: AttributesSummary

# Anti-Spoofing Models
class SpoofingFaceResult(BaseModel):
    face_index: int
    is_real: Optional[bool] = None
    antispoofing_score: Optional[float] = None
    confidence: str
    region: Optional[FacialArea] = None
    status: str

class SpoofingImageResult(BaseModel):
    image_index: int
    filename: str
    faces_detected: int
    faces: Optional[List[SpoofingFaceResult]] = None
    spoof_detected: Optional[bool] = None
    error: Optional[str] = None

class SpoofingSummary(BaseModel):
    total_faces: int
    real_faces: int
    spoofed_faces: int
    detection_rate: str
    successful_analyses: int
    failed_analyses: int

class AntiSpoofingResponse(BaseResponse):
    results: List[SpoofingImageResult]
    summary: SpoofingSummary

# Health Check Models
class HealthResponse(BaseModel):
    status: str

# Models List Response
class ModelsResponse(BaseModel):
    models: List[str]

# Face Embeddings Models
class EmbeddingResult(BaseModel):
    face_index: int
    embedding: List[float]
    embedding_dimensions: int
    region: Optional[FacialArea] = None

class EmbeddingImageResult(BaseModel):
    image_index: int
    filename: str
    faces_detected: int
    embeddings: Optional[List[EmbeddingResult]] = None
    error: Optional[str] = None

class EmbeddingComparison(BaseModel):
    image1: str
    image2: str
    face1_index: int
    face2_index: int
    cosine_distance: float
    euclidean_distance: float
    similarity_percentage: float

class EmbeddingsSummary(BaseModel):
    total_faces: int
    total_embeddings: int
    embedding_dimensions: int
    successful_extractions: int
    failed_extractions: int
    extraction_rate: str

class FaceEmbeddingsResponse(BaseResponse):
    model_used: str
    total_embeddings: int
    results: List[EmbeddingImageResult]
    comparisons: Optional[List[EmbeddingComparison]] = None
    summary: EmbeddingsSummary

# Basic Response Models
class BasicResponse(BaseModel):
    message: str