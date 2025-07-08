/**
 * Face Embeddings Page - React Frontend
 * Created by @andi-fajar & Claude.ai
 * 
 * Extract and visualize face embeddings for advanced analysis and clustering
 */

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import './FaceEmbeddingsPage.css';

interface EmbeddingResult {
  face_index: number;
  embedding: number[];
  embedding_dimensions: number;
  region?: {
    x: number;
    y: number;
    w: number;
    h: number;
  };
}

interface EmbeddingImageResult {
  image_index: number;
  filename: string;
  faces_detected: number;
  embeddings?: EmbeddingResult[];
  error?: string;
}

interface EmbeddingComparison {
  image1: string;
  image2: string;
  face1_index: number;
  face2_index: number;
  cosine_distance: number;
  euclidean_distance: number;
  similarity_percentage: number;
}

interface EmbeddingsSummary {
  total_faces: number;
  total_embeddings: number;
  embedding_dimensions: number;
  successful_extractions: number;
  failed_extractions: number;
  extraction_rate: string;
}

interface ApiResponse {
  model_used: string;
  total_images: number;
  total_embeddings: number;
  results: EmbeddingImageResult[];
  comparisons?: EmbeddingComparison[];
  summary: EmbeddingsSummary;
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

const FaceEmbeddingsPage: React.FC = () => {
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
    if (files.length < 1) {
      setError("At least 1 image is required for embedding extraction");
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
        '/api/extract-embeddings',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResults(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred during embedding extraction');
    } finally {
      setLoading(false);
    }
  };

  const renderEmbeddingVisualization = (embedding: number[], title: string) => {
    // Show first 32 dimensions for better visualization
    const displayDimensions = embedding.slice(0, 32);
    const maxValue = Math.max(...displayDimensions.map(Math.abs));
    const minValue = Math.min(...displayDimensions);
    const maxAbsValue = Math.max(Math.abs(minValue), Math.abs(Math.max(...displayDimensions)));
    
    return (
      <div className="embedding-visualization">
        <h4>{title}</h4>
        <p className="dimension-info">Showing first 32 of {embedding.length} dimensions</p>
        
        {/* Horizontal Bar Chart */}
        <div className="embedding-horizontal-bars">
          {displayDimensions.map((value, index) => (
            <div key={index} className="embedding-row">
              <span className="dimension-label">{index}</span>
              <div className="bar-track">
                <div className="zero-line"></div>
                <div 
                  className={`embedding-horizontal-bar ${value >= 0 ? 'positive' : 'negative'}`}
                  style={{
                    width: `${Math.abs(value) / maxAbsValue * 100}%`,
                    [value >= 0 ? 'left' : 'right']: '50%'
                  }}
                  title={`Dimension ${index}: ${value.toFixed(6)}`}
                />
              </div>
              <span className="value-label">{value.toFixed(3)}</span>
            </div>
          ))}
        </div>

        {/* Heatmap Visualization */}
        <div className="embedding-heatmap">
          <h5>Heatmap View (8x4 grid)</h5>
          <div className="heatmap-grid">
            {displayDimensions.map((value, index) => {
              const intensity = Math.abs(value) / maxAbsValue;
              const hue = value >= 0 ? 120 : 0; // Green for positive, Red for negative
              const saturation = 70;
              const lightness = 90 - (intensity * 40); // Darker = higher magnitude
              
              return (
                <div
                  key={index}
                  className="heatmap-cell"
                  style={{
                    backgroundColor: `hsl(${hue}, ${saturation}%, ${lightness}%)`
                  }}
                  title={`Dim ${index}: ${value.toFixed(6)}`}
                >
                  {index}
                </div>
              );
            })}
          </div>
        </div>

        {/* Line Chart */}
        <div className="embedding-line-chart">
          <h5>Line Chart View</h5>
          <svg className="line-chart-svg" viewBox="0 0 400 150">
            {/* Grid lines */}
            <defs>
              <pattern id="grid" width="25" height="25" patternUnits="userSpaceOnUse">
                <path d="M 25 0 L 0 0 0 25" fill="none" stroke="#e0e0e0" strokeWidth="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
            
            {/* Zero line */}
            <line x1="0" y1="75" x2="400" y2="75" stroke="#999" strokeWidth="1" strokeDasharray="2,2"/>
            
            {/* Data line */}
            <polyline
              fill="none"
              stroke="#9C27B0"
              strokeWidth="2"
              points={displayDimensions.map((value, index) => {
                const x = (index / (displayDimensions.length - 1)) * 380 + 10;
                const y = 75 - (value / maxAbsValue) * 60; // Center at 75, scale by 60px
                return `${x},${y}`;
              }).join(' ')}
            />
            
            {/* Data points */}
            {displayDimensions.map((value, index) => {
              const x = (index / (displayDimensions.length - 1)) * 380 + 10;
              const y = 75 - (value / maxAbsValue) * 60;
              return (
                <circle
                  key={index}
                  cx={x}
                  cy={y}
                  r="3"
                  fill={value >= 0 ? '#4CAF50' : '#f44336'}
                />
              );
            })}
          </svg>
        </div>

        <div className="embedding-stats">
          <div className="stat-item">
            <strong>Dimensions:</strong> {embedding.length}
          </div>
          <div className="stat-item">
            <strong>Min:</strong> {Math.min(...embedding).toFixed(4)}
          </div>
          <div className="stat-item">
            <strong>Max:</strong> {Math.max(...embedding).toFixed(4)}
          </div>
          <div className="stat-item">
            <strong>Mean:</strong> {(embedding.reduce((a, b) => a + b, 0) / embedding.length).toFixed(4)}
          </div>
          <div className="stat-item">
            <strong>Std Dev:</strong> {Math.sqrt(embedding.reduce((acc, val) => acc + Math.pow(val - (embedding.reduce((a, b) => a + b, 0) / embedding.length), 2), 0) / embedding.length).toFixed(4)}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="face-embeddings-page">
      <div className="page-header">
        <h1>🧮 Face Embeddings</h1>
        <p>Extract numerical feature vectors from face images for advanced analysis and clustering</p>
        
        <div className="educational-content">
          <h3>What are Face Embeddings?</h3>
          <p>
            Face embeddings are high-dimensional numerical representations of faces that capture unique facial features.
            These vectors allow computers to understand and compare faces mathematically.
          </p>
          
          <div className="use-cases">
            <h4>Key Use Cases:</h4>
            <ul>
              <li><strong>Similarity Search:</strong> Find similar faces in large databases</li>
              <li><strong>Face Clustering:</strong> Group photos by person automatically</li>
              <li><strong>Custom Models:</strong> Train specialized face recognition systems</li>
              <li><strong>Feature Analysis:</strong> Understand what makes faces unique</li>
              <li><strong>Distance Metrics:</strong> Quantify facial similarity</li>
            </ul>
          </div>
        </div>
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
          <small>Different models produce embeddings with different dimensions and characteristics</small>
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
          disabled={files.length < 1 || loading}
          className="submit-button"
        >
          {loading ? 'Extracting Embeddings...' : 'Extract Embeddings'}
        </button>
      </div>

      {results && (
        <div className="results-section">
          <h2>Embedding Results</h2>
          
          <div className="results-summary">
            <p><strong>Model Used:</strong> {results.model_used}</p>
            <p><strong>Total Images:</strong> {results.total_images}</p>
            <p><strong>Total Embeddings:</strong> {results.total_embeddings}</p>
            <p><strong>Embedding Dimensions:</strong> {results.summary.embedding_dimensions}</p>
            <p><strong>Extraction Rate:</strong> {results.summary.extraction_rate}</p>
          </div>
          
          <div className="embeddings-results">
            <h3>Face Embeddings by Image:</h3>
            {results.results.map((result, index) => (
              <div key={index} className="embedding-result">
                <h4>{result.filename}</h4>
                {result.error ? (
                  <p className="error">Error: {result.error}</p>
                ) : (
                  <>
                    <p><strong>Faces Detected:</strong> {result.faces_detected}</p>
                    {result.embeddings && result.embeddings.map((embedding, embIndex) => (
                      <div key={embIndex} className="single-embedding">
                        <h5>Face {embIndex + 1}</h5>
                        {embedding.region && (
                          <p><strong>Face Region:</strong> ({embedding.region.x}, {embedding.region.y}) 
                             {embedding.region.w}×{embedding.region.h}</p>
                        )}
                        {renderEmbeddingVisualization(
                          embedding.embedding, 
                          `Face ${embIndex + 1} Embedding Vector`
                        )}
                      </div>
                    ))}
                  </>
                )}
              </div>
            ))}
          </div>

          {results.comparisons && results.comparisons.length > 0 && (
            <div className="comparisons-section">
              <h3>Embedding Comparisons:</h3>
              <div className="comparison-grid">
                {results.comparisons.map((comp, index) => (
                  <div key={index} className="comparison-card">
                    <h4>{comp.image1} (Face {comp.face1_index}) vs {comp.image2} (Face {comp.face2_index})</h4>
                    <div className="comparison-metrics">
                      <div className="metric">
                        <span className="metric-label">Similarity:</span>
                        <span className="metric-value">{comp.similarity_percentage.toFixed(1)}%</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Cosine Distance:</span>
                        <span className="metric-value">{comp.cosine_distance.toFixed(4)}</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Euclidean Distance:</span>
                        <span className="metric-value">{comp.euclidean_distance.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FaceEmbeddingsPage;