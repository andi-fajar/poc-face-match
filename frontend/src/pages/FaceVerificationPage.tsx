/**
 * Face Verification Page - React Frontend
 * Created by @andi-fajar & Claude.ai
 * 
 * A fun proof-of-concept application for face matching using DeepFace library
 */

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import './FaceVerificationPage.css';

interface ComparisonResult {
  image1: string;
  image2: string;
  verified: boolean;
  distance: number;
  threshold: number;
  model: string;
  similarity_metric: string;
  detector_backend: string;
  facial_areas: {
    img1?: { x: number; y: number; w: number; h: number };
    img2?: { x: number; y: number; w: number; h: number };
  };
  time: number;
  error?: string;
}

interface ApiResponse {
  model_used: string;
  total_images: number;
  total_comparisons: number;
  comparisons: ComparisonResult[];
  summary: {
    matches: number;
    no_matches: number;
    errors: number;
  };
}

const AVAILABLE_MODELS = [
  "Facenet",
  "VGG-Face",
  "Facenet512", 
  "OpenFace",
  "DeepFace",
  "DeepID",
  "ArcFace",
  "Dlib",
  "SFace"
];

const FaceVerificationPage: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("Facenet");
  const [results, setResults] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length + files.length > 4) {
      setError("Maximum 4 images allowed");
      return;
    }
    
    const newFiles = acceptedFiles.slice(0, 4 - files.length);
    setFiles(prev => [...prev, ...newFiles]);
    setError(null);
  }, [files.length]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    },
    maxFiles: 4,
    multiple: true
  });

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (files.length < 2) {
      setError("At least 2 images are required for comparison");
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });
      formData.append('model', selectedModel);

      const response = await axios.post<ApiResponse>(
        '/api/compare-faces',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResults(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred during comparison');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="face-verification-page">
      <div className="page-header">
        <h1>🔍 Face Verification</h1>
        <p>Compare faces to verify if they belong to the same person using state-of-the-art AI models</p>
      </div>
      
      <div className="upload-section">
        <div className="model-selector">
          <label htmlFor="model-select">Select Face Recognition Model:</label>
          <select 
            id="model-select"
            value={selectedModel} 
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            {AVAILABLE_MODELS.map(model => (
              <option key={model} value={model}>{model}</option>
            ))}
          </select>
        </div>

        <div 
          {...getRootProps()} 
          className={`dropzone ${isDragActive ? 'active' : ''}`}
        >
          <input {...getInputProps()} />
          {isDragActive ? (
            <p>Drop the images here...</p>
          ) : (
            <p>Drag & drop images here, or click to select files (max 4)</p>
          )}
        </div>

        {files.length > 0 && (
          <div className="file-preview">
            <h3>Selected Images ({files.length}/4):</h3>
            <div className="file-list">
              {files.map((file, index) => (
                <div key={index} className="file-item">
                  <img 
                    src={URL.createObjectURL(file)} 
                    alt={`Preview ${index}`}
                    className="preview-image"
                  />
                  <div className="file-info">
                    <p>{file.name}</p>
                    <button onClick={() => removeFile(index)}>Remove</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <button 
          onClick={handleSubmit} 
          disabled={files.length < 2 || loading}
          className="submit-button"
        >
          {loading ? 'Processing...' : 'Compare Faces'}
        </button>
      </div>

      {results && (
        <div className="results-section">
          <h2>Results</h2>
          <div className="results-summary">
            <p><strong>Model Used:</strong> {results.model_used}</p>
            <p><strong>Total Images:</strong> {results.total_images}</p>
            <p><strong>Total Comparisons:</strong> {results.total_comparisons}</p>
            <p><strong>Matches:</strong> {results.summary.matches}</p>
            <p><strong>No Matches:</strong> {results.summary.no_matches}</p>
            <p><strong>Errors:</strong> {results.summary.errors}</p>
          </div>
          
          <div className="comparisons">
            <h3>Detailed Comparisons:</h3>
            {results.comparisons.map((comp, index) => (
              <div key={index} className={`comparison-item ${comp.verified ? 'match' : 'no-match'}`}>
                <h4>{comp.image1} vs {comp.image2}</h4>
                {comp.error ? (
                  <p className="error">Error: {comp.error}</p>
                ) : (
                  <>
                    <p><strong>Match:</strong> {comp.verified ? 'Yes' : 'No'}</p>
                    <p><strong>Distance:</strong> {comp.distance.toFixed(4)}</p>
                    <p><strong>Threshold:</strong> {comp.threshold.toFixed(4)}</p>
                    <p><strong>Similarity Metric:</strong> {comp.similarity_metric}</p>
                    <p><strong>Detector Backend:</strong> {comp.detector_backend}</p>
                    <p><strong>Processing Time:</strong> {comp.time.toFixed(3)}s</p>
                    {comp.facial_areas.img1 && comp.facial_areas.img2 && (
                      <details>
                        <summary><strong>Facial Areas</strong></summary>
                        <p>Image 1: ({comp.facial_areas.img1.x}, {comp.facial_areas.img1.y}) 
                           {comp.facial_areas.img1.w}×{comp.facial_areas.img1.h}</p>
                        <p>Image 2: ({comp.facial_areas.img2.x}, {comp.facial_areas.img2.y}) 
                           {comp.facial_areas.img2.w}×{comp.facial_areas.img2.h}</p>
                      </details>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FaceVerificationPage;