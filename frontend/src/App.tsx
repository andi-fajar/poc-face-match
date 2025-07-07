/**
 * Face Matching POC - React Frontend
 * Created by @andi-fajar & Claude.ai
 * 
 * A fun proof-of-concept application for face matching using DeepFace library
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import FaceVerificationPage from './pages/FaceVerificationPage';
import ComingSoonPage from './pages/ComingSoonPage';
import './App.css';

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/face-verification" element={<FaceVerificationPage />} />
            
            {/* Coming Soon Pages */}
            <Route 
              path="/face-recognition" 
              element={
                <ComingSoonPage
                  icon="👤"
                  title="Face Recognition"
                  description="Find and identify faces in a database of known individuals using advanced AI models"
                  features={[
                    "Search faces in large databases",
                    "Real-time face identification",
                    "Multiple face detection in single image",
                    "Confidence scoring for matches",
                    "Support for various image formats"
                  ]}
                  expectedFeatures={[
                    "Database management for known faces",
                    "Batch processing capabilities",
                    "Integration with security systems",
                    "RESTful API for external integration",
                    "Advanced filtering and search options"
                  ]}
                />
              } 
            />
            
            <Route 
              path="/facial-attributes" 
              element={
                <ComingSoonPage
                  icon="📊"
                  title="Facial Attributes Analysis"
                  description="Analyze age, gender, emotion, and race from facial images using deep learning models"
                  features={[
                    "Age estimation with accuracy",
                    "Gender classification",
                    "Emotion detection (happy, sad, angry, etc.)",
                    "Race/ethnicity prediction",
                    "Real-time attribute analysis"
                  ]}
                  expectedFeatures={[
                    "Demographic analytics dashboard",
                    "Batch processing for multiple faces",
                    "Custom attribute model training",
                    "Export analysis results",
                    "Integration with business intelligence tools"
                  ]}
                />
              } 
            />
            
            <Route 
              path="/face-embeddings" 
              element={
                <ComingSoonPage
                  icon="🧮"
                  title="Face Embeddings"
                  description="Extract numerical feature vectors from face images for advanced analysis and clustering"
                  features={[
                    "512-dimensional face embeddings",
                    "Feature vector extraction",
                    "Similarity calculations",
                    "Clustering capabilities",
                    "Export embeddings for ML pipelines"
                  ]}
                  expectedFeatures={[
                    "Vector database integration",
                    "Dimensionality reduction visualization",
                    "Custom embedding models",
                    "Batch embedding extraction",
                    "API for embedding services"
                  ]}
                />
              } 
            />
            
            <Route 
              path="/anti-spoofing" 
              element={
                <ComingSoonPage
                  icon="🔒"
                  title="Face Anti-Spoofing"
                  description="Detect real faces vs fake/spoofed images for enhanced security and fraud prevention"
                  features={[
                    "Live face detection",
                    "Photo/video spoof detection",
                    "3D mask detection",
                    "Deepfake identification",
                    "Security scoring system"
                  ]}
                  expectedFeatures={[
                    "Real-time liveness detection",
                    "Multi-modal verification",
                    "Integration with authentication systems",
                    "Fraud prevention analytics",
                    "Customizable security thresholds"
                  ]}
                />
              } 
            />
            
            <Route 
              path="/real-time" 
              element={
                <ComingSoonPage
                  icon="📹"
                  title="Real-time Analysis"
                  description="Perform face analysis on live webcam feed with real-time processing capabilities"
                  features={[
                    "Live webcam face detection",
                    "Real-time attribute analysis",
                    "Multiple face tracking",
                    "Live recognition against database",
                    "Performance optimization for speed"
                  ]}
                  expectedFeatures={[
                    "Video stream processing",
                    "Recording and playback features",
                    "Alert system for matches",
                    "Dashboard for live monitoring",
                    "Mobile device compatibility"
                  ]}
                />
              } 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
