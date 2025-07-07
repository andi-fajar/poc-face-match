/**
 * Coming Soon Page Template
 * Created by @andi-fajar & Claude.ai
 */

import React from 'react';
import { Link } from 'react-router-dom';
import './ComingSoonPage.css';

interface ComingSoonPageProps {
  icon: string;
  title: string;
  description: string;
  features: string[];
  expectedFeatures: string[];
}

const ComingSoonPage: React.FC<ComingSoonPageProps> = ({
  icon,
  title,
  description,
  features,
  expectedFeatures
}) => {
  return (
    <div className="coming-soon-page">
      <div className="coming-soon-header">
        <div className="feature-icon-large">{icon}</div>
        <h1>{title}</h1>
        <p className="feature-description">{description}</p>
        <div className="coming-soon-badge-large">Coming Soon</div>
      </div>

      <div className="feature-details">
        <div className="detail-section">
          <h2>🚀 What This Feature Will Do</h2>
          <ul className="feature-list">
            {features.map((feature, index) => (
              <li key={index}>{feature}</li>
            ))}
          </ul>
        </div>

        <div className="detail-section">
          <h2>⚡ Expected Capabilities</h2>
          <ul className="feature-list">
            {expectedFeatures.map((capability, index) => (
              <li key={index}>{capability}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="tech-preview">
        <h2>🔧 Technology Stack</h2>
        <div className="tech-stack-preview">
          <div className="tech-item">
            <span>🧠</span>
            <span>DeepFace Library</span>
          </div>
          <div className="tech-item">
            <span>🚀</span>
            <span>FastAPI Backend</span>
          </div>
          <div className="tech-item">
            <span>⚛️</span>
            <span>React Frontend</span>
          </div>
          <div className="tech-item">
            <span>🔧</span>
            <span>TensorFlow Models</span>
          </div>
        </div>
      </div>

      <div className="call-to-action">
        <h2>🎯 Try Available Features</h2>
        <p>While this feature is in development, explore our working face verification!</p>
        <Link to="/face-verification" className="cta-button">
          🔍 Try Face Verification
        </Link>
      </div>

      <div className="back-to-home">
        <Link to="/" className="back-button">
          ← Back to Home
        </Link>
      </div>
    </div>
  );
};

export default ComingSoonPage;