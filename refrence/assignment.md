# HR Chatbot with Agent + Milvus RAG

## Goal:
  Leave/Attendance/Payroll agents plus an HR staƟc-doc retriever (Milvus) containing HR
  policies, handbooks, benefit guides, org chart PDFs.

## Tasks

1. Agents: Leave Agent, Attendance Agent, Payroll Agent, Orchestrator.
2. Tools:
    - HR data tools (mock APIs)
    - hr_rag_tool — retriever over HR PDFs (leave_policy.pdf, benefits_2025.pdf, payroll_process.pdf)
3. Data task: generate HR policy PDFs (6–10) using Copilot code assistant patterns; embed and ingest into Milvus.
4. Agent logic: If user asks staƟc quesƟons (e.g., “what's the maternity leave policy?”), call hr_rag_tool; if user asks “apply leave” route to LeaveAgent/tool.

## Deliverables

- Agent + tools + mock HR APIs
- Milvus corpus and retriever tool
- Demo flows: policy lookup (RAG) and leave applicaƟon (agent → tool → API)
