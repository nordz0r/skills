# Skills

Коллекция кастомных скиллов для [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

Скиллы — это переиспользуемые наборы знаний и инструкций, которые расширяют возможности Claude Code в конкретных предметных областях. Каждый скилл содержит справочные материалы, примеры кода и практические рецепты.

## Скиллы

| Скилл | Описание |
|-------|----------|
| [agency-devops-automator](agency-devops-automator/) | Automation-first DevOps: CI/CD, Terraform, Ansible, Kubernetes, Helm, Vault, rollout/rollback, backup-aware delivery |
| [agency-sre](agency-sre/) | Reliability engineering: SLO/SLI, observability, alert quality, capacity, toil reduction |
| [agency-incident-response-commander](agency-incident-response-commander/) | Incident handling: SEV triage, stakeholder updates, timelines, postmortems, on-call discipline |
| [agency-security-engineer](agency-security-engineer/) | Practical platform and app security: threat modeling, secrets, hardening, CI/CD guardrails |
| [agency-database-optimizer](agency-database-optimizer/) | PostgreSQL/MySQL schema, migration safety, EXPLAIN, indexing, production-safe DB changes |
| [agency-ui-designer](agency-ui-designer/) | Visual interface design: hierarchy, components, accessibility, responsive polish |
| [agency-ux-architect](agency-ux-architect/) | UX foundations: IA, flow structure, layout systems, implementation-ready UI architecture |
| [agency-whimsy-injector](agency-whimsy-injector/) | Deliberate delight: micro-interactions, personality, empty/loading/success states |
| [agency-technical-writer](agency-technical-writer/) | READMEs, runbooks, migration guides, contributor docs, operator-facing documentation |
| [agency-ux-researcher](agency-ux-researcher/) | Research plans, usability tests, interview guides, evidence-based design validation |
| [open-webui-guide](open-webui-guide/) | Русскоязычная справка по Open WebUI: архитектура, авторизация, функции, пайплайны, API, RAG, масштабирование, отладка |
| [zapret-openwrt-guide](zapret-openwrt-guide/) | Русскоязычная справка по zapret-openwrt: Anti-DPI утилита для OpenWrt, стратегии обхода DPI, конфигурация, веб-интерфейс LuCI, диагностика |
| [ollama-search](ollama-search/) | Ollama Web Search & Fetch API: поиск в интернете, получение контента страниц, Python/JS SDK, MCP-сервер, интеграция с OpenClaw |
| [open-terminal-guide](open-terminal-guide/) | Русскоязычная справка по Open Terminal: REST API терминала для AI-агентов, эндпоинты, конфигурация, Docker, интеграция с Open WebUI, архитектура |
| [nextcloud-admin](nextcloud-admin/) | Nextcloud OCS API и WebDAV: управление пользователями, группами, приложениями, файлами |
| [amneziawg-openwrt-guide](amneziawg-openwrt-guide/) | AmneziaWG для OpenWrt: установка, настройка, интеграция с Podkop |
| [podkop-openwrt-guide](podkop-openwrt-guide/) | Podkop для OpenWrt: маршрутизация трафика через VPN/прокси, конфигурация, диагностика |
| [qdrant-codebase-search](qdrant-codebase-search/) | Семантический поиск по коду через Qdrant + Ollama: AST-индексация, поиск по коду и git-истории, MCP-сервер для AI-агентов |

## Структура

```
skills/
└── <skill-name>/
    ├── SKILL.md              # Точка входа скилла (frontmatter + основной контент)
    ├── evals/
    │   └── evals.json        # Тестовые промпты для проверки триггеров и качества
    ├── scripts/              # Исполняемые скрипты (опционально)
    │   └── ...
    └── references/           # Справочные материалы, подгружаемые по необходимости
        ├── topic-a.md
        ├── topic-b.md
        └── ...
```

## Установка

```bash
# Все скиллы, глобально (доступны во всех проектах)
npx skills add nordz0r/skills -g

# Все скиллы, только в текущий проект
npx skills add nordz0r/skills

# Конкретный скилл
npx skills add nordz0r/skills -s open-webui-guide -g
```

| Флаг | Назначение |
|------|-----------|
| `-l, --list` | Показать доступные скиллы, не устанавливая |
| `-s, --skill <name>` | Установить конкретный скилл по имени |
| `-g, --global` | Глобальная установка (`~/.claude/skills/`) |
| `-y, --yes` | Без подтверждений |

## Как использовать

После установки открой новую сессию агента: многие инструменты читают список skills только на старте.

Есть 2 способа использования:

### 1. Явно по имени

Самый надежный способ — назвать skill прямо в первом сообщении:

```text
Используй agency-devops-automator и собери CI/CD для k3s с rollback.
Используй agency-ui-designer и agency-ux-architect для редизайна админки.
Используй agency-database-optimizer для плана миграции MariaDB -> PostgreSQL.
```

### 2. Автоматически по смыслу задачи

Skills также могут срабатывать автоматически, если запрос совпадает с `description` в `SKILL.md`. Для этого формулируй задачу предметно:

- `agency-devops-automator`: CI/CD, deploy, Helm, Ansible, k3s, Vault, rollout, rollback
- `agency-sre`: SLO, SLI, alerts, observability, capacity, reliability
- `agency-incident-response-commander`: outage, incident, SEV, rollback, postmortem
- `agency-security-engineer`: threat model, secrets, hardening, auth, security review
- `agency-database-optimizer`: Postgres, MySQL, EXPLAIN, slow query, migration, indexing
- `agency-ui-designer`: hierarchy, spacing, typography, components, responsive polish
- `agency-ux-architect`: IA, flow, layout system, implementation-ready UX structure
- `agency-whimsy-injector`: delight, personality, micro-interactions, less generic UI
- `agency-technical-writer`: README, runbook, migration guide, contributor guide
- `agency-ux-researcher`: usability test, interview guide, research plan, validation

Если нужен предсказуемый результат, всегда лучше указывать skill явно.

## Проверка качества

У каждого `agency-*` skill есть `evals/evals.json` с тестовыми промптами. Их можно использовать как:

- smoke-test на корректный trigger
- примеры формулировок для явного вызова
- заготовки для дальнейших evals и benchmark'ов

## Лицензия

MIT
