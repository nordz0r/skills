# MCP-инструменты @mhalder/qdrant-mcp-server

20 инструментов + 2 ресурса. Ниже — параметры и примеры для каждого.

## Code Vectorization (5 tools)

### index_codebase

Индексирует кодовую базу: парсит файлы через tree-sitter, генерирует embeddings, сохраняет в Qdrant.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `path` | string | да | Путь к корню проекта |
| `forceReindex` | boolean | нет | Переиндексировать с нуля (игнорировать кеш хешей) |
| `extensions` | array | нет | Расширения файлов для индексации |
| `ignorePatterns` | array | нет | Паттерны для исключения |

```
index_codebase path="/home/user/project" forceReindex=false
index_codebase path="." extensions=[".ts",".tsx",".py"] ignorePatterns=["**/dist/**"]
```

Учитывает `.gitignore`, `.dockerignore`, `.contextignore`.

### search_code

Семантический поиск по проиндексированному коду.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `path` | string | да | Путь к проекту (должен быть проиндексирован) |
| `query` | string | да | Поисковый запрос на естественном языке |
| `limit` | number | нет | Количество результатов (по умолчанию 5) |
| `fileTypes` | array | нет | Фильтр по типам файлов: `[".ts", ".py"]` |
| `pathPattern` | string | нет | Фильтр по пути: `"src/api/**"` |

```
search_code path="." query="error handling in authentication" limit=10
search_code path="." query="database connection pool" fileTypes=[".go"] pathPattern="internal/**"
```

Результат: массив объектов с `filePath`, `lineNumbers`, `language`, `content`, `score`.

### reindex_changes

Инкрементальная переиндексация — обновляет только изменённые файлы (отслеживает хеши).

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `path` | string | да | Путь к проекту |

```
reindex_changes path="."
```

### get_index_status

Статус индекса: количество файлов, чанков, дата последней индексации.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `path` | string | да | Путь к проекту |

```
get_index_status path="."
```

### clear_index

Удаляет индекс (коллекцию Qdrant) для проекта.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `path` | string | да | Путь к проекту |

```
clear_index path="."
```

## Git History (5 tools)

### index_git_history

Индексирует git-коммиты: сообщения, авторы, даты, изменённые файлы, диффы.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `path` | string | да | Путь к git-репозиторию |
| `forceReindex` | boolean | нет | Переиндексировать с нуля |
| `sinceDate` | string | нет | Индексировать коммиты с даты: `"2024-01-01"` |
| `maxCommits` | number | нет | Максимум коммитов (по умолчанию 5000) |

```
index_git_history path="." sinceDate="2024-06-01" maxCommits=1000
```

Классифицирует conventional commits (feat, fix, refactor и др.).

### search_git_history

Семантический поиск по git-истории.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `path` | string | да | Путь к репозиторию |
| `query` | string | да | Поисковый запрос |
| `limit` | number | нет | Количество результатов (по умолчанию 10) |
| `commitTypes` | array | нет | Фильтр по типу: `["feat", "fix"]` |
| `authors` | array | нет | Фильтр по авторам |
| `dateFrom` | string | нет | С даты: `"2024-01-01"` |
| `dateTo` | string | нет | По дату: `"2024-12-31"` |

```
search_git_history path="." query="fix memory leak" limit=5
search_git_history path="." query="API changes" commitTypes=["feat"] authors=["alice"] dateFrom="2024-06-01"
```

### index_new_commits

Инкрементальная индексация — только новые коммиты с момента последней индексации.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `path` | string | да | Путь к репозиторию |

```
index_new_commits path="."
```

### get_git_index_status

Статус индекса git-истории.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `path` | string | да | Путь к репозиторию |

### clear_git_index

Удаляет индекс git-истории для репозитория.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `path` | string | да | Путь к репозиторию |

## Advanced Search (2 tools)

### contextual_search

Комбинированный поиск по коду и git-истории с корреляцией результатов (какие коммиты связаны с найденными файлами).

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `path` | string | да | Путь к проекту |
| `query` | string | да | Поисковый запрос |
| `codeLimit` | number | нет | Лимит результатов по коду (по умолчанию 5) |
| `gitLimit` | number | нет | Лимит результатов по git (по умолчанию 5) |
| `correlate` | boolean | нет | Связать код с коммитами (по умолчанию true) |

```
contextual_search path="." query="rate limiting implementation" codeLimit=5 gitLimit=5 correlate=true
```

### federated_search

Поиск по нескольким репозиториям с RRF-ранжированием (Reciprocal Rank Fusion).

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `paths` | string[] | да | Массив путей к репозиториям |
| `query` | string | да | Поисковый запрос |
| `searchType` | string | нет | Тип: `"code"`, `"git"`, `"both"` (по умолчанию `"both"`) |
| `limit` | number | нет | Общий лимит результатов (по умолчанию 20) |

```
federated_search paths=["/project-a", "/project-b", "/shared-lib"] query="authentication middleware" searchType="code" limit=10
```

## Collection Management (4 tools)

### create_collection

Создаёт коллекцию Qdrant вручную (обычно коллекции создаются автоматически при индексации).

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `name` | string | да | Имя коллекции |
| `distance` | string | нет | Метрика: Cosine (по умолчанию), Euclid, Dot |
| `enableHybrid` | boolean | нет | Включить BM25 для hybrid search |

### list_collections

Список всех коллекций. Без параметров.

### get_collection_info

Информация о коллекции: количество точек, размерность, метрика.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `name` | string | да | Имя коллекции |

### delete_collection

Удаляет коллекцию.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `name` | string | да | Имя коллекции |

## Document Operations (4 tools)

Низкоуровневые операции с документами — для кастомных сценариев (не для поиска по коду).

### add_documents

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `collection` | string | да | Имя коллекции |
| `documents` | array | да | Массив `{id, text, metadata?}` |

### semantic_search

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `collection` | string | да | Имя коллекции |
| `query` | string | да | Поисковый запрос |
| `limit` | number | нет | Лимит результатов (по умолчанию 5) |
| `filter` | object | нет | Фильтр по metadata |

### hybrid_search

Как `semantic_search`, но с BM25 + RRF. Коллекция должна быть создана с `enableHybrid: true`.

### delete_documents

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `collection` | string | да | Имя коллекции |
| `ids` | array | да | Массив ID документов |

## MCP Resources (2)

- `qdrant://collections` — список всех коллекций
- `qdrant://collection/{name}` — детали конкретной коллекции
