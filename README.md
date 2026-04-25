# SnapLearn AI - Adaptive Tutoring Engine

An AI-powered adaptive tutoring platform with personalized explanations, animated blackboards, and video generation capabilities.

## 🎯 Overview

SnapLearn AI is an embeddable tutoring engine that provides:

- **🤖 AI Tutoring**: Personalized explanations using Gemini API
- **📝 Animated Blackboard**: Step-by-step visual explanations  
- **🎥 Video Generation**: Educational videos created with Manim
- **👤 Student Profiles**: Adaptive learning based on progress tracking
- **🔧 SDK Integration**: RESTful API for embedding in any platform

## 🏗️ Architecture

- **Backend**: FastAPI with Gemini AI integration
- **Frontend**: React + TypeScript + Tailwind CSS
- **Video Generation**: Local Manim subprocess execution
- **Database**: Supabase with local JSON fallback
- **AI Models**: Google Gemini 3 Flash Preview

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ 
- Node.js 18+
- Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))
- Optional: Manim for video generation

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
# GOOGLE_API_KEY=your_api_key_here

# Start the FastAPI server
python main.py
```

The backend will be available at http://localhost:8000

### 2. Frontend Setup

```bash
# Navigate to frontend directory  
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at http://localhost:3000

### 3. Testing the Integration

1. Open http://localhost:3000 in your browser
2. Try asking a question like "How do fractions work?"
3. Watch the animated explanation on the blackboard
4. Generate a video by going to the Videos page
5. Check out the SDK demo for API integration examples

## 📖 API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Example API Call

```bash
curl -X POST http://localhost:8000/api/explain \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is photosynthesis?",
    "student_id": "demo-student", 
    "grade_level": "5",
    "language": "en"
  }'
```

## 🎬 Features

### Hero Feature 1: Manim Video Generator
Generate educational videos locally using Manim animations:
- Personalized content based on grade level
- Mathematical notation with MathTex
- Step-by-step visual explanations
- No cloud dependencies or generation limits

### Hero Feature 2: Adaptive AI Tutor
AI-powered tutoring with personalized explanations:
- Gemini-powered content generation
- Animated blackboard with SVG animations
- Student profile-based personalization
- Confusion detection and style adaptation

### Hero Feature 3: SDK Integration
Embeddable tutoring engine via REST API:
- Complete API documentation
- Live demo interface
- Multiple language SDKs
- Real-time API call monitoring

## 📁 Project Structure

```
SnapLearn/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── models.py           # Data models
│   ├── tutor_engine.py     # AI tutoring logic
│   ├── manim_generator.py  # Video generation
│   ├── memory.py           # Data persistence
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Page components
│   │   ├── utils/         # Utilities
│   │   └── types/         # TypeScript types
│   └── package.json       # Node.js dependencies
├── data/                  # Local data storage
├── videos/               # Generated videos
├── static/               # Static assets
└── Reference Docs/       # Documentation
```

## 🧪 Testing

See detailed testing instructions in [CHANGELOG.md](Reference%20Docs/CHANGELOG.md#testing-instructions---phase-1).

### Quick Health Check

1. **Backend**: Visit http://localhost:8000/health
2. **Frontend**: Visit http://localhost:3000  
3. **API**: Test explanation endpoint with sample question
4. **Video**: Generate a short test video

## 🔧 Configuration

### Environment Variables

Create `backend/.env` from `.env.example`:

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional  
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
```

### Development Settings

- **Backend Port**: 8000 (configurable via PORT env var)
- **Frontend Port**: 3000 (configurable via vite.config.ts)
- **API Proxy**: Frontend proxies /api requests to backend
- **Hot Reload**: Enabled for both frontend and backend

## 📊 Phase Progress

| Phase | Status | Features |
|-------|--------|----------|
| **Phase 1** | ✅ Complete | Foundation, API, Frontend, Basic AI |
| **Phase 2** | 🚧 Planned | Input modalities (image, voice) |
| **Phase 3** | 🚧 Planned | Advanced AI features, assessments |
| **Phase 4** | 🚧 Planned | Enhanced video generation |
| **Phase 5** | 🚧 Planned | SDK completion, analytics |
| **Phase 6** | 🚧 Planned | Hardening, performance, security |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/DarshanKrishna-DK/SnapLearn/issues)
- **Documentation**: [Reference Docs](Reference%20Docs/)
- **API Docs**: http://localhost:8000/docs (when running)

## 🙏 Acknowledgments

- **Google Gemini**: AI model and API
- **Manim**: Mathematical animation engine  
- **FastAPI**: Modern Python web framework
- **React**: Frontend framework
- **Tailwind CSS**: Utility-first CSS framework