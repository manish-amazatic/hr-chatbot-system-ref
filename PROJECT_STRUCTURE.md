# HR Chatbot System - Complete Project Structure

## 📁 Full Directory Tree

```
hr-chatbot-system/                          # Monorepo root
│
├── services/                                # All microservices
│   │
│   ├── hr-chatbot-service/                 # Service 1: Agentic Chatbot
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                     # FastAPI application
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py                 # Authentication endpoints
│   │   │       ├── chat.py                 # Chat endpoints
│   │   │       └── health.py               # Health check
│   │   │
│   │   ├── core/                           # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── processors/
│   │   │   │   ├── __init__.py
│   │   │   │   └── llm_processor.py        # LLM Factory + Singleton
│   │   │   ├── agents/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── orchestrator.py         # Main routing agent
│   │   │   │   ├── leave_agent.py          # Leave management
│   │   │   │   ├── attendance_agent.py     # Attendance tracking
│   │   │   │   └── payroll_agent.py        # Payroll queries
│   │   │   └── tools/
│   │   │       ├── __init__.py
│   │   │       ├── hr_rag_tool.py          # Milvus RAG retriever
│   │   │       └── hrms_api_client.py      # HRMS API client
│   │   │
│   │   ├── models/                         # Database models
│   │   │   ├── __init__.py
│   │   │   ├── session.py                  # Chat session model
│   │   │   ├── message.py                  # Message model
│   │   │   └── user.py                     # User model
│   │   │
│   │   ├── services/                       # Service layer
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py             # Authentication
│   │   │   ├── session_service.py          # Session management
│   │   │   └── milvus_service.py           # Milvus operations
│   │   │
│   │   ├── utils/                          # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── jwt_utils.py                # JWT helpers
│   │   │   └── config.py                   # Configuration
│   │   │
│   │   ├── scripts/                        # Utility scripts
│   │   │   ├── generate_hr_policies.py     # Generate HR PDFs
│   │   │   └── ingest_to_milvus.py         # Milvus ingestion
│   │   │
│   │   ├── tests/                          # Unit tests
│   │   │   ├── __init__.py
│   │   │   ├── test_agents.py
│   │   │   ├── test_tools.py
│   │   │   └── test_api.py
│   │   │
│   │   ├── docs/                           # HR policy PDFs
│   │   │   ├── leave_policy.pdf
│   │   │   ├── benefits_2025.pdf
│   │   │   ├── payroll_process.pdf
│   │   │   ├── attendance_policy.pdf
│   │   │   ├── remote_work_policy.pdf
│   │   │   ├── maternity_paternity_policy.pdf
│   │   │   ├── performance_review_guidelines.pdf
│   │   │   └── code_of_conduct.pdf
│   │   │
│   │   ├── data/                           # Runtime data
│   │   │   └── chatbot.db                  # SQLite database (sessions)
│   │   │
│   │   ├── requirements.txt                # Python dependencies
│   │   ├── Dockerfile                      # Container definition
│   │   ├── .env.example                    # Environment template
│   │   └── README.md                       # Service documentation
│   │
│   ├── hrms-mock-api/                      # Service 2: Mock HRMS
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                     # FastAPI application
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py                 # Auth endpoints (5)
│   │   │   │   ├── leave.py                # Leave endpoints (9)
│   │   │   │   ├── attendance.py           # Attendance endpoints (8)
│   │   │   │   ├── payroll.py              # Payroll endpoints (7)
│   │   │   │   ├── employees.py            # Employee endpoints (4)
│   │   │   │   └── health.py               # Health check
│   │   │   └── middleware/
│   │   │       └── auth_middleware.py      # JWT middleware
│   │   │
│   │   ├── models/                         # Database models
│   │   │   ├── __init__.py
│   │   │   ├── employee.py                 # Employee model
│   │   │   ├── leave.py                    # Leave models
│   │   │   ├── attendance.py               # Attendance model
│   │   │   └── payroll.py                  # Payroll model
│   │   │
│   │   ├── services/                       # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py             # Authentication
│   │   │   ├── leave_service.py            # Leave management
│   │   │   ├── attendance_service.py       # Attendance tracking
│   │   │   └── payroll_service.py          # Payroll processing
│   │   │
│   │   ├── utils/                          # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── jwt_utils.py                # JWT helpers
│   │   │   └── config.py                   # Configuration
│   │   │
│   │   ├── scripts/                        # Data scripts
│   │   │   ├── seed_data.py                # Seed database
│   │   │   └── generate_mock_data.py       # Generate mock data
│   │   │
│   │   ├── tests/                          # Unit tests
│   │   │   ├── __init__.py
│   │   │   ├── test_auth.py
│   │   │   ├── test_leave.py
│   │   │   ├── test_attendance.py
│   │   │   └── test_payroll.py
│   │   │
│   │   ├── data/                           # Database files
│   │   │   └── hrms.db                     # SQLite database
│   │   │
│   │   ├── requirements.txt                # Python dependencies
│   │   ├── Dockerfile                      # Container definition
│   │   ├── .env.example                    # Environment template
│   │   └── README.md                       # Service documentation
│   │
│   └── hr-chatbot-ui/                      # Service 3: React Frontend
│       ├── src/
│       │   ├── components/
│       │   │   ├── Auth/
│       │   │   │   ├── LoginForm.tsx       # Login page
│       │   │   │   └── ProtectedRoute.tsx  # Route guard
│       │   │   ├── Chat/
│       │   │   │   ├── ChatInterface.tsx   # Main chat area
│       │   │   │   ├── MessageList.tsx     # Message display
│       │   │   │   ├── MessageInput.tsx    # Input box
│       │   │   │   ├── Message.tsx         # Single message
│       │   │   │   └── TypingIndicator.tsx # Typing animation
│       │   │   ├── Sidebar/
│       │   │   │   ├── SessionList.tsx     # Session history
│       │   │   │   └── SessionItem.tsx     # Single session
│       │   │   ├── Examples/
│       │   │   │   ├── ExamplesPanel.tsx   # Prompt examples
│       │   │   │   └── PromptCard.tsx      # Single example
│       │   │   └── Layout/
│       │   │       ├── Header.tsx          # Top header
│       │   │       ├── Sidebar.tsx         # Left sidebar
│       │   │       └── MainLayout.tsx      # Main layout
│       │   │
│       │   ├── contexts/
│       │   │   ├── AuthContext.tsx         # Auth state
│       │   │   └── ChatContext.tsx         # Chat state
│       │   │
│       │   ├── services/
│       │   │   ├── api.ts                  # Axios instance
│       │   │   ├── authService.ts          # Auth API calls
│       │   │   └── chatService.ts          # Chat API calls
│       │   │
│       │   ├── hooks/
│       │   │   ├── useAuth.ts              # Auth hook
│       │   │   ├── useChat.ts              # Chat hook
│       │   │   └── useSessions.ts          # Sessions hook
│       │   │
│       │   ├── types/
│       │   │   ├── auth.types.ts           # Auth types
│       │   │   ├── chat.types.ts           # Chat types
│       │   │   └── session.types.ts        # Session types
│       │   │
│       │   ├── utils/
│       │   │   ├── tokenManager.ts         # Token storage
│       │   │   └── formatters.ts           # Formatting utils
│       │   │
│       │   ├── assets/                     # Static assets
│       │   ├── App.tsx                     # Root component
│       │   └── main.tsx                    # Entry point
│       │
│       ├── public/                         # Public assets
│       ├── index.html                      # HTML template
│       ├── package.json                    # NPM dependencies
│       ├── tsconfig.json                   # TypeScript config
│       ├── vite.config.ts                  # Vite config
│       ├── Dockerfile                      # Container definition
│       ├── .env.example                    # Environment template
│       └── README.md                       # Service documentation
│
├── infrastructure/                         # Infrastructure code
│   ├── docker/                             # Docker configs
│   │   ├── milvus/                         # Milvus config
│   │   └── nginx/                          # Nginx config (if needed)
│   └── scripts/                            # Utility scripts
│       ├── start-dev.sh                    # Start all services
│       ├── stop-all.sh                     # Stop all services
│       ├── reset-db.sh                     # Reset databases
│       ├── logs.sh                         # View logs
│       └── test-all.sh                     # Run all tests
│
├── shared/                                 # Shared code (if needed)
│   ├── types/                              # Shared TypeScript types
│   └── utils/                              # Shared utilities
│
├── docs/                                   # Project documentation
│   ├── ARCHITECTURE.md                     # Architecture guide
│   ├── API_DOCS.md                         # API documentation
│   └── DEVELOPMENT.md                      # Development guide
│
├── docker-compose.yml                      # Multi-service orchestration
├── .env.example                            # Environment template
├── .gitignore                              # Git ignore rules
├── README.md                               # Main documentation
├── IMPLEMENTATION_PLAN.md                  # Implementation plan
└── PROJECT_STRUCTURE.md                    # This file
```

## 📊 File Count Summary

### Total Files by Category

**Configuration Files**: 15
- docker-compose.yml
- .env.example (x4 - root + 3 services)
- Dockerfile (x3)
- package.json
- tsconfig.json
- vite.config.ts
- requirements.txt (x2)
- .gitignore

**Documentation**: 8
- README.md (x4 - root + 3 services)
- IMPLEMENTATION_PLAN.md
- PROJECT_STRUCTURE.md
- ARCHITECTURE.md
- DEVELOPMENT.md

**Python Source Files**: ~40
- API routes: ~12 files
- Core logic (agents, tools, processors): ~8 files
- Models: ~8 files
- Services: ~8 files
- Scripts: ~4 files
- Tests: ~10 files

**TypeScript Source Files**: ~30
- Components: ~15 files
- Contexts: 2 files
- Services: 3 files
- Hooks: 3 files
- Types: 3 files
- Utils: 2 files
- Root: 2 files

**Infrastructure Scripts**: 5
- Bash scripts for deployment and management

**Total Estimated Files**: ~100+ files

## 🎯 Key Entry Points

### Development
1. **Start Everything**: `./infrastructure/scripts/start-dev.sh`
2. **HRMS API**: `services/hrms-mock-api/api/main.py`
3. **Chatbot Service**: `services/hr-chatbot-service/api/main.py`
4. **Frontend**: `services/hr-chatbot-ui/src/main.tsx`

### Configuration
1. **Environment**: `.env` (root level)
2. **Docker**: `docker-compose.yml`
3. **Service Configs**: Each service has `.env.example`

### Documentation
1. **Getting Started**: `README.md`
2. **Implementation Tasks**: `IMPLEMENTATION_PLAN.md`
3. **Service Docs**: Each service has `README.md`

## 🔧 Technology Stack by Service

### hr-chatbot-service
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **AI/ML**: LangChain, OpenAI
- **Vector DB**: Milvus
- **Session DB**: SQLite
- **Testing**: pytest

### hrms-mock-api
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Testing**: pytest

### hr-chatbot-ui
- **Language**: TypeScript
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Bootstrap 5
- **Chat UI**: assistant-ui
- **Routing**: React Router
- **HTTP**: Axios

### Infrastructure
- **Containers**: Docker
- **Orchestration**: Docker Compose
- **Vector DB**: Milvus
- **Scripts**: Bash

## 📋 Next Steps

1. **Setup Environment**
   ```bash
   cd hr-chatbot-system
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Start Services**
   ```bash
   ./infrastructure/scripts/start-dev.sh
   ```

3. **Begin Implementation**
   - Follow [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
   - Each contributor starts with their assigned service
   - Use service-level READMEs for setup instructions

## 📊 Lines of Code Estimate

| Component | Estimated LOC |
|-----------|---------------|
| hr-chatbot-service | 3,000 - 4,000 |
| hrms-mock-api | 2,500 - 3,500 |
| hr-chatbot-ui | 2,000 - 3,000 |
| Tests | 1,500 - 2,000 |
| Documentation | 1,000 - 1,500 |
| Scripts & Config | 500 - 1,000 |
| **Total** | **10,500 - 15,000** |

## 🎓 Learning Path

### For New Contributors

1. **Read Documentation** (Day 1)
   - Main README.md
   - IMPLEMENTATION_PLAN.md
   - Your service README.md

2. **Setup Environment** (Day 1)
   - Install dependencies
   - Configure .env
   - Run services

3. **Explore Reference Code** (Day 1-2)
   - Review `refcode/day1` (RAG basics)
   - Review `refcode/day2` (Agents & Tools)

4. **Start Implementation** (Day 2+)
   - Follow your service tasks
   - Daily standups
   - Regular integration testing

---

*Last Updated: 2025-01-24*
*Total Setup Time: ~1 hour*
*Ready for Development: ✅*
