# Vercel AI Gateway API Reference

## Authentication
```python
import os

# Read API key from environment
api_key = os.environ["AI_GATEWAY_API_KEY"]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

## Endpoint
```
POST https://gateway.vercel.com/v1/chat/completions
```

## Request Format
```python
import requests
import json

payload = {
    "model": "openai/gpt-4o-mini",  # Format: provider/model
    "messages": [
        {"role": "system", "content": "System prompt here"},
        {"role": "user", "content": "User message here"}
    ],
    "temperature": 0.1,
    "max_tokens": 2000
}

url = "https://gateway.vercel.com/v1/chat/completions"
response = requests.post(url, headers=headers, json=payload)
result = response.json()
```

## Response Format
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "{\"nodes\": [...]}"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 450,
    "completion_tokens": 320,
    "total_tokens": 770
  }
}
```

## Parsing with Error Handling
```python
import json
import re

def parse_llm_response(response_text):
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Strip markdown code blocks if present
    text = response_text.strip()
    if text.startswith("```"):
        # Remove ```json or ``` wrapper
        text = re.sub(r'^```(?:json)?\n', '', text)
        text = re.sub(r'\n```$', '', text)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}\nResponse: {text[:200]}...")

# Usage
assistant_message = result["choices"][0]["message"]["content"]
extracted_data = parse_llm_response(assistant_message)
nodes = extracted_data["nodes"]
```

## Token Counting
```python
import tiktoken

def count_tokens(text, model="cl100k_base"):
    """Count tokens using tiktoken (OpenAI tokenizer)."""
    encoding = tiktoken.get_encoding(model)
    return len(encoding.encode(text))
```
