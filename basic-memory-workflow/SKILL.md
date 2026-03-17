---
name: basic-memory-workflow
description: "Используй этот скилл, когда нужно читать или записывать память проекта через local basic-memory: найти прошлые решения, вспомнить контекст, посмотреть recent activity, сохранить summary, ADR, meeting notes или stable facts в knowledge base. Триггерится на: basic-memory, memory, memories, запомни, сохрани в память, проверь память, project memory, recall context, прошлые решения, заметки проекта, meeting notes, ADR, summary в память."
---

# Basic Memory Workflow

Этот skill задаёт рабочий workflow для текущей среды, где `basic-memory` уже настроен локально.

## Текущая среда

- default project: `main`
- WSL storage path: `/mnt/c/Users/Legion/OneDrive/Infra/memories`
- основной доступ: `basic-memory` CLI
- для чтения/записи памяти используй `basic-memory tool ...`

Важно:
- В папке `memories` лежат только Markdown notes.
- Конфиги и индексы не хранятся там; они живут в `~/.basic-memory` или в Docker state.
- Не пиши в память шум, секреты и одноразовый чат-мусор.

## Когда использовать

Используй skill, если пользователь:

- просит вспомнить, что уже решали раньше
- просит найти прошлые заметки, summary, ADR или meeting notes
- просит сохранить вывод, решение, контекст, next steps или договорённости
- говорит, что `basic-memory` нужно считать основной памятью по проекту
- ссылается на `memory`, `memories`, `basic-memory`, project memory

## Базовый workflow

### 1. Если нужно вспомнить контекст

Для недавней активности:

```bash
basic-memory tool recent-activity --project main --local
```

Для поиска по теме:

```bash
basic-memory tool search-notes "query" --project main --local
```

Если нужен точный note:

```bash
basic-memory tool read-note identifier --project main --local
```

### 2. Если нужно сохранить результат

Для новой note используй:

```bash
basic-memory tool write-note --title "Title" --folder "folder" --content "..." --project main --local
```

Для обновления существующей note предпочитай `edit-note`, если уже известен целевой note и обновление точечное.

### 3. Как выбирать папку

Если пользователь не указал folder явно, используй такие дефолты:

- `inbox` — быстрые заметки без жёсткой структуры
- `decisions` — архитектурные решения, ADR, trade-offs
- `meetings` — summary созвонов, договорённости, action items
- `projects/<slug>` — устойчивый контекст по конкретному проекту

Не создавай сложную вложенность без причины. Если контекст неочевиден, `inbox` безопаснее.

## Что именно сохранять

Храни только устойчивую информацию:

- принятые решения
- причины выбора и trade-offs
- agreed next steps
- ссылки между сущностями и темами
- краткие summaries обсуждений

Не сохраняй автоматически:

- сырые длинные логи
- временные гипотезы без подтверждения
- чувствительные токены, ключи, пароли
- каждую мелкую реплику из чата

## Предпочтительный стиль записи

Перед записью сжимай информацию до полезного остатка:

- 1 note = 1 тема
- короткий, информативный title
- content должен быть годен для повторного чтения без исходного чата
- если есть решение, обязательно фиксируй `что`, `почему`, `что дальше`

## Практические шаблоны

### Сохранить решение

```bash
basic-memory tool write-note \
  --title "Decision: Basic Memory storage on OneDrive" \
  --folder "decisions" \
  --project main \
  --local \
  --content "Decision: store markdown memories in OneDrive/Infra/memories. Why: shared access from WSL and Windows while keeping local indexes separate. Next: keep Docker state outside OneDrive."
```

### Найти прошлый контекст по теме

```bash
basic-memory tool search-notes "OneDrive basic-memory docker qwen" --hybrid --project main --local
```

### Прочитать точный note

```bash
basic-memory tool read-note "decision-basic-memory-storage-on-onedrive" --project main --local
```

## Проверка состояния

Если нужно быстро проверить, что проект жив и память доступна:

```bash
basic-memory project info main
basic-memory status --json
basic-memory project ls --name main
```

## Поведенческие правила для агента

- Для вопросов о прошлом контексте сначала читай память, потом отвечай.
- Для новых устойчивых решений сначала кратко сформулируй summary, затем записывай.
- Если пользователь явно не просил сохранять, но вывод выглядит как важное решение, предложи сохранить, а не записывай молча.
- Если note уже явно существует, лучше обновить его, чем плодить дубликаты.
