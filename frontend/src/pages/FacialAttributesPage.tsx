/**
 * Facial Attributes Page - React Frontend
 * Created by @andi-fajar & Claude.ai
 * 
 * A page for analyzing facial attributes using DeepFace library
 */

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import './FacialAttributesPage.css';

interface FaceResult {
  face_index: number;
  filename: string;
  region: { x: number; y: number; w: number; h: number };
  age?: number;
  gender?: {
    prediction: string;
    confidence: { [key: string]: number };
  };
  emotion?: {
    prediction: string;
    confidence: { [key: string]: number };
  };
  race?: {
    prediction: string;
    confidence: { [key: string]: number };
  };
}

interface ImageResult {
  image_index: number;
  filename: string;
  faces_detected: number;
  faces: FaceResult[];
  error?: string;
}

interface ApiResponse {
  actions_performed: string[];
  total_images: number;
  total_faces_detected: number;
  results: ImageResult[];
  summary: {
    successful_analyses: number;
    failed_analyses: number;
  };
}

const AVAILABLE_ACTIONS = [
  { key: 'age', label: 'Age Estimation', icon: '🎂' },
  { key: 'gender', label: 'Gender Detection', icon: '👤' },
  { key: 'emotion', label: 'Emotion Recognition', icon: '😊' },
  { key: 'race', label: 'Ethnicity Analysis', icon: '🌍' }
];

const FacialAttributesPage: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [selectedActions, setSelectedActions] = useState<string[]>(['age', 'gender', 'emotion', 'race']);
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

  const handleActionChange = (action: string) => {
    setSelectedActions(prev => 
      prev.includes(action) 
        ? prev.filter(a => a !== action)
        : [...prev, action]
    );
  };

  const handleSubmit = async () => {
    if (files.length < 1) {
      setError("At least 1 image is required for analysis");
      return;
    }

    if (selectedActions.length === 0) {
      setError("Please select at least one attribute to analyze");
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
      formData.append('actions', selectedActions.join(','));

      const response = await axios.post<ApiResponse>(
        '/api/analyze-attributes',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResults(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred during analysis');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return '#10B981'; // Green
    if (confidence >= 0.6) return '#F59E0B'; // Yellow
    return '#EF4444'; // Red
  };

  const renderAttributeCard = (face: FaceResult) => {
    return (
      <div className="attribute-card">
        <div className="face-info">
          <h4>Face {face.face_index + 1}</h4>
          <p className="region-info">
            Region: ({face.region.x}, {face.region.y}) {face.region.w}×{face.region.h}
          </p>
        </div>

        <div className="attributes-grid">
          {face.age && (
            <div className="attribute-item">
              <div className="attribute-header">
                <span className="icon">🎂</span>
                <span className="label">Age</span>
              </div>
              <div className="attribute-value">
                <span className="value">{Math.round(face.age)} years</span>
              </div>
            </div>
          )}

          {face.gender && (
            <div className="attribute-item">
              <div className="attribute-header">
                <span className="icon">👤</span>
                <span className="label">Gender</span>
              </div>
              <div className="attribute-value">
                <span className="value">{face.gender.prediction}</span>
                <div className="confidence-bars">
                  {Object.entries(face.gender.confidence).map(([key, value]) => (
                    <div key={key} className="confidence-bar">
                      <span className="bar-label">{key}</span>
                      <div className="bar-container">
                        <div 
                          className="bar-fill" 
                          style={{ 
                            width: `${value}%`,
                            backgroundColor: getConfidenceColor(value / 100)
                          }}
                        />
                      </div>
                      <span className="bar-value">{value.toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {face.emotion && (
            <div className="attribute-item">
              <div className="attribute-header">
                <span className="icon">😊</span>
                <span className="label">Emotion</span>
              </div>
              <div className="attribute-value">
                <span className="value">{face.emotion.prediction}</span>
                <div className="confidence-bars">
                  {Object.entries(face.emotion.confidence).map(([key, value]) => (
                    <div key={key} className="confidence-bar">
                      <span className="bar-label">{key}</span>
                      <div className="bar-container">
                        <div 
                          className="bar-fill" 
                          style={{ 
                            width: `${value}%`,
                            backgroundColor: getConfidenceColor(value / 100)
                          }}
                        />
                      </div>
                      <span className="bar-value">{value.toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {face.race && (
            <div className="attribute-item">
              <div className="attribute-header">
                <span className="icon">🌍</span>
                <span className="label">Ethnicity</span>
              </div>
              <div className="attribute-value">
                <span className="value">{face.race.prediction}</span>
                <div className="confidence-bars">
                  {Object.entries(face.race.confidence).map(([key, value]) => (
                    <div key={key} className="confidence-bar">
                      <span className="bar-label">{key.replace('_', ' ')}</span>
                      <div className="bar-container">
                        <div 
                          className="bar-fill" 
                          style={{ 
                            width: `${value}%`,
                            backgroundColor: getConfidenceColor(value / 100)
                          }}
                        />
                      </div>
                      <span className="bar-value">{value.toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="facial-attributes-page">
      <div className="page-header">
        <h1>🧠 Facial Attributes Analysis</h1>
        <p>Analyze facial attributes including age, gender, emotion, and ethnicity using AI</p>
      </div>
      
      <div className="upload-section">
        <div className="actions-selector">
          <h3>Select Attributes to Analyze:</h3>
          <div className="actions-grid">
            {AVAILABLE_ACTIONS.map(action => (
              <label key={action.key} className="action-checkbox">
                <input
                  type="checkbox"
                  checked={selectedActions.includes(action.key)}
                  onChange={() => handleActionChange(action.key)}
                />
                <span className="checkbox-content">
                  <span className="icon">{action.icon}</span>
                  <span className="label">{action.label}</span>
                </span>
              </label>
            ))}
          </div>
        </div>

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
          disabled={files.length < 1 || selectedActions.length === 0 || loading}
          className="submit-button"
        >
          {loading ? 'Analyzing...' : 'Analyze Attributes'}
        </button>
      </div>

      {results && (
        <div className="results-section">
          <h2>Analysis Results</h2>
          <div className="results-summary">
            <p><strong>Actions Performed:</strong> {results.actions_performed.join(', ')}</p>
            <p><strong>Total Images:</strong> {results.total_images}</p>
            <p><strong>Total Faces Detected:</strong> {results.total_faces_detected}</p>
            <p><strong>Successful Analyses:</strong> {results.summary.successful_analyses}</p>
            <p><strong>Failed Analyses:</strong> {results.summary.failed_analyses}</p>
          </div>
          
          <div className="image-results">
            {results.results.map((imageResult, index) => (
              <div key={index} className="image-result">
                <h3>
                  📸 {imageResult.filename}
                  {imageResult.faces_detected > 0 && (
                    <span className="face-count">({imageResult.faces_detected} face{imageResult.faces_detected > 1 ? 's' : ''})</span>
                  )}
                </h3>
                
                {imageResult.error ? (
                  <div className="error-message">
                    Error: {imageResult.error}
                  </div>
                ) : (
                  <div className="faces-grid">
                    {imageResult.faces.map((face, faceIndex) => (
                      <div key={faceIndex}>
                        {renderAttributeCard(face)}
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

export default FacialAttributesPage;