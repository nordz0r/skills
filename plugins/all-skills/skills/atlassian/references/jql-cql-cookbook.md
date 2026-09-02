# JQL / CQL Cookbook: готовые запросы

Проверенные запросы для `jira_search` (JQL) и `confluence_search` (CQL).
Синтаксис одинаков для Cloud и Data Center, если не указано иное.

## Jira: JQL

### Мои задачи

```jql
assignee = currentUser() AND status != Done ORDER BY updated DESC
```

```python
from scripts.jira_search import jira_search
jira_search(jql="assignee = currentUser() AND status != Done ORDER BY updated DESC",
            fields="summary,status,priority,updated", limit=25)
```

### Открытые баги проекта, отсортированные по приоритету

```jql
project = PROJ AND issuetype = Bug AND status not in (Done, Closed)
ORDER BY priority DESC, created DESC
```

### Просроченные задачи

```jql
duedate < endOfDay() AND status not in (Done, Closed) AND duedate is not EMPTY
```

Функции дат: `startOfDay()`, `endOfWeek()`, `startOfMonth()`,
`-1d`/`-2w` (относительно сейчас): `created <= -30d`.

### Обновлялось за неделю и было изменено конкретным человеком

```jql
project = PROJ AND updated >= -7d AND assignee was "ivanov" BEFORE "2026-09-01"
```

### Задачи без компонента и без оценки

```jql
project = PROJ AND component is EMPTY AND timeoriginalestimate is EMPTY
```

### Через связи (blocks / is blocked by)

```jql
issue in blockedIssues()                    # функция доступна в DC
blockedBy = PROJ-100                        # через link type, Cloud
project = PROJ AND issueFunction in linkedIssuesOf("blocks", "PROJ-100")  # Scriptrunner (DC)
```

Без плагинов универсальный вариант — искать по ключу связи через
`jira_get_issue` и поле `issuelinks`.

### Эпик и его дети

```jql
"_epic link" = PROJ-100 OR key = PROJ-100   # Cloud (company-managed)
parent = PROJ-100                            # Cloud (team-managed / next-gen)
```

### Спринт

```jql
project = PROJ AND sprint in openSprints() AND status != Done
```

Функции: `openSprints()`, `closedSprints()`, `futureSprints()`. Для точного
спринта: `sprint = "Sprint 5"` или ID спринта из `jira_get_sprints_from_board`.

### Поля и функции-частые

| Фрагмент JQL | Что делает |
|---|---|
| `status CHANGED TO "In Review" AFTER -1d` | статус менялся за сутки |
| `text ~ "timeout error"` | полнотекстовый поиск |
| `summary ~ "deploy*"` | поиск по заголовку с wildcard |
| `labels = hotfix` | фильтр по метке |
| `fixVersion = v2.0.0` | задачи релиза |
| `assignee is EMPTY` | нераспределённые |
| `ORDER BY rank` | порядок бэклога |

## Confluence: CQL

### Поиск по тексту в конкретном пространстве

```sql
space = DEV AND type = page AND text ~ "deployment guide"
```

```python
from scripts.confluence_search import confluence_search
confluence_search(query='space = DEV AND type = page AND text ~ "deployment guide"', limit=25)
```

### Точное совпадение в заголовке

```sql
space = OPS AND type = page AND title = "Runbook: Payments"
```

`title ~ "runbook"` — нечёткое совпадение; `title = "..."` — точное.

### Страницы по метке

```sql
type = page AND label = "runbook" AND space = OPS ORDER BY lastmodified DESC
```

### Недавно изменённые страницы

```sql
space = DEV AND type = page ORDER BY lastmodified DESC
```

### Созданные конкретным автором

```sql
type = page AND creator = "ivanov" ORDER BY created DESC
```

### Блог-посты и вложения

```sql
space = TEAM AND type = blogpost
space = DEV AND type = attachment AND title ~ "*.pdf"
```

### Разница Cloud / DC в CQL

| Возможность | Cloud | Data Center |
|---|---|---|
| `space.type = global` | да | да (7.18+) |
| `contributor` / `contributor.name` | да | зависит от версии |
| полнотекстовый `text ~` | да | да (с ограничениями по объёму) |
| `parent = <id>` | да | да (6.0+) |

## Советы

- Ограничивайте `limit` (10–50) — полные выборки тратят токены впустую.
- Уточняйте `fields=` в `jira_search`: без него тянутся все поля.
- Точные имена статусов зависят от workflow проекта: сначала
  `jira_get_issue("PROJ-123")` и посмотрите актуальные `status`.
- В CQL строки в одинарных или двойных кавычках равнозначны; для текста
  с пробелами кавычки обязательны.
