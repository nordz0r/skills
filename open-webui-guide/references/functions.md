# Функции (Functions)

## Содержание
1. [Что такое функции](#что-такое-функции)
2. [Типы функций](#типы-функций)
3. [Структура функции](#структура-функции)
4. [Valves (настройки)](#valves)
5. [Примеры кода](#примеры-кода)
6. [Жизненный цикл](#жизненный-цикл)
7. [API-эндпоинты](#api-эндпоинты)
8. [Подводные камни](#подводные-камни)

---

## Что такое функции

Функции — это Python-модули, которые исполняются **внутри** процесса Open WebUI. Они позволяют модифицировать запросы/ответы, создавать кастомные провайдеры моделей и добавлять действия в UI.

В отличие от пайплайнов (внешние HTTP-сервисы), функции:
- Работают в том же процессе, что и Open WebUI
- Имеют доступ к внутренним API и контексту
- Не требуют отдельного деплоя
- Загружаются динамически (hot-reload)

---

## Типы функций

### 1. Filter (Фильтр)

Перехватывает запросы и ответы модели. Два хука:

- **inlet** — вызывается ПЕРЕД отправкой запроса модели. Можно модифицировать промпт, добавить контекст, проверить/отклонить запрос.
- **outlet** — вызывается ПОСЛЕ получения ответа. Можно модифицировать ответ, добавить метаданные, логировать.

Фильтры выполняются в порядке приоритета (поле `priority`). Можно включить/выключить глобально (`is_global`) или привязать к конкретным моделям.

### 2. Pipe (Труба/Провайдер)

Кастомный провайдер модели. Pipe-функция сама генерирует ответ — Open WebUI показывает её как отдельную «модель» в списке. Используй для:
- Обёрток над нестандартными API
- Агрегации нескольких моделей
- Кастомной логики генерации

### 3. Action (Действие)

Кнопка действия в UI чата. При нажатии пользователем вызывается Python-код с доступом к контексту сообщения. Примеры:
- «Перевести на русский»
- «Создать задачу в Jira»
- «Сохранить в заметки»

---

## Структура функции

### Минимальный шаблон (Filter)

```python
"""
title: My Filter
author: Your Name
version: 0.1.0
"""

from pydantic import BaseModel, Field
from typing import Optional


class Filter:
    class Valves(BaseModel):
        """Настройки, доступные администратору"""
        enabled: bool = Field(default=True, description="Включить фильтр")
        max_tokens: int = Field(default=4096, description="Максимум токенов")

    class UserValves(BaseModel):
        """Настройки, доступные каждому пользователю"""
        language: str = Field(default="ru", description="Язык ответа")

    def __init__(self):
        self.valves = self.Valves()

    async def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """Вызывается перед отправкой запроса модели"""
        # body содержит: messages, model, stream, и т.д.
        if self.valves.enabled:
            # Пример: добавить системное сообщение
            body["messages"].insert(0, {
                "role": "system",
                "content": f"Отвечай на языке: {self.valves.language}"
            })
        return body

    async def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """Вызывается после получения ответа"""
        # body содержит ответ модели
        return body
```

### Минимальный шаблон (Pipe)

```python
"""
title: Custom Model
author: Your Name
version: 0.1.0
"""

from pydantic import BaseModel, Field
from typing import Optional, Generator


class Pipe:
    class Valves(BaseModel):
        api_key: str = Field(default="", description="API ключ внешнего сервиса")
        api_url: str = Field(default="https://api.example.com", description="URL API")

    def __init__(self):
        self.valves = self.Valves()
        # Определяет имя модели в списке. Может быть списком для нескольких моделей:
        # self.pipes = [{"id": "model-a", "name": "Model A"}, {"id": "model-b", "name": "Model B"}]

    def pipes(self) -> list[dict]:
        """Возвращает список моделей, предоставляемых этим pipe"""
        return [{"id": "my-custom-model", "name": "My Custom Model"}]

    async def pipe(self, body: dict, __user__: Optional[dict] = None) -> str | Generator:
        """Генерирует ответ"""
        messages = body.get("messages", [])
        # Реализуй вызов внешнего API
        # Для стриминга возвращай генератор, для обычного — строку
        return "Ответ от кастомной модели"
```

### Минимальный шаблон (Action)

```python
"""
title: Translate to Russian
author: Your Name
version: 0.1.0
"""

from pydantic import BaseModel


class Action:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()

    async def action(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__=None,
    ) -> Optional[dict]:
        """Вызывается при нажатии кнопки действия"""
        # body содержит контекст текущего сообщения
        message = body.get("messages", [])[-1]

        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Перевожу...", "done": False},
                }
            )

        # ... выполни действие ...

        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Готово!", "done": True},
                }
            )
```

---

## Valves

Valves — это механизм конфигурации функций через Pydantic-модели.

### Два уровня

1. **Valves** (класс-уровень) — настраиваются администратором через UI или API
2. **UserValves** — настраиваются каждым пользователем индивидуально

### Поддерживаемые типы полей

```python
class Valves(BaseModel):
    # Простые типы
    enabled: bool = Field(default=True)
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=4096)
    api_key: str = Field(default="")

    # Списки
    allowed_models: list[str] = Field(default=["gpt-4", "gpt-3.5-turbo"])

    # Enum через Literal
    mode: Literal["fast", "accurate"] = Field(default="fast")
```

### Динамические опции (dropdown)

Valves поддерживают динамические выпадающие списки через метод в классе функции.

---

## Специальные параметры

В методах `inlet`, `outlet`, `pipe`, `action` доступны специальные параметры через двойное подчёркивание:

| Параметр | Описание |
|----------|----------|
| `__user__` | Словарь с данными пользователя: `{id, email, name, role}` |
| `__event_emitter__` | Функция для отправки событий в UI (статус, прогресс) |
| `__event_call__` | Функция для запроса ввода от пользователя |
| `__id__` | ID функции |
| `__model__` | Информация о текущей модели |
| `__chat_id__` | ID текущего чата |
| `__message_id__` | ID текущего сообщения |

---

## Жизненный цикл

### Загрузка
1. Код функции хранится в БД (таблица `function`)
2. При активации Open WebUI динамически импортирует Python-модуль
3. Выполняется автозамена импортов для безопасности
4. Создаётся экземпляр класса

### Исполнение (Filter)
```
Запрос пользователя
  → Filter 1 inlet (priority=0)
  → Filter 2 inlet (priority=1)
  → Модель генерирует ответ
  → Filter 2 outlet
  → Filter 1 outlet
  → Ответ пользователю
```

### Глобальные функции
`is_global=True` — применяется ко ВСЕМ моделям. Иначе привязывается к конкретным моделям через UI.

---

## API-эндпоинты

```
GET    /api/v1/functions/              — список функций
POST   /api/v1/functions/create        — создать функцию
POST   /api/v1/functions/sync          — массовая синхронизация
POST   /api/v1/functions/load/url      — загрузить с GitHub
GET    /api/v1/functions/id/{id}       — получить функцию
POST   /api/v1/functions/id/{id}/update     — обновить
DELETE /api/v1/functions/id/{id}/delete      — удалить
POST   /api/v1/functions/id/{id}/toggle     — вкл/выкл
POST   /api/v1/functions/id/{id}/toggle/global  — глобальный режим
GET    /api/v1/functions/id/{id}/valves          — текущие valves
POST   /api/v1/functions/id/{id}/valves/update   — обновить valves
GET    /api/v1/functions/id/{id}/valves/user     — пользовательские valves
POST   /api/v1/functions/id/{id}/valves/user/update — обновить user valves
```

---

## Подводные камни

### 1. ID функции — только lowercase + underscore
```
my_filter     ✓
My-Filter     ✗
my filter     ✗
```

### 2. Bcrypt-ограничение модулей
Код функций исполняется в основном процессе — плохо написанная функция может:
- Заблокировать event loop (sync I/O без async)
- Утечь память
- Упасть и повлиять на весь сервис

Всегда используй `async` для I/O операций.

### 3. Порядок фильтров имеет значение
Фильтры с меньшим `priority` исполняются первыми. Если один фильтр модифицирует `messages`, следующий получит уже изменённую версию.

### 4. Auto-import replacement
Open WebUI автоматически заменяет некоторые импорты для безопасности. Если твой импорт не работает — это может быть причиной.

### 5. Hot reload
После обновления кода функции через UI, она перезагружается автоматически. Но если функция хранит состояние в `__init__`, оно будет сброшено.
