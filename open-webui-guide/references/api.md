# API-справочник

## Содержание
1. [Аутентификация API](#аутентификация-api)
2. [Базовый URL](#базовый-url)
3. [Роутеры по категориям](#роутеры-по-категориям)
4. [OpenAI-совместимый API](#openai-совместимый-api)
5. [Примеры запросов](#примеры-запросов)

---

## Аутентификация API

Все API-запросы (кроме `/api/v1/auths/signin` и `/api/v1/auths/signup`) требуют авторизации:

```bash
# Через JWT-токен (получается при логине)
Authorization: Bearer eyJhbGciOiJI...

# Через API-ключ
Authorization: Bearer sk-xxxxxxxx...
```

---

## Базовый URL

```
http://localhost:8080/api/v1/
```

В Docker-контейнере порт по умолчанию — `8080`, часто маппится на `3000`.

---

## Роутеры по категориям

### Аутентификация (`/api/v1/auths/`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| POST | `/signin` | Вход по паролю | Публичный |
| POST | `/signup` | Регистрация | Публичный |
| POST | `/ldap` | Вход через LDAP | Публичный |
| GET | `/oauth/{provider}/authorize` | OAuth авторизация | Публичный |
| POST | `/logout` | Выход (отзыв токена) | Авторизованный |
| POST | `/api-key` | Создать API-ключ | Авторизованный |
| DELETE | `/api-key` | Удалить API-ключ | Авторизованный |
| PATCH | `/profile` | Обновить профиль | Авторизованный |
| PATCH | `/password/update` | Сменить пароль | Авторизованный |

### Пользователи (`/api/v1/users/`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| GET | `/` | Список пользователей | Admin |
| GET | `/{id}` | Профиль пользователя | Admin |
| POST | `/{id}/update` | Обновить пользователя | Admin |
| DELETE | `/{id}` | Удалить пользователя | Admin |
| GET | `/me` | Текущий пользователь | Авторизованный |
| POST | `/{id}/role` | Изменить роль | Admin |

### Чаты (`/api/v1/chats/`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| GET | `/` | Список чатов | Авторизованный |
| POST | `/new` | Создать чат | Авторизованный |
| GET | `/{id}` | Получить чат | Владелец |
| POST | `/{id}` | Обновить чат | Владелец |
| DELETE | `/{id}` | Удалить чат | Владелец |
| GET | `/all` | Все чаты (admin) | Admin |
| POST | `/{id}/archive` | Архивировать | Владелец |
| POST | `/{id}/share` | Поделиться чатом | Владелец |
| POST | `/{id}/clone` | Клонировать чат | Авторизованный |
| GET | `/tags` | Теги чатов | Авторизованный |

### Модели (`/api/v1/models/`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| GET | `/` | Список моделей | Авторизованный |
| POST | `/create` | Создать модель | Admin |
| GET | `/{id}` | Информация о модели | Авторизованный |
| POST | `/{id}/update` | Обновить модель | Admin |
| DELETE | `/{id}/delete` | Удалить модель | Admin |

### Функции (`/api/v1/functions/`)

См. `functions.md` для полного списка.

### Пайплайны (`/api/v1/pipelines/`)

См. `pipelines.md` для полного списка.

### Базы знаний (`/api/v1/knowledge/`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| GET | `/` | Список баз знаний | Авторизованный |
| POST | `/` | Создать базу | Авторизованный |
| GET | `/{id}` | Информация о базе | Авторизованный |
| POST | `/{id}/update` | Обновить | Владелец/Admin |
| DELETE | `/{id}/delete` | Удалить | Владелец/Admin |
| POST | `/{id}/files` | Добавить файл | Владелец/Admin |
| GET | `/{id}/files` | Файлы базы | Авторизованный |
| DELETE | `/{id}/files/{file_id}` | Удалить файл | Владелец/Admin |

### Файлы (`/api/v1/files/`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| POST | `/` | Загрузить файл | Авторизованный |
| GET | `/` | Список файлов | Авторизованный |
| GET | `/{id}` | Метаданные файла | Авторизованный |
| GET | `/{id}/content` | Содержимое файла | Авторизованный |
| DELETE | `/{id}` | Удалить файл | Владелец/Admin |

### Промпты (`/api/v1/prompts/`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| GET | `/` | Список промптов | Авторизованный |
| POST | `/create` | Создать промпт | Авторизованный |
| GET | `/{command}` | Получить промпт | Авторизованный |
| POST | `/{command}/update` | Обновить промпт | Владелец/Admin |
| DELETE | `/{command}/delete` | Удалить промпт | Владелец/Admin |

### Tools (Инструменты) (`/api/v1/tools/`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| GET | `/` | Список инструментов | Авторизованный |
| POST | `/create` | Создать инструмент | Admin |
| GET | `/id/{id}` | Информация | Авторизованный |
| POST | `/id/{id}/update` | Обновить | Admin |
| DELETE | `/id/{id}/delete` | Удалить | Admin |

### Каналы (`/api/v1/channels/`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| GET | `/` | Список каналов | Авторизованный |
| POST | `/create` | Создать канал | Admin |
| GET | `/{id}` | Информация | Участник |
| POST | `/{id}/update` | Обновить | Admin |
| DELETE | `/{id}/delete` | Удалить | Admin |
| GET | `/{id}/messages` | Сообщения канала | Участник |
| POST | `/{id}/messages/post` | Отправить сообщение | Участник |

### Группы (`/api/v1/groups/`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| GET | `/` | Список групп | Авторизованный |
| POST | `/create` | Создать группу | Admin |
| GET | `/{id}` | Информация | Авторизованный |
| POST | `/{id}/update` | Обновить | Admin |
| DELETE | `/{id}/delete` | Удалить | Admin |

### Конфигурация (`/api/v1/configs/`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| GET | `/` | Текущая конфигурация | Admin |
| POST | `/update` | Обновить конфигурацию | Admin |

### Другие роутеры

| Роутер | Путь | Назначение |
|--------|------|------------|
| Audio | `/api/v1/audio/` | TTS/STT (синтез и распознавание речи) |
| Images | `/api/v1/images/` | Генерация изображений (DALL-E, Stable Diffusion) |
| Retrieval | `/api/v1/retrieval/` | Веб-поиск, обработка документов |
| Memories | `/api/v1/memories/` | Пользовательские воспоминания |
| Notes | `/api/v1/notes/` | Заметки |
| Folders | `/api/v1/folders/` | Папки для организации |
| Tags | `/api/v1/tags/` | Теги |
| Evaluations | `/api/v1/evaluations/` | Оценка моделей |
| Analytics | `/api/v1/analytics/` | Аналитика использования |
| SCIM | `/api/v1/scim/` | SCIM 2.0 провизия |
| Terminals | `/api/v1/terminals/` | Исполнение кода |

---

## OpenAI-совместимый API

Open WebUI предоставляет OpenAI-совместимый API, что позволяет использовать его как drop-in replacement:

```bash
# Chat Completions
curl -X POST http://localhost:8080/api/chat/completions \
  -H "Authorization: Bearer sk-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1",
    "messages": [{"role": "user", "content": "Привет!"}],
    "stream": false
  }'

# List Models
curl http://localhost:8080/api/models \
  -H "Authorization: Bearer sk-your-api-key"
```

Это позволяет подключать Open WebUI к любым приложениям, которые умеют работать с OpenAI API (LangChain, AutoGen, и т.д.).

---

## Примеры запросов

### Создать чат и отправить сообщение

```python
import requests

BASE = "http://localhost:8080/api/v1"
TOKEN = "your-jwt-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Создать чат
chat = requests.post(f"{BASE}/chats/new", json={
    "chat": {"title": "Тестовый чат", "messages": []}
}, headers=headers).json()

# Отправить сообщение через OpenAI-совместимый API
response = requests.post("http://localhost:8080/api/chat/completions", json={
    "model": "llama3.1",
    "messages": [{"role": "user", "content": "Что такое Python?"}],
    "stream": False
}, headers=headers).json()
```

### Загрузить файл в knowledge base

```python
# 1. Загрузить файл
with open("document.pdf", "rb") as f:
    file_resp = requests.post(f"{BASE}/files/",
        files={"file": f},
        headers=headers
    ).json()

# 2. Создать knowledge base
kb = requests.post(f"{BASE}/knowledge/", json={
    "name": "Документация",
    "description": "Проектная документация"
}, headers=headers).json()

# 3. Добавить файл в knowledge base
requests.post(f"{BASE}/knowledge/{kb['id']}/files", json={
    "file_id": file_resp["id"]
}, headers=headers)
```
