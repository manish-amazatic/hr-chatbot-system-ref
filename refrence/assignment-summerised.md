# Assignment 2: HR Chatbot with Agent + Milvus RAG

## Goal
Build an HR chatbot system with:
- Leave/Attendance/Payroll agents
- HR static-doc retriever (Milvus) containing HR policies, handbooks, benefit guides, org chart PDFs

---

## Tasks

### 1. Agents
Implement the following agents:
- **Leave Agent**
- **Attendance Agent**
- **Payroll Agent**
- **Orchestrator** (to route queries to appropriate agents)

### 2. Tools

#### HR Data Tools
- Mock APIs for HR operations

#### hr_rag_tool
Retriever over HR PDFs, including:
- `leave_policy.pdf`
- `benefits_2025.pdf`
- `payroll_process.pdf`
- Additional HR policy documents

### 3. Data Task
- Generate HR policy PDFs (6–10) using Copilot code assistant patterns
- Embed and ingest into Milvus

### 4. Agent Logic

#### Static Questions → RAG Tool
**Example**: "What's the maternity leave policy?"
- Route to `hr_rag_tool`
- Retrieve relevant information from HR policy documents

#### Transactional Actions → Agent/Tool/API
**Example**: "Apply leave"
- Route to `LeaveAgent`
- Call appropriate tool
- Execute API call

---

## Deliverables

### 1. Agent + Tools + Mock HR APIs
- Fully functional agent system
- Mock API implementations for HR operations
- Tool definitions and implementations

### 2. Milvus Corpus and Retriever Tool
- Collection with 6-10 HR policy PDFs
- Properly chunked and embedded content
- Working retriever tool with query functionality

### 3. Demo Flows

#### Policy Lookup (RAG Flow)
Demonstrate static knowledge retrieval:
- "What is the paternity leave policy?"
- "How many sick days do employees get?"
- "What are the performance review guidelines?"

#### Leave Application (Agent → Tool → API Flow)
Demonstrate transactional operations:
- "I want to apply for 3 days of sick leave"
- "Check my remaining leave balance"
- "Cancel my leave request for next week"

---

## Sample HR Policy Documents to Generate

1. **leave_policy.pdf** - Vacation, sick, maternity, paternity leave policies
2. **benefits_2025.pdf** - Health insurance, retirement plans, perks
3. **payroll_process.pdf** - Salary disbursement, tax deductions, reimbursements
4. **attendance_policy.pdf** - Work hours, remote work, time tracking
5. **onboarding_handbook.pdf** - New employee orientation procedures
6. **performance_review.pdf** - Evaluation criteria, review cycles
7. **code_of_conduct.pdf** - Ethics, behavior standards
8. **training_policy.pdf** - Professional development, certifications
9. **org_structure.pdf** - Reporting hierarchy, department structure
10. **expense_reimbursement.pdf** - Travel, equipment, expense claims

---

## Implementation Checklist

### Phase 1: Setup
- [ ] Set up project structure
- [ ] Configure Milvus connection
- [ ] Set up LLM provider (using factory pattern)

### Phase 2: Data Preparation
- [ ] Generate 6-10 HR policy PDFs
- [ ] Extract text from PDFs
- [ ] Chunk content (200-500 tokens)
- [ ] Generate embeddings
- [ ] Ingest into Milvus collection

### Phase 3: Agent Development
- [ ] Implement Orchestrator agent
- [ ] Implement Leave Agent
- [ ] Implement Attendance Agent
- [ ] Implement Payroll Agent
- [ ] Create mock HR APIs

### Phase 4: RAG Integration
- [ ] Build hr_rag_tool
- [ ] Implement query embedding
- [ ] Implement similarity search
- [ ] Add response synthesis

### Phase 5: Testing & Demo
- [ ] Test static queries (RAG flow)
- [ ] Test transactional queries (Agent flow)
- [ ] Record demo video (2-5 minutes)
- [ ] Write README with setup instructions

---

## Example Query Flows

### Flow 1: Static Knowledge Query
```
User: "What's the maternity leave policy?"
↓
Orchestrator detects static knowledge intent
↓
Calls hr_rag_tool
↓
Embeds query → Searches Milvus → Retrieves relevant chunks
↓
LLM synthesizes answer from retrieved context
↓
Response: "According to our policy, maternity leave is..."
```

### Flow 2: Transactional Query
```
User: "Apply for 5 days leave from Dec 1st to Dec 5th"
↓
Orchestrator detects transactional intent
↓
Routes to Leave Agent
↓
Leave Agent calls leave_application_tool
↓
Tool calls mock HR API
↓
Response: "Leave application submitted successfully. Request ID: #12345"
```

---

## Expected Outcomes

Upon completion, your system should:
1. Successfully distinguish between static (RAG) and transactional (Agent) queries
2. Retrieve relevant HR policy information from Milvus
3. Process leave, attendance, and payroll operations via agents
4. Provide accurate responses with proper context
5. Handle edge cases gracefully

---

## Submission Requirements

1. **Source Code** - Complete implementation with all agents and tools
2. **Milvus Collection** - Populated with HR policy documents
3. **Demo Video** - 2-5 minutes showing both RAG and transactional flows
4. **README.md** - Setup instructions, architecture overview, how to run
5. **Sample PDFs** - Generated HR policy documents with metadata