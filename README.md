# HR Chatbot System - Monorepo

Intelligent HR Chatbot with agentic workflows, RAG capabilities, and mock HRMS integration.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     hr-chatbot-ui (React)                    │
│              Port: 3000 | Bootstrap + assistant-ui           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              hr-chatbot-service (Python FastAPI)             │
│         Port: 8000 | LangChain + Agents + Milvus RAG        │
│                                                              │
│  Orchestrator → [Leave Agent | Attendance | Payroll]        │
│              → [hr_rag_tool (Milvus)]                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               hrms-mock-api (Python FastAPI)                 │
│         Port: 8001 | SQLite + 40+ REST APIs                 │
│  Auth | Leave | Attendance | Payroll | Employees            │
└─────────────────────────────────────────────────────────────┘

    Milvus (19530)    Redis (6379)    SQLite
```

## 📁 Monorepo Structure

```
hr-chatbot-system/
├── services/
│   ├── hr-chatbot-service/      # Agentic chatbot service
│   ├── hrms-mock-api/           # Mock HRMS backend
│   └── hr-chatbot-ui/           # React frontend
├── infrastructure/
│   ├── docker/                  # Docker configs
│   └── scripts/                 # Deployment scripts
├── shared/                      # Shared utilities/types
├── docs/                        # Documentation
├── docker-compose.yml           # Multi-service orchestration
├── .env.example                 # Environment template
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+
- OpenAI API Key

### 1. Clone & Setup
```bash
# Navigate to project
cd hr-chatbot-system

# Copy environment file
cp .env.example .env

# Edit .env and add your OPENAI_API_KEY
nano .env
```

### 2. Start All Services
```bash
# Start everything with Docker Compose
docker-compose up --build

# Or start individual services for development
./infrastructure/scripts/start-dev.sh
```

### 3. Access Services
- **Frontend**: http://localhost:3000
- **Chatbot API**: http://localhost:8000/docs
- **HRMS API**: http://localhost:8001/docs
- **Milvus**: localhost:19530

## 🧪 Development

### Service 1: hr-chatbot-service
```bash
cd services/hr-chatbot-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option 1: Generate and ingest TEXT files (recommended for development)
python3 scripts/generate_hr_policies.py
python3 scripts/ingest_hr_policies.py --drop-existing

# Option 2: Generate and ingest PDF files (assignment requirement)
python3 scripts/generate_hr_policies_pdf.py
python3 scripts/ingest_hr_policies_pdf.py --drop-existing

# Both approaches work equally well for RAG
# Text: 8 files → 63 chunks (877 chars avg)
# PDF:  8 files → 10 chunks (773 chars avg)

# Start service
uvicorn api.main:app --reload --port 8000
```

### Service 2: hrms-mock-api
```bash
cd services/hrms-mock-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/seed_data.py
uvicorn api.main:app --reload --port 8001
```

### Service 3: hr-chatbot-ui
```bash
cd services/hr-chatbot-ui
npm install
npm run dev
```

## 📊 Services Overview

### hr-chatbot-service (Python FastAPI)

**Features**:
- **Orchestrator Agent** (improved intent routing with policy priority)
  - Explicit policy keyword detection
  - Informational question pattern matching
  - Smart routing: Questions → RAG, Actions → Agents
- **Leave Agent** (leave management via HRMS API)
- **Attendance Agent** (attendance tracking via HRMS API)
- **Payroll Agent** (payroll queries via HRMS API)
- **hr_rag_tool** (Milvus vector search with 8 HR policy documents)
  - 63 chunks ingested with OpenAI embeddings
  - Covers: leave, attendance, payroll, WFH, code of conduct, performance reviews, onboarding, handbook
- JWT authentication with token passthrough
- Session management with persistent chat history
- Streaming responses via Server-Sent Events (SSE)

**Key Files**:
- `core/processors/llm_processor.py` - Factory + Singleton LLM
- `core/agents/orchestrator.py` - Main routing agent with improved intent classification
- `core/tools/hr_rag_tool.py` - Milvus RAG retriever
- `api/routes/chat.py` - Chat endpoints (standard + streaming)
- `scripts/generate_hr_policies.py` - Generate 8 HR policy documents
- `scripts/ingest_hr_policies.py` - Ingest policies into Milvus (63 chunks)

### hrms-mock-api (Python FastAPI)

**Features**:
- 40+ REST APIs
- JWT authentication
- Mock data for 5 employees × 1 month
- SQLite database

**API Categories**:
- Auth (5 endpoints)
- Leave (9 endpoints)
- Attendance (8 endpoints)
- Payroll (7 endpoints)
- Employees (4 endpoints)

### hr-chatbot-ui (React + TypeScript)

**Features**:
- Split-screen layout (Chat + Examples)
- Session management
- assistant-ui integration
- Bootstrap 5 styling
- Responsive design

**Key Components**:
- `ChatInterface` - Main chat area
- `SessionList` - Chat history sidebar
- `ExamplesPanel` - Prompt examples
- `LoginForm` - Authentication

## 🧑‍💻 Team

1. **manish.w@amazatic.com**
2. **priyanka.c@amazatic.com**
3. **palak.s@amazatic.com**
4. **rohit.g@amazatic.com**
5. **manik.l@amazatic.com**

## 📅 Development Timeline

- **Week 1**: Foundation & Setup
- **Week 2**: Core Development
- **Week 3**: Integration
- **Week 4**: Testing & Polish

## 🧪 Testing & Demo

### Complete System Demo
Showcases both RAG flow (policy questions) and Agent flow (transactional queries):
```bash
./demo_complete_system.sh
```

**Demo includes**:
- 5 RAG flow tests (annual leave, WFH, performance reviews, maternity leave, code of conduct)
- 6 Agent flow tests (leave balance, apply leave, attendance, payroll)
- Complete end-to-end demonstration

### RAG Flow Tests
Test policy question routing and retrieval:
```bash
./test_rag_flow.sh
```

**Tests**:
- Annual leave policy → rag_tool (retrieves "20 days per year")
- WFH policy → rag_tool (retrieves eligibility and options)
- Performance reviews → rag_tool (retrieves review cycles)
- Maternity leave → rag_tool (retrieves "26 weeks, fully paid")
- Probation period → rag_tool

**Status**: ✅ 5/5 tests passing

### Integration Tests
Test all chatbot service endpoints:
```bash
./test_hr_chatbot_service.sh
```

### Agent-Specific Tests
Test attendance and payroll agents:
```bash
./test_updated_agents.sh
```

### Unit Tests
```bash
# Individual service tests
cd services/hr-chatbot-service && pytest
cd services/hrms-mock-api && pytest
cd services/hr-chatbot-ui && npm test
```

## 📚 Documentation

- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md)
- [API Documentation](docs/API_DOCS.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Development Guide](docs/DEVELOPMENT.md)

## 🔐 Environment Variables

Required variables in `.env`:
```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Services
CHATBOT_SERVICE_URL=http://localhost:8000
HRMS_SERVICE_URL=http://localhost:8001
FRONTEND_URL=http://localhost:3000

# Milvus
MILVUS_URI=http://localhost:19530
MILVUS_COLLECTION_NAME=hr_policies

# Database
DATABASE_URL=sqlite:///./hrms.db
```

## 🐛 Troubleshooting

### Common Issues

**1. Milvus connection fails**
```bash
# Check if Milvus is running
docker ps | grep milvus

# Restart Milvus
docker-compose restart milvus
```

**2. HRMS API database empty**
```bash
cd services/hrms-mock-api
python scripts/seed_data.py
```

**3. Frontend can't connect to backend**
- Check `.env.local` in hr-chatbot-ui
- Verify VITE_API_URL is set correctly

## 📖 Additional Resources

- [LangChain Docs](https://python.langchain.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [assistant-ui](https://github.com/assistant-ui/assistant-ui)
- [Milvus Docs](https://milvus.io/docs)

## 📄 License

Proprietary - Amazatic Technologies

---

**Latest Updates (2025-11-26)**:
- ✅ PDF generation and ingestion implemented (8 PDFs, 25.8 KB)
- ✅ Both text and PDF approaches fully operational
- ✅ PDF-based RAG validated (5/5 tests passing)
- ✅ 8 HR policy documents available in both formats
- ✅ Intent classification improved to prioritize policy/informational queries
- ✅ Complete system demo script created
- ✅ All documentation updated

*Last Updated: 2025-11-26*
*Project Owner: manish.w@amazatic.com*
