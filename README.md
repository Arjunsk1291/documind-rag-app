# 🚀 DocuMind - Advanced CAD Analysis RAG System

AI-powered document assistant with advanced multi-model CAD drawing analysis.

## ✨ Features

- 📄 **Multi-format Support**: PDF, DOCX, DXF, DWG, STL, and more
- 🤖 **6 AI Models**: Choose from Gemini and OpenRouter models
- 🔍 **5-Stage CAD Analysis**: Comprehensive technical analysis
- 💬 **RAG Chat**: Context-aware Q&A with your documents
- 🎨 **CAD Viewer**: Interactive SVG/PNG rendering
- 🧠 **Mind Maps**: Auto-generate Mermaid diagrams
- 🌓 **Dark Mode**: Beautiful UI with theme switching

## 🏗️ Architecture
```
Frontend (React + Vite) ← REST API → Backend (FastAPI)
                                          ↓
                            ┌─────────────┴─────────────┐
                            ↓                           ↓
                    Pinecone Vector DB          Google Gemini / OpenRouter
```

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Add your API keys

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
npm install
npm run dev
```

Visit: http://localhost:5173

## 🔑 Required API Keys

- **Google AI Studio**: https://aistudio.google.com/apikey
- **Pinecone**: https://www.pinecone.io/
- **OpenRouter** (optional): https://openrouter.ai/

## 📊 AI Models

| Model | Provider | Free | Capabilities |
|-------|----------|------|--------------|
| Gemini 2.5 Flash | Google | ✅ | Vision, Fast, 1M context |
| Gemini 2.5 Pro | Google | ❌ | Vision, Reasoning, 2M context |
| Xiaomi MiMo V2 | OpenRouter | ✅ | Vision, Multimodal |
| DeepSeek R1 | OpenRouter | ❌ | Reasoning, Chain-of-thought |
| NVIDIA Nemotron | OpenRouter | ✅ | Vision, Technical diagrams |
| Qwen 3 235B | OpenRouter | ❌ | Large-scale, Advanced |

## 🎯 Advanced CAD Analysis

1. Upload a DXF/DWG file
2. Create a new chat
3. Click the **Advanced CAD Analysis** button (purple sparkles ✨)
4. Wait 1-2 minutes for comprehensive 5-stage analysis

### Analysis Stages

1. **Overview**: Type, purpose, complexity assessment
2. **Technical**: Dimensions, line types, annotations, standards
3. **Components**: Inventory, features, materials, assemblies
4. **Measurements**: All dimensions, tolerances, specifications
5. **Quality**: Clarity rating, completeness, recommendations

## 📝 Tech Stack

**Backend:**
- FastAPI
- LlamaIndex
- Pinecone
- Google Gemini API
- OpenRouter API
- ezdxf (CAD parsing)

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- Axios
- Lucide Icons
- Mermaid.js

## 🤝 Contributing

Contributions welcome! Please open an issue first to discuss changes.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Google Gemini for advanced AI capabilities
- OpenRouter for model diversity
- Pinecone for vector storage
- ezdxf for CAD file parsing
