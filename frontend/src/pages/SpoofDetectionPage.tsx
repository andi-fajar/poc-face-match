/**
 * Spoof Detection Page - React Frontend
 * Created by @andi-fajar & Claude.ai
 * 
 * A proof-of-concept application for face anti-spoofing using DeepFace library
 */

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import './SpoofDetectionPage.css';

interface FaceResult {
  face_index: number;
  is_real: boolean | null;
  antispoofing_score: number | null;
  confidence: string;
  region: {
    x?: number;
    y?: number;
    w?: number;
    h?: number;
  };
  status: string;
}

interface ImageResult {
  image_index: number;
  filename: string;
  faces_detected: number;
  faces?: FaceResult[];
  spoof_detected?: boolean;
  error?: string;
}

interface ApiResponse {
  total_images: number;
  results: ImageResult[];
  summary: {
    total_faces: number;
    real_faces: number;
    spoofed_faces: number;
    detection_rate: string;
    successful_analyses: number;
    failed_analyses: number;
  };
}

const SpoofDetectionPage: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [results, setResults] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length + files.length > 10) {
      setError("Maximum 10 images allowed");
      return;
    }
    
    const newFiles = acceptedFiles.slice(0, 10 - files.length);
    setFiles(prev => [...prev, ...newFiles]);
    setError(null);
  }, [files.length]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    },
    maxFiles: 10,
    multiple: true
  });

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (files.length < 1) {
      setError("At least 1 image is required for spoof detection");
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

      const response = await axios.post<ApiResponse>(
        '/api/anti-spoofing',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResults(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred during spoof detection');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'real': return '✅';
      case 'spoofed': return '❌';
      default: return '❓';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'real': return '#4CAF50';
      case 'spoofed': return '#f44336';
      default: return '#ff9800';
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high': return '#4CAF50';
      case 'medium': return '#ff9800';
      case 'low': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  return (
    <div className="spoof-detection-page">
      <div className="page-header">
        <h1>🔒 Face Anti-Spoofing</h1>
        <p>Detect real faces vs fake/spoofed images for enhanced security and fraud prevention</p>
      </div>
      
      <div className="upload-section">
        <div 
          {...getRootProps()} 
          className={`dropzone ${isDragActive ? 'active' : ''}`}
        >
          <input {...getInputProps()} />
          {isDragActive ? (
            <p>Drop the images here...</p>
          ) : (
            <p>Drag & drop images here, or click to select files (max 10)</p>
          )}
        </div>

        {files.length > 0 && (
          <div className="file-preview">
            <h3>Selected Images ({files.length}/10):</h3>
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
          disabled={files.length < 1 || loading}
          className="submit-button"
        >
          {loading ? 'Analyzing...' : 'Detect Spoofing'}
        </button>
      </div>

      {results && (
        <div className="results-section">
          <h2>Spoof Detection Results</h2>
          <div className="results-summary">
            <div className="summary-grid">
              <div className="summary-card">
                <h3>📊 Total Analysis</h3>
                <p><strong>Images Analyzed:</strong> {results.total_images}</p>
                <p><strong>Faces Detected:</strong> {results.summary.total_faces}</p>
                <p><strong>Detection Rate:</strong> {results.summary.detection_rate}</p>
              </div>
              <div className="summary-card">
                <h3>✅ Real Faces</h3>
                <p className="real-count">{results.summary.real_faces}</p>
                <p>Authentic faces detected</p>
              </div>
              <div className="summary-card">
                <h3>❌ Spoofed Faces</h3>
                <p className="spoofed-count">{results.summary.spoofed_faces}</p>
                <p>Fake faces detected</p>
              </div>
              <div className="summary-card">
                <h3>📈 Success Rate</h3>
                <p><strong>Successful:</strong> {results.summary.successful_analyses}</p>
                <p><strong>Failed:</strong> {results.summary.failed_analyses}</p>
              </div>
            </div>
          </div>
          
          <div className="detailed-results">
            <h3>Detailed Analysis:</h3>
            {results.results.map((result, index) => (
              <div key={index} className="result-item">
                <h4>📷 {result.filename}</h4>
                {result.error ? (
                  <div className="error-result">
                    <p className="error">Error: {result.error}</p>
                    {result.spoof_detected && (
                      <p className="spoof-warning">⚠️ Spoof detected by DeepFace security check</p>
                    )}
                  </div>
                ) : result.faces_detected === 0 ? (
                  <p className="no-faces">No faces detected in this image</p>
                ) : (
                  <div className="faces-grid">
                    {result.faces?.map((face, faceIndex) => (
                      <div 
                        key={faceIndex} 
                        className="face-card"
                        style={{ borderLeft: `4px solid ${getStatusColor(face.status)}` }}
                      >
                        <div className="face-header">
                          <span className="face-status">
                            {getStatusIcon(face.status)} Face {face.face_index + 1}
                          </span>
                          <span 
                            className="confidence-badge"
                            style={{ backgroundColor: getConfidenceColor(face.confidence) }}
                          >
                            {face.confidence}
                          </span>
                        </div>
                        
                        <div className="face-details">
                          <p><strong>Status:</strong> {face.status.charAt(0).toUpperCase() + face.status.slice(1)}</p>
                          {face.antispoofing_score !== null && (
                            <div className="score-container">
                              <p><strong>Anti-spoofing Score:</strong> {(face.antispoofing_score * 100).toFixed(1)}%</p>
                              <div className="score-bar">
                                <div 
                                  className="score-fill"
                                  style={{ 
                                    width: `${face.antispoofing_score * 100}%`,
                                    backgroundColor: getConfidenceColor(face.confidence)
                                  }}
                                ></div>
                              </div>
                            </div>
                          )}
                          
                          {face.region && Object.keys(face.region).length > 0 && (
                            <details className="face-region">
                              <summary><strong>Face Region</strong></summary>
                              <p>Position: ({face.region.x}, {face.region.y})</p>
                              <p>Size: {face.region.w}×{face.region.h}</p>
                            </details>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SpoofDetectionPage;