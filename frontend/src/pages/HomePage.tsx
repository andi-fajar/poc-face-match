/**
 * Home Page Component
 * Created by @andi-fajar & Claude.ai
 */

import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage: React.FC = () => {
  const features = [
    {
      title: 'Face Verification',
      description: 'Compare 2-4 faces to verify if they belong to the same person using 9 AI models',
      icon: '🔍',
      path: '/face-verification',
      status: 'available'
    },
    {
      title: 'Face Recognition',
      description: 'Find and identify faces in a database of known individuals',
      icon: '👤',
      path: '/face-recognition',
      status: 'coming-soon'
    },
    {
      title: 'Facial Attributes',
      description: 'Analyze age, gender, emotion, and ethnicity from facial images using AI',
      icon: '🧠',
      path: '/facial-attributes',
      status: 'available'
    },
    {
      title: 'Face Embeddings',
      description: 'Extract numerical feature vectors from face images',
      icon: '🧮',
      path: '/face-embeddings',
      status: 'coming-soon'
    },
    {
      title: 'Anti-Spoofing',
      description: 'Detect real faces vs fake/spoofed images for security',
      icon: '🔒',
      path: '/anti-spoofing',
      status: 'available'
    },
    {
      title: 'Real-time Analysis',
      description: 'Perform face analysis on live webcam feed',
      icon: '📹',
      path: '/real-time',
      status: 'coming-soon'
    }
  ];

  return (
    <div className="home-page">
      <div className="hero-section">
        <h1>🎯 Face Matching POC</h1>
        <p className="hero-subtitle">
          Explore the power of modern face recognition technology with DeepFace
        </p>
        <p className="hero-description">
          This proof-of-concept showcases advanced facial analysis capabilities including 
          face verification, facial attributes analysis (age, gender, emotion, ethnicity), 
          and more. Built with React, FastAPI, and the powerful DeepFace library.
        </p>
      </div>

      <div className="features-grid">
        {features.map((feature, index) => (
          <div key={index} className={`feature-card ${feature.status}`}>
            <div className="feature-icon">{feature.icon}</div>
            <h3 className="feature-title">{feature.title}</h3>
            <p className="feature-description">{feature.description}</p>
            <div className="feature-actions">
              {feature.status === 'available' ? (
                <Link to={feature.path} className="feature-button primary">
                  Try Now
                </Link>
              ) : (
                <>
                  <Link to={feature.path} className="feature-button secondary">
                    Preview
                  </Link>
                  <span className="coming-soon-badge">Coming Soon</span>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="featured-section">
        <h2>🚀 Available Features</h2>
        <div className="featured-items">
          <div className="featured-item">
            <span className="featured-icon">🔍</span>
            <div className="featured-content">
              <h3>Face Verification</h3>
              <p>Compare multiple faces with 9 different AI models including VGG-Face, FaceNet, and ArcFace</p>
              <ul>
                <li>Support for 2-4 images simultaneously</li>
                <li>Confidence scores and detailed metrics</li>
                <li>Multiple face recognition models</li>
              </ul>
            </div>
          </div>
          <div className="featured-item">
            <span className="featured-icon">🧠</span>
            <div className="featured-content">
              <h3>Facial Attributes Analysis</h3>
              <p>Extract demographic and emotional insights from facial images using deep learning</p>
              <ul>
                <li>Age estimation with high accuracy</li>
                <li>Gender classification with confidence</li>
                <li>Emotion detection (7 emotions)</li>
                <li>Ethnicity analysis (6 categories)</li>
                <li>Multiple faces per image support</li>
              </ul>
            </div>
          </div>
          <div className="featured-item">
            <span className="featured-icon">🔒</span>
            <div className="featured-content">
              <h3>Face Anti-Spoofing</h3>
              <p>Advanced security through real vs fake face detection using MiniVision models</p>
              <ul>
                <li>Detect spoofed photos and videos</li>
                <li>Anti-spoofing confidence scores</li>
                <li>Multiple face analysis support</li>
                <li>Real-time fraud prevention</li>
                <li>Enhanced security verification</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="tech-stack">
        <h2>Technology Stack</h2>
        <div className="tech-items">
          <div className="tech-item">
            <span className="tech-icon">⚛️</span>
            <span>React + TypeScript</span>
          </div>
          <div className="tech-item">
            <span className="tech-icon">🚀</span>
            <span>FastAPI</span>
          </div>
          <div className="tech-item">
            <span className="tech-icon">🧠</span>
            <span>DeepFace</span>
          </div>
          <div className="tech-item">
            <span className="tech-icon">🐳</span>
            <span>Docker</span>
          </div>
          <div className="tech-item">
            <span className="tech-icon">🔧</span>
            <span>TensorFlow</span>
          </div>
        </div>
      </div>

      <div className="credits">
        <p>
          Created by{' '}
          <a href="https://github.com/andi-fajar" target="_blank" rel="noopener noreferrer">
            @andi-fajar
          </a>{' '}
          &{' '}
          <a href="https://claude.ai" target="_blank" rel="noopener noreferrer">
            Claude.ai
          </a>
        </p>
      </div>
    </div>
  );
};

export default HomePage;