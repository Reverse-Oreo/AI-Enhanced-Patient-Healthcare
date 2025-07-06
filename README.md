# AI Medical Assistant Web App (In-Progress)

An intelligent medical diagnosis platform powered by LangGraph workflows and local AI models, featuring real-time symptom analysis, image classification, and comprehensive healthcare recommendations.

## 🌟 Features

### **Multi-Modal Medical Analysis**
- **Textual Symptom Analysis**: Advanced LLM-powered diagnosis from symptom descriptions
- **Medical Image Classification**: Skin lesion analysis using EfficientNet
- **Follow-up Interactions**: Dynamic questioning system for comprehensive diagnosis
- **Overall Analysis**: Synthesized insights from all available data sources

### **AI-Powered Chatbot Workflow**
- **LangGraph Integration**: Sophisticated agent orchestration and workflow management
- **Local Model Support**: Privacy-focused local LLM execution (Llama 3.1, BioMistral)
- **Real-time Processing**: WebSocket-based live updates and streaming responses
- **Confidence Scoring**: Quantified diagnostic confidence with threshold-based routing

### **Smart Healthcare Recommendations**
- **Specialist Referrals**: Intelligent matching with appropriate medical specialists
- **Urgency Assessment**: Automated severity classification and emergency detection
- **Self-care Guidance**: Personalized health management recommendations
- **Comprehensive Reports**: Detailed medical analysis summaries

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │◄──►│   FastAPI Backend │◄──►│  Local AI Models │
│   (TypeScript)   │    │   (Python)       │    │  (GGUF/PyTorch) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
    ┌────▼────┐             ┌────▼────┐             ┌────▼────┐
    │ Pages & │             │LangGraph│             │ Llama   │
    │UI Logic │             │Workflow │             │BioMistral│
    └─────────┘             └─────────┘             │EfficNet │
                                                    └─────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control
- **4GB+ RAM** for local AI models

### 1. Clone & Setup
```bash
git clone https://github.com/Jwongjs/AI-Medical-Assistant-Web-App.git
cd AI-Medical-Assistant-Web-App
```

### 2. Backend Setup
```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Download AI models (or use your own)
# Place models in backend/ai_models/ directory:
# - Llama-3.1-8B-UltraMedical.Q8_0.gguf
# - skin_lesion_efficientnetb0.pth

# Start backend server
python main.py
```

### 3. Frontend Setup
```bash
cd my-app

# Install Node dependencies
npm install

# Start development server
npm start
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📂 Project Structure

```
AI-Medical-Assistant-Web-App/
├── 📁 backend/                    # Python FastAPI backend
│   ├── 📁 adapters/              # Model abstraction layer
│   │   ├── base.py               # Base model interface
│   │   ├── local_model_adapter.py # Local LLM integration
│   │   ├── hf_api_adapter.py     # Hugging Face API client
│   │   └── skinlesion_efficientNet_adapter.py # Image classifier
│   ├── 📁 api/                   # REST API endpoints
│   ├── 📁 graphs/                # LangGraph workflow definitions
│   ├── 📁 managers/              # State & model management
│   ├── 📁 nodes/                 # Workflow node implementations
│   ├── 📁 schemas/               # Pydantic data models
│   ├── 📁 ai_models/             # Local AI model files
│   ├── main.py                   # FastAPI application entry
│   └── requirements.txt          # Python dependencies
├── 📁 my-app/                    # React TypeScript frontend
│   ├── 📁 src/
│   │   ├── 📁 components/        # Reusable UI components
│   │   ├── 📁 pages/             # Main application pages
│   │   ├── 📁 hooks/             # Custom React hooks
│   │   ├── 📁 services/          # API integration layer
│   │   ├── 📁 workflow/          # Workflow routing logic
│   │   └── 📁 types/             # TypeScript definitions
│   ├── package.json              # Node.js dependencies
│   └── tsconfig.json             # TypeScript configuration
├── 📁 4_deployment/              # Docker & Kubernetes configs
├── start-local-test.bat          # Windows startup script
└── README.md                     # This file
```

## 🔧 Configuration

### Environment Variables
Create `backend/.env`:
```env
# Hugging Face API Token (optional)
hf_api="your_hugging_face_token"

# Google Maps API Key (for specialist recommendations)
google_maps_api="your_google_maps_key"
```

### Model Configuration
Update model paths in `backend/graphs/patient_workflow.py`:
```python
multipurpose_model_path = "ai_models/Llama-3.1-8B-UltraMedical.Q8_0.gguf"
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
```

## 🎯 Usage Examples

### 1. Textual Symptom Analysis
```bash
curl -X POST "http://localhost:8000/patient/textual_analysis" \
     -F "user_symptoms=I have a headache and feel dizzy" \
     -F "session_id=session_123"
```

### 2. Image Classification
```bash
curl -X POST "http://localhost:8000/patient/image_analysis" \
     -F "image=@skin_lesion.jpg" \
     -F "session_id=session_123"
```

### 3. Follow-up Questions
```bash
curl -X POST "http://localhost:8000/patient/followup_questions" \
     -H "Content-Type: application/json" \
     -d '{"responses": {"How long have you had these symptoms?": "3 days"}}'
```

## 🔄 Workflow Stages

The application follows a sophisticated multi-stage workflow:

1. **Textual Analysis** → Initial symptom processing
2. **Follow-up Questions** → Dynamic clarification (optional)
3. **Image Analysis** → Medical image classification (optional)
4. **Overall Analysis** → Comprehensive data synthesis
5. **Healthcare Recommendations** → Specialist referrals & guidance
6. **Medical Report** → Final comprehensive summary

## 🛠️ Development

### Key Technologies
- **Backend**: FastAPI, LangGraph, LangChain, Pydantic, llama-cpp-python
- **Frontend**: React 19, TypeScript, Custom CSS
- **AI Models**: Llama 3.1, BioMistral, EfficientNet
- **Deployment**: Docker, Kubernetes (optional)

### Design Principles
1. **Lazy Loading**: Minimal LLM output optimization
2. **Singleton Pattern**: Efficient model sharing
3. **Privacy-First**: Local model execution
4. **Real-time Updates**: WebSocket streaming

### Adding New Models
1. Implement the `ModelInterface` in `backend/adapters/base.py`
2. Create adapter class inheriting from `ModelInterface`
3. Register in `backend/managers/model_manager.py`
4. Update workflow nodes as needed

## 🧪 Testing

### Backend Tests
```bash
cd backend
python test_script1.py        # Local model testing
python test_endpoint.py       # API endpoint testing
python hf_api_test.py         # Hugging Face integration
```

### Frontend Tests
```bash
cd my-app
npm test                      # Jest test suite
npm run build                 # Production build test
```

## 🚀 Deployment

### Local Development
```bash
# Windows
./start-local-test.bat

# Linux/Mac
./start-local-test.sh
```

### Docker Deployment
```bash
cd 4_deployment/docker
docker-compose up -d
```

### Kubernetes Deployment
```bash
cd 4_deployment/kubernetes
kubectl apply -f medical-ai-deployment.yaml
```

## 📊 Performance & Resources

### System Requirements
- **RAM**: 8GB minimum (16GB recommended for larger models)
- **Storage**: 10GB+ for AI models
- **CPU**: Multi-core processor recommended
- **GPU**: Optional (CUDA support for faster inference)

### Model Performance
- **Llama 3.1-8B**: ~4GB VRAM, 2-5 tokens/sec
- **EfficientNet**: ~1GB VRAM, <1sec inference
- **Embedding Model**: ~500MB RAM, <100ms

## 🔒 Security & Privacy

- **Local Processing**: All AI inference runs locally
- **No Data Storage**: Patient data not persisted
- **Session Isolation**: Each session independent
- **Input Validation**: Comprehensive request sanitization

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines
- Follow Python PEP 8 style guide
- Use TypeScript strict mode
- Add comprehensive tests for new features
- Update documentation for API changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Troubleshooting

### Common Issues

**Model Loading Errors**
```bash
# Ensure correct model paths
ls backend/ai_models/
# Check memory availability
free -h
```

**Frontend Connection Issues**
```bash
# Verify backend is running
curl http://localhost:8000/docs
# Check CORS settings
```

**Performance Issues**
- Reduce model size (use Q4 quantization)
- Enable GPU acceleration
- Increase system RAM

## 🙏 Acknowledgments

- **LangGraph**: Advanced AI agent orchestration
- **Llama.cpp**: Efficient local LLM inference
- **Hugging Face**: Model hosting and APIs
- **FastAPI**: Modern Python web framework
- **React**: Powerful frontend framework

---
