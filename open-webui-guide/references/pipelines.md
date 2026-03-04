# Пайплайны (Pipelines)

## Содержание
1. [Что такое пайплайны](#что-такое-пайплайны)
2. [Отличие от функций](#отличие-от-функций)
3. [Архитектура](#архитектура)
4. [Настройка](#настройка)
5. [Создание пайплайна](#создание-пайплайна)
6. [API-эндпоинты](#api-эндпоинты)
7. [Типичные сценарии](#типичные-сценарии)

---

## Что такое пайплайны

Пайплайны — это **внешние HTTP-сервисы**, которые обрабатывают запросы к моделям. В отличие от функций (работают внутри Open WebUI), пайплайны:

- Запускаются как отдельные процессы/контейнеры
- Общаются с Open WebUI по HTTP (REST)
- Могут быть написаны на любом языке
- Масштабируются независимо
- Изолированы от основного процесса

---

## Отличие от функций

| Аспект | Функции | Пайплайны |
|--------|---------|-----------|
| Где исполняются | Внутри Open WebUI | Отдельный сервис |
| Протокол | Python-вызов | HTTP REST |
| Изоляция | Нет (общий процесс) | Полная |
| Деплой | Встроены в Open WebUI | Отдельный контейнер |
| Язык | Только Python | Любой |
| Доступ к внутренним API | Полный | Нет |
| Масштабирование | С Open WebUI | Независимое |

### Когда использовать что

- **Функции** — быстрые модификации запросов/ответов, простая логика, доступ к контексту Open WebUI
- **Пайплайны** — тяжёлая обработка, изоляция, микросервисная архитектура, сторонние зависимости

---

## Архитектура

```
Пользователь → Open WebUI → [Фильтр-пайплайн inlet] → Модель/LLM
                                                          ↓
Пользователь ← Open WebUI ← [Фильтр-пайплайн outlet] ← Ответ
```

Пайплайны подключаются как дополнительные URL в списке `OPENAI_API_BASE_URLS`. Open WebUI отправляет запросы к ним по стандартному OpenAI-совместимому протоколу.

### Типы пайплайнов

1. **Filter Pipeline** — пре/пост-обработка (аналог filter-функций, но внешний)
   - `inlet` — модификация запроса перед отправкой модели
   - `outlet` — модификация ответа после получения
   - Привязка к моделям через `pipeline.valves.pipelines` (список model_id или `["*"]` для всех)
   - Приоритет через `pipeline.valves.priority`

2. **Model Pipeline** — кастомный провайдер, выглядит как модель в списке

---

## Настройка

### Подключение pipeline-сервера

Пайплайн-серверы регистрируются в Open WebUI через:
- Админ-панель → Settings → Connections → добавить URL
- Или через переменные окружения:

```env
OPENAI_API_BASE_URLS="http://localhost:11434;http://pipeline-server:9099"
OPENAI_API_KEYS="ollama-key;pipeline-api-key"
```

### Загрузка пайплайна на сервер

```bash
# Загрузить Python-файл пайплайна
POST /api/v1/pipelines/upload
Content-Type: multipart/form-data
file: pipeline.py
urlIdx: 0  # индекс сервера в OPENAI_API_BASE_URLS

# Или добавить из URL (GitHub)
POST /api/v1/pipelines/add
{
  "url": "https://github.com/user/repo/blob/main/pipeline.py",
  "urlIdx": 0
}
```

---

## Создание пайплайна

### Структура pipeline-сервера

Официальный фреймворк: [open-webui/pipelines](https://github.com/open-webui/pipelines)

```python
# pipelines/my_pipeline.py

from pydantic import BaseModel, Field
from typing import Optional, List, Generator


class Pipeline:
    class Valves(BaseModel):
        """Настройки пайплайна"""
        pipelines: List[str] = Field(
            default=["*"],
            description="Список model_id или ['*'] для всех"
        )
        priority: int = Field(
            default=0,
            description="Приоритет (меньше = раньше)"
        )
        api_key: str = Field(default="", description="API-ключ")

    def __init__(self):
        self.name = "My Pipeline"
        self.valves = self.Valves()

    async def on_startup(self):
        """Вызывается при запуске pipeline-сервера"""
        print(f"Pipeline {self.name} started")

    async def on_shutdown(self):
        """Вызывается при остановке"""
        pass

    # Для Filter Pipeline:
    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """Пре-обработка запроса"""
        return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """Пост-обработка ответа"""
        return body

    # Для Model Pipeline:
    async def pipe(self, body: dict, user: Optional[dict] = None) -> str | Generator:
        """Генерация ответа"""
        return "Response from pipeline"
```

### Запуск pipeline-сервера

```bash
# Клонируй фреймворк
git clone https://github.com/open-webui/pipelines
cd pipelines

# Помести свой пайплайн в pipelines/
cp my_pipeline.py pipelines/

# Запуск
pip install -r requirements.txt
python main.py --port 9099

# Или через Docker
docker run -d -p 9099:9099 \
  -v ./pipelines:/app/pipelines \
  ghcr.io/open-webui/pipelines:main
```

---

## API-эндпоинты

```
GET    /api/v1/pipelines/list                — список pipeline-серверов
GET    /api/v1/pipelines/                    — список активных пайплайнов
POST   /api/v1/pipelines/upload              — загрузить файл пайплайна
POST   /api/v1/pipelines/add                 — добавить из URL
DELETE /api/v1/pipelines/delete              — удалить пайплайн
GET    /api/v1/pipelines/{id}/valves         — настройки пайплайна
POST   /api/v1/pipelines/{id}/valves/update  — обновить настройки
```

---

## Типичные сценарии

### 1. Логирование всех запросов
Filter-пайплайн, который записывает все запросы и ответы в внешнюю БД/сервис.

### 2. Content moderation
Filter-пайплайн с inlet-хуком, который проверяет запрос на запрещённый контент через стороннее API и блокирует при необходимости.

### 3. Кастомный LLM-провайдер
Model-пайплайн, который выступает адаптером для нестандартного API (например, корпоративный LLM без OpenAI-совместимого интерфейса).

### 4. RAG-обогащение
Filter-пайплайн, который перед отправкой запроса модели ищет релевантные документы во внешней системе и добавляет их в контекст.

### 5. A/B-тестирование моделей
Model-пайплайн, который случайно маршрутизирует запросы между несколькими моделями и собирает метрики.
