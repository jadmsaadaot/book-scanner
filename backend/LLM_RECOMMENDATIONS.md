# LLM-Based Book Recommendations

The book scanner now uses **Large Language Models (LLMs)** to provide intelligent, semantic book recommendations based on user reading preferences.

## Features

✨ **Semantic Understanding** - LLMs understand themes, writing styles, and emotional tones beyond simple keyword matching

🔌 **Pluggable Providers** - Support for multiple LLM providers:
- **Google Gemini** (recommended - best cost/performance)
- **OpenAI GPT**
- **Anthropic Claude**

⚡ **Smart Caching** - In-memory cache with 1-hour TTL to reduce API calls and costs

🔄 **Automatic Fallback** - Falls back to rule-based recommendations if LLM is unavailable

💡 **Explainable** - Each recommendation includes an explanation of why it matches the user's preferences

## Configuration

Add the following environment variables to your `.env` file:

```bash
# Enable/disable LLM recommendations (default: true)
LLM_ENABLED=true

# Choose primary provider (default: google)
# Options: "openai" | "anthropic" | "google"
LLM_PROVIDER=google

# API Keys (add at least one)
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Getting API Keys

**Google Gemini (Recommended)**
- Free tier available with generous limits
- Get key: https://aistudio.google.com/app/apikey
- Cost: $0.075/$0.30 per 1M tokens (input/output)

**OpenAI**
- Get key: https://platform.openai.com/api-keys
- Cost: ~$0.15/$0.60 per 1M tokens (gpt-4o-mini)

**Anthropic Claude**
- Get key: https://console.anthropic.com/
- Cost: ~$0.25/$1.25 per 1M tokens (claude-3-5-haiku)

## How It Works

1. **User scans books** → OCR extracts titles
2. **Google Books API** → Fetches book metadata
3. **User's library** → Retrieved from database
4. **LLM analyzes** → Compares detected book against user's reading patterns
5. **Score & explanation** → Returns match score (0-1) and reasoning
6. **Cached** → Results cached for 1 hour per user library + book combination

### Provider Fallback Logic

1. Tries **configured primary provider** (from `LLM_PROVIDER`)
2. Falls back to **cheapest available** (Google → OpenAI → Anthropic)
3. If all LLMs fail → **rule-based recommendations** (original algorithm)

## Cost Estimation

Assuming average usage:
- **10 books scanned** per user per day
- **20 books in user's library**
- **~500 tokens** per LLM call

**Daily cost per user:**
- Google Gemini: ~$0.001 (essentially free with caching)
- OpenAI GPT-4o-mini: ~$0.003
- Anthropic Claude: ~$0.005

**With caching**, most requests hit the cache, reducing costs by ~80%.

## Disabling LLM Recommendations

Set in `.env`:
```bash
LLM_ENABLED=false
```

The service will automatically use the original rule-based algorithm (author matching, category overlap, ratings).

## API Response

The `/api/v1/books/scan` endpoint now includes:

```json
{
  "detected_books": [
    {
      "title": "The Name of the Wind",
      "author": "Patrick Rothfuss",
      "match_score": 0.85,
      "recommendation_explanation": "Strong match - similar epic fantasy themes to Brandon Sanderson's work in your library, complex magic systems, and literary prose style.",
      "in_library": false
    }
  ],
  "recommendations": [...]
}
```

## Cache Management

**Cache Details:**
- **Type**: In-memory TTL cache
- **Size**: 1000 entries max
- **TTL**: 1 hour
- **Key**: Hash of (user's library book IDs + detected book's google_books_id)

**Cache invalidation:**
- Automatic after 1 hour
- When user adds/removes books from library (library hash changes)
- On server restart (in-memory)

**Future improvements:**
- Add Redis for persistent, distributed caching
- Configurable TTL and cache size
- Cache warming for popular books

## Development

**Test imports:**
```bash
source .venv/bin/activate
python -c "from app.services.llm import get_llm_provider; print('✓ LLM service ready')"
```

**Check available providers:**
```python
from app.services.llm.factory import get_available_providers
print(get_available_providers())  # ['google', 'openai', 'anthropic']
```

## Architecture

```
app/services/llm/
├── __init__.py              # Public API
├── base.py                  # Abstract LLMProvider base class
├── factory.py               # Provider factory and fallback logic
└── providers/
    ├── openai.py           # OpenAI GPT implementation
    ├── anthropic.py        # Anthropic Claude implementation
    └── google.py           # Google Gemini implementation
```

## Troubleshooting

**"No LLM providers are configured"**
- Add at least one API key to `.env`

**High API costs**
- Switch to Google Gemini (cheapest)
- Reduce library size sent to LLM (current limit: 20 books)
- Increase cache TTL
- Set `LLM_ENABLED=false`

**Slow recommendations**
- LLM calls take 1-3 seconds
- Cache hits are instant
- Consider async processing for large batches

**Provider not working**
- Check API key is valid
- Verify quota/rate limits
- Check provider status page
- System will auto-fallback to other providers
