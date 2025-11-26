# HR Chatbot with Agent + Milvus RAG

## Goal

Build a Leave/Attendance/Payroll agents system plus an HR static-doc retriever (Milvus) containing HR policies, handbooks, benefit guides, and org chart PDFs.

## Tasks

### 1. Agents
- Leave Agent
- Attendance Agent
- Payroll Agent
- Orchestrator

### 2. Tools
- HR data tools (mock APIs)
- `hr_rag_tool` — retriever over HR PDFs:
  - `leave_policy.pdf`
  - `benefits_2025.pdf`
  - `payroll_process.pdf`

### 3. Data Task
Generate HR policy PDFs (6–10) using Copilot code assistant patterns and embed and ingest into Milvus.

### 4. Agent Logic
- If user asks static questions (e.g., "what's the maternity leave policy?"), call `hr_rag_tool`
- If user asks "apply leave", route to LeaveAgent/tool

## Deliverables

- Agent + tools + mock HR APIs
- Milvus corpus and retriever tool
- Demo flows:
  - Policy lookup (RAG)
  - Leave application (agent → tool → API)