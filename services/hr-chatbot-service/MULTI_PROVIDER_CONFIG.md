# Multi-Provider LLM and Embedding Configuration

## Overview

The HR Chatbot Service now supports multiple LLM and embedding providers, giving you flexibility to choose the best provider for your use case based on cost, performance, privacy, or availability.

## Supported Providers

### LLM Providers
- **OpenAI** - GPT-4, GPT-4 Turbo, GPT-3.5 models
- **Azure OpenAI** - Enterprise-grade OpenAI models via Azure
- **Anthropic** - Claude 3.5, Claude 3 Opus/Sonnet/Haiku models
- **Google** - Gemini Pro, Gemini 1.5 Pro/Flash models
- **Ollama** - Local/self-hosted open source models (Llama 3, Mistral, etc.)

### Embedding Providers
- **OpenAI** - text-embedding-3-small/large, ada-002
- **Azure OpenAI** - OpenAI embeddings via Azure
- **Anthropic** - Voyage AI embeddings (voyage-2, voyage-lite)
- **Google** - Google text-embedding-004, embedding-001
- **Ollama** - Local embeddings (nomic-embed-text, mxbai-embed-large)

## Configuration Changes

### Updated Files

#### 1. [core/config.py](core/config.py)

**New Configuration Fields:**

```python
# LLM Provider Selection
llm_provider: Literal["openai", "azure", "anthropic", "google", "ollama"]

# OpenAI Configuration
openai_api_key: Optional[str]
openai_base_url: Optional[str]
openai_organization: Optional[str]

# Azure OpenAI Configuration
azure_openai_api_key: Optional[str]
azure_openai_endpoint: Optional[str]
azure_openai_api_version: str
azure_openai_deployment_name: Optional[str]
azure_openai_embedding_deployment_name: Optional[str]

# Anthropic Configuration
anthropic_api_key: Optional[str]
anthropic_base_url: Optional[str]

# Google Configuration
google_api_key: Optional[str]
google_project_id: Optional[str]
google_location: str

# Ollama Configuration
ollama_base_url: str

# Embedding Configuration
embedding_provider: Literal["openai", "azure", "anthropic", "google", "ollama"]
embedding_model: str
embedding_dimensions: Optional[int]
```

**Enhanced Validation:**
- Provider-specific API key validation
- Model validation for each provider
- Azure deployment name requirements
- Support for custom base URLs and endpoints

#### 2. [.env.example](.env.example)

Comprehensive environment configuration template with:
- All provider configurations documented
- Model options for each provider
- 6 real-world configuration examples
- Inline documentation for each setting

## Usage Examples

### Example 1: OpenAI (Default)

```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=sk-...
```

**Use Case:** Production deployments with OpenAI API access

### Example 2: Anthropic Claude

```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

**Use Case:** High-quality responses with Claude, OpenAI embeddings

### Example 3: Azure OpenAI (Enterprise)

```bash
LLM_PROVIDER=azure
EMBEDDING_PROVIDER=azure
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt4-deployment
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=embedding-deployment
```

**Use Case:** Enterprise deployments with Azure compliance requirements

### Example 4: Google Gemini

```bash
LLM_PROVIDER=google
LLM_MODEL=gemini-1.5-pro
EMBEDDING_PROVIDER=google
EMBEDDING_MODEL=text-embedding-004
GOOGLE_API_KEY=...
```

**Use Case:** Google Cloud ecosystem integration

### Example 5: Ollama (Local/Self-Hosted)

```bash
LLM_PROVIDER=ollama
LLM_MODEL=llama3
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://localhost:11434
```

**Use Case:** Privacy-focused, air-gapped, or cost-sensitive deployments

### Example 6: Mixed Providers

```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

**Use Case:** Best-of-breed approach (Claude for chat, OpenAI for embeddings)

## Supported Models

### OpenAI Models
- `gpt-4o` - Latest GPT-4 Optimized
- `gpt-4o-mini` - Cost-effective GPT-4 Optimized (recommended)
- `gpt-4-turbo` - Fast GPT-4
- `gpt-4` - Standard GPT-4
- `gpt-3.5-turbo` - Fast and cheap
- `gpt-3.5-turbo-16k` - Larger context

### Anthropic Models
- `claude-3-5-sonnet-20241022` - Latest Claude (recommended)
- `claude-3-5-sonnet-20240620` - Previous Sonnet
- `claude-3-opus-20240229` - Most capable
- `claude-3-sonnet-20240229` - Balanced
- `claude-3-haiku-20240307` - Fastest, cheapest
- `claude-2.1`, `claude-2.0` - Legacy

### Google Models
- `gemini-1.5-pro` - Most capable (recommended)
- `gemini-1.5-flash` - Fast and efficient
- `gemini-pro` - Standard
- `gemini-pro-vision` - With vision
- `gemini-1.0-pro` - Legacy

### OpenAI Embeddings
- `text-embedding-3-small` - 1536 dims (recommended)
- `text-embedding-3-large` - 3072 dims
- `text-embedding-ada-002` - 1536 dims (legacy)

### Anthropic Embeddings (Voyage AI)
- `voyage-2` - High quality (recommended)
- `voyage-lite-02-instruct` - Instruction-following

### Google Embeddings
- `text-embedding-004` - Latest (recommended)
- `embedding-001` - Standard
- `embedding-gecko-001` - Legacy

### Ollama Embeddings
- `nomic-embed-text` - General purpose (recommended)
- `mxbai-embed-large` - High quality
- `all-minilm` - Fast and small

## Migration Guide

### From Old Configuration

**Old (.env):**
```bash
OPENAI_API_KEY=sk-...
OPENAI_TEMPERATURE=0
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini
```

**New (.env):**
```bash
# Provider Selection
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai

# Models
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.0
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# API Keys
OPENAI_API_KEY=sk-...
```

### Key Changes
1. Add `LLM_PROVIDER` and `EMBEDDING_PROVIDER` fields
2. Rename `OPENAI_TEMPERATURE` to `LLM_TEMPERATURE`
3. Add `EMBEDDING_DIMENSIONS` field
4. All other fields remain compatible

## Validation

The configuration system includes comprehensive validation:

1. **Provider Validation**
   - Validates required API keys for each provider
   - Checks Azure deployment names
   - Verifies endpoint URLs

2. **Model Validation**
   - Ensures model is compatible with selected provider
   - Validates model names against known models
   - Allows custom models for Azure and Ollama

3. **Configuration Validation**
   - Type checking for all fields
   - Range validation for numeric values
   - URL format validation

## Testing Configuration

Test your configuration:

```bash
cd services/hr-chatbot-service
python3 -c "from core.config import Settings; s = Settings(); print(f'LLM: {s.llm_provider}/{s.llm_model}')"
```

## Requirements

All LangChain provider packages are already included in [requirements.txt](requirements.txt):

```
langchain==1.1.0
langchain-openai==1.1.0
langchain-anthropic==1.2.0
langchain-google-genai==3.2.0
langchain-ollama==1.0.0
```

No changes to requirements.txt were needed - all dependencies were already present.

## Next Steps

1. Copy `.env.example` to `.env`
2. Choose your preferred LLM and embedding providers
3. Add required API keys for your selected providers
4. Configure model names and other settings
5. Test the configuration
6. Update your service initialization code to use the new providers

## Benefits

- **Flexibility**: Switch providers without code changes
- **Cost Optimization**: Use cheaper providers for development
- **Privacy**: Run fully local with Ollama
- **Redundancy**: Easy fallback to alternative providers
- **Best-of-Breed**: Mix providers (e.g., Claude + OpenAI embeddings)
- **Compliance**: Use Azure for regulated industries
- **Future-Proof**: Easy to add new providers

## Support

For issues or questions about multi-provider configuration:
1. Check `.env.example` for configuration examples
2. Review this guide for provider-specific settings
3. Ensure API keys are valid and have proper permissions
4. Verify models are spelled exactly as shown above
