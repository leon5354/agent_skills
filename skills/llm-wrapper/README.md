# LLM Wrapper Skill

Unified interface for multiple LLM providers.

## What It Does

- Single interface for Ollama, OpenAI, Anthropic, and Google
- Automatic retry with exponential backoff
- JSON mode for structured output
- Graceful fallback when litellm unavailable

## Supported Providers

| Provider | Requirements | Models |
|----------|-------------|--------|
| Ollama | Local installation | llama3, mistral, qwen2, ... |
| OpenAI | API key | gpt-4o-mini, gpt-4o |
| Anthropic | API key | claude-3-haiku, claude-3-sonnet |
| Google | API key | gemini-2.0-flash, gemini-2.5-pro |

## Usage

```python
from skills.llm_wrapper.skill import complete, provider_info

# Check current setup
info = provider_info()
print(f"Using: {info['provider']} / {info['model']}")

# Simple completion
response = complete(
    prompt="What is machine learning?",
    system="You are a helpful assistant."
)

# JSON mode (for structured output)
response = complete(
    prompt='Classify: "Great product!"',
    system="Output JSON with 'label' and 'confidence'",
    json_mode=True
)
```

## Configuration

Edit `config.py`:

```python
# Choose provider
LLM_PROVIDER = "ollama"  # ollama, openai, anthropic, google

# Behavior
TEMPERATURE = 0.1        # Lower = more consistent
MAX_TOKENS = 512         # Max response length
RETRY_ATTEMPTS = 3       # Retry count
```

Or use `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

## Ollama Setup (Free, Local)

```bash
# Install
curl -fsSL https://ollama.com/install.sh | sh

# Download model
ollama pull llama3

# Run
ollama serve
```

## Dependencies

- `litellm` (recommended for multi-provider)
- `requests` (fallback for Ollama)
- `pydantic` (optional)
