# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Face Matching POC (Proof of Concept) built with React frontend and FastAPI backend using the DeepFace library. The application allows users to upload 2-4 images and compare faces using various AI models like VGG-Face, FaceNet, ArcFace, etc.

## Architecture

### Backend (FastAPI + DeepFace)
- **Location**: `backend/main.py`
- **Framework**: FastAPI with uvicorn server
- **AI Library**: DeepFace (deepface==0.0.93) for face recognition
- **Models**: 9 different face recognition models preloaded for performance
- **Features**: 
  - Model preloading system for production performance
  - File upload handling with temporary file cleanup
  - CORS configuration for frontend communication
  - Health check endpoint at `/health`
  - Model selection endpoint at `/models`
  - Face comparison endpoint at `/compare-faces`

### Frontend (React + TypeScript)
- **Location**: `frontend/src/`
- **Framework**: React 19.1.0 with TypeScript
- **Key Components**:
  - Navigation component with routing
  - FaceVerificationPage for main functionality
  - HomePage for landing page
  - ComingSoonPage for future features
- **Libraries**: axios for API calls, react-dropzone for file uploads, react-router-dom for routing

### Deployment
- **Container**: Docker Compose setup with persistent model storage
- **Services**: Backend (port 8000), Frontend (port 3000/80)
- **Volumes**: `deepface_models` for persistent model weight storage
- **Networks**: `face-match-network` for service communication

## Development Commands

### Local Development

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
Backend runs on `http://localhost:8000`

#### Frontend Development
```bash
cd frontend
npm install
npm start
```
Frontend runs on `http://localhost:3000`

#### Available Frontend Scripts
- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Docker Development
```bash
# Build and run all services
docker-compose up --build

# Run in detached mode
docker-compose up --build -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
docker-compose logs backend
docker-compose logs frontend

# Check service status
docker-compose ps
```

### Testing and Linting
- **Frontend**: Uses Create React App's built-in ESLint configuration
- **Backend**: No specific linting configured, but follows FastAPI best practices
- **Tests**: Frontend has testing-library setup, backend has no tests configured

## Key Technical Details

### Environment Variables
- `TF_USE_LEGACY_KERAS=1` - Required for TensorFlow 2.16+ compatibility
- `TF_ENABLE_ONEDNN_OPTS=0` - Optimizes TensorFlow performance
- `PYTHONUNBUFFERED=1` - Ensures proper logging output

### Model Management
- Models are preloaded during backend startup (`preload_models()` function)
- First-time model downloads are cached in persistent volumes
- Models supported: Facenet, VGG-Face, Facenet512, OpenFace, DeepFace, DeepID, ArcFace, Dlib, SFace

### File Upload Handling
- Frontend uses react-dropzone for drag-and-drop file uploads
- Backend accepts 2-4 image files via `/compare-faces` endpoint
- Temporary files are automatically cleaned up after processing
- Image validation ensures proper formats are accepted

### API Endpoints
- `GET /health` - Health check with model loading status
- `GET /models` - Returns available face recognition models
- `POST /compare-faces` - Main face comparison endpoint

### Frontend Routing
- `/` - Home page
- `/face-verification` - Main face matching functionality
- `/face-recognition` - Coming soon page
- Additional coming soon pages for future features

## Future Features (Planned)

The application is designed to expand with additional DeepFace capabilities:

### Face Attributes Analysis
- Age estimation
- Gender detection
- Emotion recognition
- Race classification
- Facial expression analysis

### Face Embeddings
- Face representation extraction
- Similarity search using embeddings
- Face clustering capabilities
- Database storage for face vectors

### Additional DeepFace Features
- Face detection and facial area extraction
- Multiple face detection in single image
- Real-time face analysis
- Batch processing capabilities

## Production Considerations

### Memory Requirements
- Backend requires minimum 4GB RAM for model loading
- DeepFace models: ~2-3GB
- TensorFlow overhead: ~1-2GB
- Recommended: t3.large or equivalent for production

### Performance Optimization
- Model preloading eliminates cold start latency
- Persistent volume storage avoids model re-downloads
- Multi-stage Docker builds for smaller images
- nginx caching for frontend assets

### Security
- CORS configured for localhost:3000 (update for production)
- File type validation on uploads
- Request size limits
- No sensitive data exposure in logs

## Deployment Documentation

Comprehensive deployment instructions are available in `DEPLOYMENT.md` covering:
- AWS EC2 deployment with Docker Compose
- ECS Fargate deployment
- ECS on EC2 deployment
- Load balancer configuration
- Auto-scaling setup
- Cost optimization strategies