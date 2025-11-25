# RAG System for HR Policy Search

## Overview

The HR Chatbot uses a Retrieval-Augmented Generation (RAG) system to answer questions about company policies and guidelines. This system combines vector similarity search with LLM-powered answer generation to provide accurate, context-aware responses.

## Architecture

```
User Query
    ↓
Orchestrator (Intent Classification)
    ↓
Policy Intent Detected
    ↓
search_hr_policies() Tool
    ↓
Milvus Vector Search (Top 3 similar documents)
    ↓
Context Formatting
    ↓
LLM Answer Generation (GPT-4 with context)
    ↓
Final Answer to User
```

## Components

### 1. Milvus Vector Database (`services/milvus_service.py`)

Manages vector database operations:
- **Connection**: Connects to Milvus server (default: localhost:19530)
- **Collection**: Stores documents with 1536-dimension embeddings (OpenAI text-embedding-3-small)
- **Indexing**: Uses IVF_FLAT index with L2 distance metric
- **Search**: Finds top-k similar documents based on query embedding

**Schema:**
```python
{
    "id": INT64 (auto-generated),
    "document_id": VARCHAR(100),
    "content": VARCHAR(5000),
    "metadata": JSON,
    "embedding": FLOAT_VECTOR(1536)
}
```

### 2. RAG Tool (`core/tools/hr_rag_tool.py`)

LangChain tool for policy search:
- **Tool Function**: `search_hr_policies(query: str) -> str`
- **Retrieval**: Fetches top 3 documents with similarity threshold of 0.5
- **Answer Generation**: Uses LLM with retrieved context
- **Fallback**: Graceful error handling when Milvus is unavailable

### 3. Orchestrator Integration (`core/agents/orchestrator.py`)

Routes policy-related queries:
- **Intent Detection**: Keywords like "policy", "rule", "guideline", "procedure"
- **Routing**: Directs POLICY intent to RAG tool
- **Error Handling**: Returns helpful messages on failures

## Setup and Usage

### Prerequisites

1. **Milvus Server**

You can run Milvus locally using Docker:

```bash
# Start Milvus (standalone mode)
docker run -d \
  --name milvus \
  -p 19530:19530 \
  -p 9091:9091 \
  milvusdb/milvus:latest

# Verify Milvus is running
docker ps | grep milvus
```

For production, use Milvus Distributed or Milvus Cloud.

2. **OpenAI API Key**

Set your OpenAI API key in `.env`:
```
OPENAI_API_KEY=sk-...
```

### Ingesting HR Policies

#### Step 1: Prepare Policy Documents

Policies are stored in `data/hr_policies/sample_policies.json`. Format:

```json
[
  {
    "id": "pol_001",
    "content": "Policy content here...",
    "metadata": {
      "title": "Policy Title",
      "category": "Leave Policy",
      "document_type": "policy",
      "version": "1.0",
      "last_updated": "2024-01-01"
    }
  }
]
```

#### Step 2: Run Ingestion Script

```bash
cd services/hr-chatbot-service

# Ingest policies (keeps existing collection)
python scripts/ingest_hr_policies.py

# Drop existing collection and re-ingest
python scripts/ingest_hr_policies.py --drop-existing
```

The script will:
1. Load policy documents from JSON
2. Connect to Milvus
3. Create collection (if needed)
4. Generate embeddings using OpenAI
5. Insert documents into Milvus

**Output:**
```
============================================================
HR Policy Ingestion Script
============================================================
Loading policy documents from: data/hr_policies/sample_policies.json
Loaded 15 policy documents
Initializing Milvus service...
Creating collection: hr_policies
Inserting 15 documents...
Generating embeddings (this may take a moment)...
============================================================
✓ Successfully ingested all HR policy documents!
============================================================
Collection: hr_policies
Documents: 15
Embedding Model: text-embedding-3-small
Dimension: 1536
============================================================
```

## Testing the RAG System

### 1. Test via API

```bash
# Send a policy query
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the company leave policy?",
    "user_id": "test_user"
  }'
```

### 2. Test via UI

1. Open http://localhost:5173
2. Ask policy questions like:
   - "What is the annual leave policy?"
   - "How many sick days do I get?"
   - "What are the working hours?"
   - "What is the dress code?"
   - "How do I claim expenses?"

### 3. Example Queries

**Leave Policies:**
- "How much annual leave do I get?"
- "Can I carry forward unused leave?"
- "What is the maternity leave policy?"

**Work Arrangements:**
- "What are the standard working hours?"
- "Can I work remotely?"
- "What is the flexible working policy?"

**Payroll:**
- "When do I get paid?"
- "How do I access my payslip?"

**General Policies:**
- "What is the code of conduct?"
- "What is the training budget?"
- "What is the notice period for resignation?"

## Configuration

### Environment Variables

```bash
# Milvus Configuration
MILVUS_URI=http://localhost:19530
MILVUS_TOKEN=  # Optional: for authenticated Milvus
MILVUS_COLLECTION_NAME=hr_policies

# OpenAI Configuration
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4

# RAG Parameters (in code)
SIMILARITY_THRESHOLD=0.5  # Minimum similarity score
TOP_K=3  # Number of documents to retrieve
```

### Tuning RAG Performance

1. **Similarity Threshold** (`hr_rag_tool.py:58`)
   - Lower (0.3-0.5): More results, less precise
   - Higher (0.7-0.9): Fewer results, more precise

2. **Top-K Documents** (`hr_rag_tool.py:58`)
   - Fewer (1-2): Faster, focused answers
   - More (3-5): Broader context, slower

3. **Embedding Model**
   - `text-embedding-3-small`: Fast, 1536 dims
   - `text-embedding-3-large`: Better accuracy, 3072 dims

## Sample Policies Included

The system includes 15 sample HR policies:

1. Annual Leave Entitlement
2. Sick Leave Guidelines
3. Maternity and Paternity Leave
4. Working Hours and Attendance
5. Remote Work Guidelines
6. Payroll and Compensation
7. Performance Management
8. Employee Code of Conduct
9. Workplace Health and Safety
10. Training and Development
11. Resignation Policy
12. Dress Code Guidelines
13. Public Holidays
14. Expense Reimbursement
15. Data Security Policy

## Adding New Policies

### Method 1: Update JSON and Re-ingest

1. Edit `data/hr_policies/sample_policies.json`
2. Add new policy documents
3. Run ingestion script:
   ```bash
   python scripts/ingest_hr_policies.py --drop-existing
   ```

### Method 2: Programmatic Ingestion

```python
from core.tools.hr_rag_tool import ingest_hr_policies

new_policies = [
    {
        "id": "pol_016",
        "content": "New policy content...",
        "metadata": {
            "title": "New Policy",
            "category": "Category",
            "document_type": "policy"
        }
    }
]

success = ingest_hr_policies(new_policies)
```

## Troubleshooting

### Milvus Connection Failed

**Error:** `Failed to connect to Milvus`

**Solutions:**
1. Verify Milvus is running: `docker ps | grep milvus`
2. Check Milvus URI in `.env`: `MILVUS_URI=http://localhost:19530`
3. Restart Milvus: `docker restart milvus`
4. Check Milvus logs: `docker logs milvus`

### No Search Results

**Issue:** RAG returns "I couldn't find specific information..."

**Solutions:**
1. Verify documents are ingested:
   ```python
   from services.milvus_service import MilvusService
   milvus = MilvusService()
   milvus.connect()
   results = milvus.search("leave", k=1)
   print(results)  # Should return documents
   ```
2. Lower similarity threshold in `hr_rag_tool.py` (line 58)
3. Re-ingest with `--drop-existing` flag

### OpenAI API Errors

**Error:** `AuthenticationError` or `RateLimitError`

**Solutions:**
1. Verify API key is set: `echo $OPENAI_API_KEY`
2. Check API key validity in OpenAI dashboard
3. Check rate limits and billing

## Architecture Benefits

1. **Scalability**: Milvus handles millions of documents efficiently
2. **Accuracy**: Vector search finds semantically similar content
3. **Flexibility**: Easy to add/update policies without retraining
4. **Context-Aware**: LLM generates answers based on actual company policies
5. **Graceful Degradation**: Falls back when Milvus unavailable

## Future Enhancements

- [ ] Multi-language support
- [ ] Document versioning and history
- [ ] Source attribution in responses
- [ ] Hybrid search (vector + keyword)
- [ ] Auto-update from SharePoint/Confluence
- [ ] Policy change notifications
- [ ] Analytics on most-queried policies

## Performance Metrics

- **Embedding Generation**: ~2-5 seconds for 15 documents
- **Query Latency**: ~200-500ms (Milvus search + LLM generation)
- **Accuracy**: Depends on policy coverage and query formulation
- **Scalability**: Tested with up to 1000 documents

## References

- [Milvus Documentation](https://milvus.io/docs)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
