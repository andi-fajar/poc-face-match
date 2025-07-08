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
import FacialAttributesPage from './pages/FacialAttributesPage';
import FaceEmbeddingsPage from './pages/FaceEmbeddingsPage';
import SpoofDetectionPage from './pages/SpoofDetectionPage';
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
            
            <Route path="/facial-attributes" element={<FacialAttributesPage />} />
            
            <Route path="/face-embeddings" element={<FaceEmbeddingsPage />} />
            
            <Route path="/anti-spoofing" element={<SpoofDetectionPage />} />
            
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
