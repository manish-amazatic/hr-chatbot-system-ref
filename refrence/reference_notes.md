# Assignment Reference Notes

## Architecture Approach

### Chat Completion vs AI Assistant
- Use the **Chat Completion approach** defining the agent's system prompt & tools definition in the application side itself
- Instead of using the AI Assistant approach of OpenAI

### LLM Processor Design
Set up an LLMProcessor with the following characteristics:
- **Factory Pattern**: Dynamically connect to different LLM providers
- **Singleton Pattern**: Based on LLM provider name & model, instantiate the LLMProcessor instance and make it singleton
- This prevents recreation every time if already built

---

## Milvus Ingestion & Retriever - Practical Checklist

### 1. Create PDFs
- Use Copilot-like assistant to generate textual content and convert to PDFs
- **Suggested libraries**: Python `reportlab` or `pdfkit`
- **Filename & metadata example**: 
  - `cancellation_policy_travel.pdf`
  - `topic=travel`
  - `source=generated`

### 2. Text Extraction
- Convert PDFs to plain text
- **Suggested libraries**: `pdfminer.six` or `PyMuPDF`

### 3. Embeddings
- Choose an embedding model:
  - `sentence-transformers`
  - OpenAI embeddings
- Generate embeddings per chunk

### 4. Milvus Setup
- Create a collection (e.g., `travel_docs`)
- **Fields**:
  - `id`
  - `embedding`
  - `text`
  - `metadata` (topic, filename)

### 5. Insert Vectors
- Chunk texts (200–500 tokens)
- Embed each chunk
- Upsert into Milvus

### 6. Retriever API
Build a tool (HTTP function or local function) that:
1. Accepts query
2. Embeds query
3. Searches Milvus (top_k)
4. Returns docs & optionally a synthesized answer (using prompt + LLM)

### 7. Agent Wiring
- In Orchestrator, detect static knowledge intent → call retriever tool
- Otherwise call action agents/tools

---

## Suggested Milvus Collection Schema

```python
{
    "id": "int64, primary key",
    "embedding": "float_vector, dim = embedding_dim (e.g., 384)",
    "text": "long text / varchar (chunk content)",
    "metadata": "JSON (filename, topic, source, created_at)"
}
```

---

## How Agent Should Decide to Call RAG Tool

### Simple Heuristic

**Call RAG tool if** user query contains tokens like:
- policy
- rules
- FAQ
- how to
- guide
- manual
- terms
- details
- brochure

**Call transactional agent** if query includes action verbs:
- book
- cancel
- transfer
- apply for leave
- order

**Implementation Note**: Students should implement classifier/intent detector; a small rule-based fallback is acceptable.

---

## Example Student Deliverable Checklist

Per assignment, ensure:

- ✅ Agents implemented and orchestrator routes properly
- ✅ Mock transactional APIs implemented
- ✅ Generated 6–15 PDFs via code assistant and saved with metadata
- ✅ Extracted text and chunked content
- ✅ Embeddings generated and inserted into Milvus collection
- ✅ Retriever tool exposed (function or HTTP) and returns useful context
- ✅ Agent calls RAG tool for static queries and tools/APIs for transactional queries
- ✅ Demo script or video (2–5 minutes) showing both flows
- ✅ README explaining how to run everything locally

---

## Evaluation Rubric (Suggested)

| Category | Weight | Description |
|----------|--------|-------------|
| **Architecture & Design** | 25% | Clear agent/tool separation, orchestrator, retriever integration |
| **Milvus & Data Work** | 25% | Number of docs, proper chunking, embeddings, metadata quality |
| **Functionality** | 30% | RAG returns relevant contexts; agents correctly route queries; mock APIs function |
| **Code Quality & Documentation** | 10% | Readable code, instructions to run |
| **Demo & Edge Cases** | 10% | Shows sample queries of both static & transactional types, handles simple failures |

---

## Quick Tips / Common Pitfalls

### Data Privacy
- ⚠️ **Don't store real PII** in training docs
- Use anonymized/example data

### Chunking Strategy
- Chunk PDFs sensibly (not too large, not too small)
- **Safe chunk size**: 200–500 words

### Metadata
- Add metadata (topic) to make filtering by collection or topic easy

### Testing & Tuning
- Test retrieval relevance: manually inspect top-k responses
- Tune embedding model or chunking if needed

### Fallback Handling
- Provide a small fallback answer if RAG returns low-similarity results