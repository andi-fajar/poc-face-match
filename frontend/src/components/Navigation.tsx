/**
 * Navigation Component
 * Created by @andi-fajar & Claude.ai
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navigation.css';

const Navigation: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: '🏠' },
    { path: '/face-verification', label: 'Face Verification', icon: '🔍' },
    { path: '/face-recognition', label: 'Face Recognition', icon: '👤' },
    { path: '/facial-attributes', label: 'Facial Attributes', icon: '📊' },
    { path: '/face-embeddings', label: 'Face Embeddings', icon: '🧮' },
    { path: '/anti-spoofing', label: 'Anti-Spoofing', icon: '🔒' },
    { path: '/real-time', label: 'Real-time Analysis', icon: '📹' },
  ];

  return (
    <nav className="navigation">
      <div className="nav-header">
        <h2>🎯 Face Matching POC</h2>
        <p>Powered by DeepFace</p>
      </div>
      <ul className="nav-list">
        {navItems.map((item) => (
          <li key={item.path}>
            <Link 
              to={item.path} 
              className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          </li>
        ))}
      </ul>
      <div className="nav-footer">
        <p>Created by <a href="https://github.com/andi-fajar" target="_blank" rel="noopener noreferrer">@andi-fajar</a> & <a href="https://claude.ai" target="_blank" rel="noopener noreferrer">Claude.ai</a></p>
      </div>
    </nav>
  );
};

export default Navigation;