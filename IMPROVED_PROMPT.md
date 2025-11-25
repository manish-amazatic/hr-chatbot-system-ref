# HR Chatbot System - Development Assignment

## Project Goal
Build an intelligent HR Chatbot system with agentic workflows, RAG (Retrieval Augmented Generation), and mock HRMS integration, consisting of three microservices deployed using Docker Compose.

---

## Team (5 Contributors)
1. **manish.w@amazatic.com** - Tech Lead & Architecture
2. **priyanka.c@amazatic.com** - Backend: hr-chatbot-service
3. **palak.s@amazatic.com** - Backend: hrms-mock-api
4. **rohit.g@amazatic.com** - Frontend: hr-chatbot-ui
5. **manik.l@amazatic.com** - DevOps & Docker Compose

---

## System Architecture

```
User ←→ hr-chatbot-ui (React)
         ↓
    hr-chatbot-service (FastAPI + LangChain + Agents + RAG)
         ↓
    hrms-mock-api (FastAPI + Mock Data)

    Milvus (Vector DB for HR Policies)
```

---

## Service 1: hr-chatbot-service

### Requirements
- **Framework**: Python 3.10+ with FastAPI
- **AI Stack**: LangChain, OpenAI GPT-4, Milvus
- **Pattern**: Chat Completion (NOT OpenAI Assistant API)
- **Architecture**: LLMProcessor (Factory + Singleton pattern)

### Core Components

#### 1. LLMProcessor (Factory + Singleton)
```python
class LLMProcessor:
    """
    Factory pattern for multi-provider LLM support
    Singleton to avoid recreating instances
    """
    - Support: OpenAI, Anthropic (extensible)
    - Dynamic model selection based on config
    - Singleton instance management
```

#### 2. Agents (using LangChain)

**Orchestrator Agent**
- Routes queries to appropriate agents or RAG tool
- Intent classification heuristic:
  - Keywords (policy, rules, FAQ, guide, manual, terms) → hr_rag_tool
  - Action verbs (apply, cancel, check, submit, order) → Specialized Agent

**Leave Agent**
- Tools: Apply leave, check balance, view history, cancel requests
- Calls: HRMS Leave APIs

**Attendance Agent**
- Tools: Check records, mark attendance, view summary
- Calls: HRMS Attendance APIs

**Payroll Agent**
- Tools: View salary slips, check details, tax info
- Calls: HRMS Payroll APIs

#### 3. hr_rag_tool (RAG Tool)
- Retrieves from Milvus vector database
- Contains 6-10 HR policy PDFs:
  - leave_policy.pdf
  - benefits_2025.pdf
  - payroll_process.pdf
  - attendance_policy.pdf
  - remote_work_policy.pdf
  - maternity_paternity_policy.pdf
  - performance_review_guidelines.pdf
  - code_of_conduct.pdf

#### 4. Authentication & Sessions
- JWT-based auth using HRMS Mock API
- Session storage with chat history
- Multi-user support

### API Endpoints
```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/verify

POST   /api/v1/chat/message          # Main chat endpoint
GET    /api/v1/chat/sessions
GET    /api/v1/chat/sessions/{id}
POST   /api/v1/chat/sessions
DELETE /api/v1/chat/sessions/{id}

GET    /api/v1/health
```

### Key Implementation Details
- Use **Chat Completion** approach (define system prompt & tools in app, not Assistant API)
- Implement **ConversationBufferMemory** for context retention
- Use **streaming responses** for better UX
- Proper **error handling** and fallbacks

---

## Service 2: hrms-mock-api

### Requirements
- **Framework**: Python 3.10+ with FastAPI
- **Database**: SQLite (dev) / PostgreSQL (prod) with SQLAlchemy
- **Authentication**: JWT tokens
- **Mock Data**: 5 employees × 1 month of realistic data

### Database Entities
1. **employees** - Employee profiles
2. **leave_balances** - Leave type balances per employee
3. **leave_requests** - Leave applications
4. **attendance_records** - Daily attendance
5. **payroll_records** - Monthly salary records

### Complete API List

#### Authentication APIs
```
POST   /api/v1/auth/login              # Login with email/password
POST   /api/v1/auth/refresh            # Refresh JWT token
POST   /api/v1/auth/logout             # Logout user
GET    /api/v1/auth/me                 # Get current user profile
GET    /api/v1/auth/verify             # Verify JWT token
```

#### Leave Management APIs
```
GET    /api/v1/leave/balance           # Get current leave balance
GET    /api/v1/leave/balance/types     # Get balance by leave type
GET    /api/v1/leave/requests          # List all leave requests (with filters)
GET    /api/v1/leave/requests/{id}     # Get specific leave request
POST   /api/v1/leave/requests          # Apply for leave
PUT    /api/v1/leave/requests/{id}     # Update leave request
DELETE /api/v1/leave/requests/{id}     # Cancel leave request
GET    /api/v1/leave/types             # Get available leave types
GET    /api/v1/leave/history           # Get leave history (past leaves)
GET    /api/v1/leave/calendar          # Get team leave calendar
```

#### Attendance APIs
```
GET    /api/v1/attendance/today        # Get today's attendance
GET    /api/v1/attendance/records      # List attendance records (date range)
POST   /api/v1/attendance/checkin      # Mark check-in
POST   /api/v1/attendance/checkout     # Mark check-out
PUT    /api/v1/attendance/update       # Update attendance record
GET    /api/v1/attendance/summary      # Monthly/yearly summary
GET    /api/v1/attendance/status       # Current attendance status
GET    /api/v1/attendance/report       # Generate attendance report
```

#### Payroll APIs
```
GET    /api/v1/payroll/current         # Current month payroll
GET    /api/v1/payroll/slips           # List all salary slips
GET    /api/v1/payroll/slips/{id}      # Get specific salary slip
GET    /api/v1/payroll/slips/{id}/pdf  # Download salary slip PDF
GET    /api/v1/payroll/ytd             # Year-to-date earnings
GET    /api/v1/payroll/tax-summary     # Tax summary (annual)
GET    /api/v1/payroll/breakdown       # Salary breakdown details
```


#### System APIs
```
GET    /api/v1/health                  # Health check endpoint
GET    /api/v1/system/stats            # System statistics
```

### Mock Data for 5 Employees

**Employee List:**
```
1. manish.w@amazatic.com    - Engineering Manager
2. priyanka.c@amazatic.com  - Senior Backend Developer
3. palak.s@amazatic.com     - Backend Developer
4. rohit.g@amazatic.com     - Frontend Developer
5. manik.l@amazatic.com     - DevOps Engineer
```

**Mock Data Coverage (1 month):**
- Leave balances for all leave types
- 2-3 leave requests per employee (various statuses)
- Daily attendance records for past 30 days
- Current month + 2 previous months salary slips
- Realistic variations in salary, attendance patterns

---

## Service 3: hr-chatbot-ui

### Requirements
- **Framework**: React 18+ with TypeScript
- **Styling**: Bootstrap 5
- **Chat UI**: assistant-ui (https://github.com/assistant-ui/assistant-ui)
- **Build**: Vite
- **State**: React Context + Hooks

### Layout Design (Split Screen 50-50)

```
┌────────────────────────────────────────────────────────┐
│  Header: Logo | Employee Name | Logout                 │
├──────────────────────┬─────────────────────────────────┤
│  Left 50%            │  Right 50%                      │
│                      │                                 │
│  SESSION LIST        │  CHAT INTERFACE                 │
│  ┌────────────────┐  │  ┌───────────────────────────┐ │
│  │ + New Chat     │  │  │ User: What's my balance?  │ │
│  │                │  │  │ Bot: You have 12 days...  │ │
│  │ ▶ Leave Qs     │  │  │                           │ │
│  │   2 hrs ago    │  │  │ User: Apply 3 days leave │ │
│  │                │  │  │ Bot: I'll help you...     │ │
│  │   Payroll      │  │  │                           │ │
│  │   Yesterday    │  │  │ [Input Box]               │ │
│  │                │  │  └───────────────────────────┘ │
│  │   Attendance   │  │                                 │
│  │   Jan 10       │  │  EXAMPLE PROMPTS                │
│  └────────────────┘  │  ┌───────────────────────────┐ │
│                      │  │ 💡 Try these:             │ │
│                      │  │ • Check leave balance     │ │
│                      │  │ • Apply for 2 days leave  │ │
│                      │  │ • Show attendance summary │ │
│                      │  │ • What's the WFH policy?  │ │
│                      │  │ • View my salary slip     │ │
│                      │  └───────────────────────────┘ │
└──────────────────────┴─────────────────────────────────┘
```

### Key Features
1. **Authentication**: Login page, JWT storage, auto-redirect on 401
2. **Chat Interface**: Message streaming, typing indicators, source citations
3. **Session Management**: Create, list, load, delete chat sessions
4. **Example Prompts**: Categorized by Leave, Attendance, Payroll, HR Policies
5. **Responsive**: Mobile-friendly, collapsible sidebar

### Integration with assistant-ui
```typescript
import { useAssistant } from "@assistant-ui/react";

const ChatInterface = () => {
  const assistant = useAssistant({
    endpoint: "http://localhost:8000/api/v1/chat/message",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return <assistant.MessageList />;
};
```

---

## Docker Compose Setup

### Services to Run
1. **milvus** - Vector database (port 19530)
2. **redis** - Session storage (port 6379)
3. **hrms-mock-api** - HRMS backend (port 8001)
4. **hr-chatbot-service** - Chatbot backend (port 8000)
5. **hr-chatbot-ui** - React frontend (port 3000)

### docker-compose.yml Structure
```yaml
version: '3.8'

services:
  milvus:
    image: milvusdb/milvus:latest
    ports: ["19530:19530", "9091:9091"]
    volumes: [milvus_data:/var/lib/milvus]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  hrms-mock-api:
    build: ./hrms-mock-api
    ports: ["8001:8000"]
    environment: [DATABASE_URL, JWT_SECRET_KEY]

  hr-chatbot-service:
    build: ./hr-chatbot-service
    ports: ["8000:8000"]
    depends_on: [milvus, hrms-mock-api, redis]
    environment: [OPENAI_API_KEY, MILVUS_URI, HRMS_API_URL]

  hr-chatbot-ui:
    build: ./hr-chatbot-ui
    ports: ["3000:80"]
    depends_on: [hr-chatbot-service]
```

### Environment Variables (.env)
```
OPENAI_API_KEY=sk-your-key-here
JWT_SECRET_KEY=your-secret-key
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini
```

---

## HR Policy PDF Generation

### Task: Generate 6-10 HR Policy PDFs

**Method:**
1. Use AI (ChatGPT/Claude) to generate realistic policy content
2. Convert to PDF using Python:
   - reportlab
   - pdfkit
   - weasyprint

**Required PDFs:**
1. leave_policy.pdf (3-5 pages)
2. benefits_2025.pdf (3-5 pages)
3. payroll_process.pdf (3-5 pages)
4. attendance_policy.pdf (3-5 pages)
5. remote_work_policy.pdf (3-5 pages)
6. maternity_paternity_policy.pdf (3-5 pages)
7. performance_review_guidelines.pdf (3-5 pages)
8. code_of_conduct.pdf (3-5 pages)

**Content Details:**
- Use company name: "Amazatic Technologies"
- Include metadata: filename, topic, creation date
- Realistic policies with proper structure
- 200-500 word chunks for good RAG retrieval

**Milvus Ingestion:**
1. Extract text from PDFs (pdfminer.six or PyMuPDF)
2. Chunk into 200-500 tokens
3. Generate embeddings (text-embedding-3-small)
4. Insert into Milvus collection with metadata

---

## Development Phases

### Phase 1: Foundation (Week 1)
- **All**: Project setup, dependencies, structure
- **Manik**: Docker Compose initial setup

### Phase 2: Core Development (Week 2-3)
- **Priyanka**: Agents, RAG tool, orchestrator, auth
- **Palak**: All HRMS APIs, mock data generation
- **Rohit**: UI components, chat interface, sessions
- **Manik**: Dockerfiles for all services

### Phase 3: Integration (Week 3-4)
- Integration testing between services
- Bug fixes and optimization
- **Manik**: Complete Docker Compose orchestration

### Phase 4: Testing & Polish (Week 4)
- End-to-end testing
- Performance tuning
- Documentation
- Demo preparation

---

## Key Requirements & Patterns

### Must Implement
1. ✅ **Chat Completion approach** (NOT OpenAI Assistant API)
2. ✅ **LLMProcessor** with factory pattern + singleton
3. ✅ **Agent-based architecture** with proper tool separation
4. ✅ **Orchestrator** with intent classification (heuristic or small model)
5. ✅ **Milvus RAG** with proper chunking and retrieval
6. ✅ **Session management** with conversation history
7. ✅ **JWT authentication** across services
8. ✅ **Split-screen UI** (chat + examples)
9. ✅ **Docker Compose** for easy deployment

### Milvus Collection Schema
```python
{
    "id": int64,  # Primary key
    "embedding": float_vector,  # dim=1536 for text-embedding-3-small
    "text": varchar,  # Chunk content
    "metadata": JSON  # {filename, topic, source, page, created_at}
}
```

### Agent Decision Heuristic
```
IF query contains ["policy", "rules", "FAQ", "guide", "manual", "terms"]:
    → Call hr_rag_tool
ELIF query contains ["apply", "cancel", "check", "submit", "mark"]:
    → Route to appropriate agent (Leave/Attendance/Payroll)
ELSE:
    → Ask clarifying question OR use orchestrator's LLM to decide
```

---

## Success Criteria

### Functional
- [ ] Orchestrator correctly routes all queries
- [ ] RAG tool retrieves relevant HR policies
- [ ] All HRMS APIs return realistic mock data
- [ ] Chat sessions persist and load correctly
- [ ] UI is responsive and intuitive

### Technical
- [ ] LLMProcessor follows factory + singleton
- [ ] Chat Completion (not Assistant API)
- [ ] Milvus properly integrated with 6-10 policy docs
- [ ] All services run via docker-compose up
- [ ] JWT auth works across services

### Quality
- [ ] API response time < 2s (95th percentile)
- [ ] RAG relevance score > 0.7
- [ ] Proper error handling everywhere
- [ ] Complete README for each service

---

## Deliverables

### Code
- [ ] Three service repositories with clean code
- [ ] Docker Compose setup
- [ ] Environment configuration files

### Documentation
- [ ] README.md for each service
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Architecture diagram
- [ ] Deployment guide

### Demo
- [ ] 2-5 minute demo video showing:
  - Login flow
  - Policy query (RAG)
  - Leave application (Agent → API)
  - Attendance check (Agent → API)
  - Session management

---

## Questions to Address Before Starting

1. ❓ **OpenAI API Access**: Do all contributors have OpenAI API keys? -> yes
2. ❓ **Milvus**: Local Docker or cloud (Zilliz)? -> local Docker
3. ❓ **LLM Model**: gpt-4o-mini, gpt-4, or other? -> selectable from from ENV Var
4. ❓ **Session Storage**: Redis, in-memory, or database? -> database
5. ❓ **Deployment**: Local development only or cloud? -> Local development only
6. ❓ **CI/CD**: Need automated pipeline? -> no
7. ❓ **Data Persistence**: Store chat history permanently?: ans -> yes

---

## Reference Materials

### Code References
- `refcode/day1/` - RAG basics, FAISS, Milvus, chat service
- `refcode/day2/` - Chains, Memory, Tools, Agents

### Documentation
- **Assignment PDF**: Agent architecture, RAG requirements
- **Reference Notes PDF**: Implementation patterns, Milvus checklist
- **LangChain Docs**: https://python.langchain.com/
- **assistant-ui**: https://github.com/assistant-ui/assistant-ui

---

## Getting Started

### Step 1: Review
- Read this entire document
- Review reference materials
- Understand your assigned service

### Step 2: Setup
- Clone/create repository
- Setup development environment
- Install dependencies

### Step 3: Align
- Kickoff meeting with team
- Clarify questions
- Agree on interfaces between services

### Step 4: Build
- Follow the development phases
- Daily standups to track progress
- Regular integration testing

---

*Document Version: 1.0*
*Last Updated: 2025-01-24*
*Owner: manish.w@amazatic.com*
