# HR Chatbot Service

Agentic chatbot service with orchestrator, specialized agents (Leave, Attendance, Payroll), RAG tool for HR policies, and session management.

## Owner
**priyanka.c@amazatic.com**

## Tech Stack
- Python 3.10+
- FastAPI
- LangChain
- OpenAI GPT-4
- Milvus (Vector Database)
- SQLite (Session Storage)

## Architecture

```
Orchestrator Agent
├── Leave Agent → HRMS API
├── Attendance Agent → HRMS API
├── Payroll Agent → HRMS API
└── hr_rag_tool → Milvus (HR Policies)
```

## Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 4. Generate HR Policies
```bash
python scripts/generate_hr_policies.py
```

### 5. Ingest to Milvus
```bash
# Make sure Milvus is running (docker-compose up milvus)
python scripts/ingest_to_milvus.py
```

### 6. Run the Service
```bash
uvicorn api.main:app --reload --port 8000
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login with HRMS credentials
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/verify` - Verify token

### Chat
- `POST /api/v1/chat/message` - Send message to chatbot
- `POST /api/v1/chat/message/stream` - Send message with streaming
- `GET /api/v1/chat/sessions` - List user chat sessions
- `GET /api/v1/chat/sessions/{id}` - Get session messages
- `POST /api/v1/chat/sessions` - Create new session
- `DELETE /api/v1/chat/sessions/{id}` - Delete session

### Health
- `GET /api/v1/health` - Health check

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_agents.py
```

## Project Structure

```
hr-chatbot-service/
├── api/
│   ├── main.py                      # FastAPI app
│   └── routes/
│       ├── auth.py                  # Auth endpoints
│       ├── chat.py                  # Chat endpoints
│       └── health.py                # Health endpoints
├── core/
│   ├── processors/
│   │   └── llm_processor.py         # LLM Factory + Singleton
│   ├── agents/
│   │   ├── orchestrator.py          # Orchestrator agent
│   │   ├── leave_agent.py           # Leave agent
│   │   ├── attendance_agent.py      # Attendance agent
│   │   └── payroll_agent.py         # Payroll agent
│   └── tools/
│       ├── hr_rag_tool.py           # Milvus RAG tool
│       └── hrms_api_client.py       # HRMS API client
├── models/
│   ├── session.py                   # Session model
│   ├── message.py                   # Message model
│   └── user.py                      # User model
├── services/
│   ├── auth_service.py              # Auth service
│   ├── session_service.py           # Session service
│   └── milvus_service.py            # Milvus service
├── utils/
│   ├── jwt_utils.py                 # JWT utilities
│   └── config.py                    # Configuration
├── scripts/
│   ├── generate_hr_policies.py      # Generate HR PDFs
│   └── ingest_to_milvus.py          # Ingest to Milvus
├── tests/
├── requirements.txt
├── Dockerfile
└── README.md
```

## Implementation Tasks

See [IMPLEMENTATION_PLAN.md](../../IMPLEMENTATION_PLAN.md) for detailed tasks.

## Documentation

API documentation available at: http://localhost:8000/docs
