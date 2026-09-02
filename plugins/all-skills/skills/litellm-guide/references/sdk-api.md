# LiteLLM SDK API

## Базовый chat completion

```python
from litellm import completion
import os

os.environ["OPENAI_API_KEY"] = "..."

response = completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.choices[0].message.content)
```

Модель обычно задается как `<provider>/<model-or-deployment>`, например `openai/gpt-4o`, `anthropic/...`, `vertex_ai/...`, `bedrock/...`, `azure/<deployment>`, `ollama/<model>`.

## Streaming

```python
for chunk in completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "Write a haiku"}],
    stream=True,
):
    print(chunk.choices[0].delta.content or "", end="")
```

Streaming chunks используют OpenAI-compatible chunk shape. Для async используй `acompletion`.

## Responses API

Используй `responses()`/`aresponses()` для OpenAI Responses-style workflows, agent/tool style payloads и провайдеров, где endpoint поддержан. Проверяй provider docs и `provider_endpoints_support.json` перед обещанием поддержки.

## Embeddings, image, audio

- `embedding()` / `aembedding()` — embeddings.
- `image_generation()` / async variants — image generation.
- `transcription()` / `atranscription()` — audio transcription.
- `speech()` / async variants — text-to-speech.
- `moderation()` / `amoderation()` — moderation.

Всегда проверяй provider-specific docs: не каждый provider поддерживает каждый endpoint.

## Ошибки

LiteLLM мапит provider errors в OpenAI-style exceptions. Типовой pattern:

```python
import litellm

try:
    litellm.completion(model="anthropic/claude-...", messages=[{"role": "user", "content": "Hi"}])
except litellm.AuthenticationError:
    ...
except litellm.RateLimitError:
    ...
except litellm.APIError:
    ...
```

## Observability callbacks

Для простых интеграций можно задать callbacks:

```python
import litellm
litellm.success_callback = ["langfuse", "mlflow", "helicone"]
```

Для enterprise/proxy deployments чаще настраивай callbacks в gateway config, чтобы аудит был централизованным.

## SDK Router

`Router` нужен для нескольких deployments одного logical model, retries/fallbacks/load balancing внутри приложения. Для platform-wide routing лучше proxy с `router_settings`.
