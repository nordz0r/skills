# Ollama SDK — Python и JavaScript

## Содержание

- [Python SDK](#python-sdk)
- [JavaScript/TypeScript SDK](#javascripttypescript-sdk)
- [Паттерн Search Agent с tool-calling](#паттерн-search-agent-с-tool-calling)

---

## Python SDK

### Установка

```bash
pip install ollama
```

### Web Search

```python
import ollama

# Простой поиск
response = ollama.web_search("что нового в ollama 2025")

for result in response["results"]:
    print(f"{result['title']}: {result['url']}")
    print(f"  {result['content'][:200]}")
```

### Web Fetch

```python
import ollama

page = ollama.web_fetch("https://docs.ollama.com/capabilities/web-search")

print(f"Заголовок: {page['title']}")
print(f"Контент: {page['content'][:500]}")
print(f"Ссылки: {len(page['links'])} найдено")
```

### Цепочка: поиск → чтение лучшего результата

```python
import ollama

# Шаг 1: поиск
search = ollama.web_search("ollama python sdk documentation")
if not search["results"]:
    print("Ничего не найдено")
    exit()

# Шаг 2: берём первый URL и получаем контент
best_url = search["results"][0]["url"]
page = ollama.web_fetch(best_url)
print(page["content"])
```

### Async-вариант

```python
import asyncio
import ollama

async def search_and_fetch(query: str) -> str:
    search = await asyncio.to_thread(ollama.web_search, query)
    if not search["results"]:
        return "Ничего не найдено"

    url = search["results"][0]["url"]
    page = await asyncio.to_thread(ollama.web_fetch, url)
    return page["content"]

result = asyncio.run(search_and_fetch("ollama api"))
```

---

## JavaScript/TypeScript SDK

### Установка

```bash
npm install ollama
```

### Web Search

```javascript
import { Ollama } from "ollama";

const client = new Ollama();

const response = await client.webSearch("новости ollama");
for (const result of response.results) {
  console.log(`${result.title}: ${result.url}`);
}
```

### Web Fetch

```javascript
import { Ollama } from "ollama";

const client = new Ollama();

const page = await client.webFetch("https://example.com");
console.log(`Заголовок: ${page.title}`);
console.log(`Контент: ${page.content.slice(0, 500)}`);
console.log(`Ссылки: ${page.links.length}`);
```

### Цепочка: поиск → чтение

```javascript
import { Ollama } from "ollama";

const client = new Ollama();

const search = await client.webSearch("ollama javascript sdk");
if (search.results.length === 0) {
  console.log("Ничего не найдено");
  process.exit(0);
}

const page = await client.webFetch(search.results[0].url);
console.log(page.content);
```

---

## Паттерн Search Agent с tool-calling

Модели с поддержкой tool-calling (Qwen 3, Llama 3 и др.) могут автономно вызывать поиск через определение инструментов.

### Определение tools

```python
web_search_tool = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current information on a topic",
        "parameters": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            }
        }
    }
}
```

### Цикл агента

```python
import json
import ollama

def handle_tool_call(tool_call):
    name = tool_call.function.name
    args = tool_call.function.arguments

    if name == "web_search":
        return ollama.web_search(args["query"])
    return {"error": f"Unknown tool: {name}"}

messages = [{"role": "user", "content": "Какая сейчас погода в Москве?"}]

# Первый вызов — модель решает, нужен ли поиск
response = ollama.chat(
    model="qwen3",
    messages=messages,
    tools=[web_search_tool],
    think=True  # включает reasoning (Qwen 3)
)

# Если модель вызвала инструмент — обрабатываем
if response.message.tool_calls:
    messages.append(response.message)

    for tool_call in response.message.tool_calls:
        result = handle_tool_call(tool_call)
        messages.append({
            "role": "tool",
            "content": json.dumps(result),
            "name": tool_call.function.name
        })

    # Финальный ответ с учётом результатов поиска
    final = ollama.chat(model="qwen3", messages=messages)
    print(final.message.content)
else:
    print(response.message.content)
```

### Рекомендации по контексту

- Результаты поиска могут занимать 1000+ токенов
- Для агентов рекомендуется контекстное окно **минимум 32 000 токенов**
- Облачные модели Ollama работают на полном контексте
- Локальные модели — проверяй `num_ctx` в параметрах модели
