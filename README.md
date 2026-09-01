# Skills for Claude Code, Codex и AI-агентов

[English README](README.en.md)

Коллекция переиспользуемых skills для `Claude Code`, `Codex` и других агентных CLI. Репозиторий распространяется через `npx skills add nordz0r/skills` и оформлен так, чтобы его было легко читать людям, индексировать каталогам и находить через встроенный skill discovery.

> English summary: reusable skills for Claude Code, Codex, and AI agents. Covers DevOps, SRE, incident response, security, UX, Playwright browser automation, Lightpanda browser automation, Open WebUI, Open Terminal, OmniRoute AI router, Ollama Search, Qdrant code search, Nextcloud, OpenWrt, and project memory workflows.

**Каталоги и discovery:** [skills.sh](https://skills.sh) · [SkillsMP](https://skillsmp.com)

**Ключевые слова для поиска:** Claude Code skills, Codex skills, AI agent skills, skills.sh, SkillsMP, DevOps, SRE, incident response, security review, technical writing, UX research, UI design, Playwright, Lightpanda, browser automation, rendered extraction, CDP, MCP, headless browser for AI, E2E testing, screenshot testing, responsive testing, Open WebUI, Open Terminal, OmniRoute, AI router, LLM proxy, combo routing, auto-combo, Ollama Search, Qdrant code search, Nextcloud, WebDAV, OCS API, Linux, systemd, Docker, Docker Compose, GitLab CI, Ansible, AmneziaVPN, AmneziaWG, policy routing, iproute2, nftables, OpenWrt, Podkop, zapret, basic-memory, project memory.

## Что внутри

| Пункт | Значение |
|------|----------|
| Формат | Каждый skill живет в собственной директории и содержит `SKILL.md`, а также опциональные `references/`, `scripts/` и `evals/` |
| Язык | Основной README на русском, дополнительный README на английском; содержимое skills зависит от домена и может быть RU или EN |
| Установка | Через `npx skills add nordz0r/skills` |
| Для кого | `Claude Code`, `Codex`, OpenClaw и любые агенты, которые читают skills в формате `SKILL.md` |
| Источник автоподбора | `name` и особенно `description` в каждом `SKILL.md` |

## Каталог skills

### Engineering, platform и product work

| Skill | Фокус | Trigger keywords |
|------|-------|------------------|
| [agency-devops-automator](agency-devops-automator/) | CI/CD, Terraform, Ansible, Kubernetes, Helm, Vault, rollout/rollback | devops, ci/cd, deploy, kubernetes, helm, ansible, vault |
| [agency-sre](agency-sre/) | Надежность сервисов, SLO/SLI, алерты, observability, scaling | sre, slo, sli, alerts, reliability, observability, capacity |
| [agency-incident-response-commander](agency-incident-response-commander/) | Incident management, SEV triage, rollback, postmortem, stakeholder comms | incident, outage, sev, rollback, postmortem, on-call |
| [agency-security-engineer](agency-security-engineer/) | Threat modeling, auth, secrets, hardening, cloud and Kubernetes security | security, threat model, authn, authz, secrets, hardening |
| [agency-database-optimizer](agency-database-optimizer/) | PostgreSQL/MySQL/MariaDB, schema design, indexing, EXPLAIN, migrations | postgres, mysql, mariadb, indexing, explain, slow query |
| [agency-technical-writer](agency-technical-writer/) | README, runbook, migration guide, architecture note, operator docs | readme, runbook, migration guide, docs, contributor guide |
| [agency-ui-designer](agency-ui-designer/) | Visual hierarchy, components, states, accessibility, responsive polish | ui design, design system, typography, spacing, responsive |
| [agency-ux-architect](agency-ux-architect/) | IA, flows, layout systems, theming foundations, implementation-ready UX | ux architecture, ia, flow, layout system, screen structure |
| [agency-ux-researcher](agency-ux-researcher/) | Research plans, interview guides, usability tests, validation | ux research, usability test, interview guide, discovery |
| [agency-whimsy-injector](agency-whimsy-injector/) | Delight, product personality, playful copy, micro-interactions | delight, micro-interactions, personality, playful ui |
| [preview-interview](preview-interview/) | Подготовка к интервью: разбор вопросов, структурирование ответов, mock-сессии | interview, prep, mock interview, behavioral, technical interview, resume |

### Linux, Docker, GitLab, Ansible и host routing

| Skill | Фокус | Trigger keywords |
|------|-------|------------------|
| [administering-linux](administering-linux/) | systemd, journald, диски, SSH, пакеты, host-level troubleshooting | linux, systemd, journalctl, sshd, disk full, oom, apt, dnf |
| [docker-ops](docker-ops/) | Dockerfile, Compose v2, healthcheck, networks, volumes, registry | docker, dockerfile, compose.yaml, healthcheck, docker logs |
| [gitlab-ci](gitlab-ci/) | `.gitlab-ci.yml`, rules, runners, dind, GitLab Registry | gitlab, gitlab-ci, runner, CI_REGISTRY, CI_JOB_TOKEN, rules |
| [ansible-playbook](ansible-playbook/) | playbooks, roles, inventory, vault, `--check --diff`, FQCN | ansible, playbook, vault, ansible-lint, inventory, handler |
| [amnezia-vpn](amnezia-vpn/) | AmneziaVPN/AWG на Linux и Docker, не OpenWrt UCI | amnezia, amneziawg, awg-quick, /opt/amnezia, Jc, handshake |
| [linux-routing](linux-routing/) | `ip rule`/`ip route`, fwmark, nft NAT, split-tunnel, conntrack | policy routing, fwmark, rt_tables, nftables, masquerade, rp_filter |

### AI tooling, knowledge workflows и integrations

| Skill | Фокус | Trigger keywords |
|------|-------|------------------|
| [basic-memory-workflow](basic-memory-workflow/) | Работа с project memory: recall context, ADR, meeting notes, stable facts | basic-memory, project memory, recall context, adr, summary |
| [playwright-skill](playwright-skill/) | Автоматизация браузера через Playwright: скриншоты, responsive checks, формы, login flows, dev-server detection | playwright, browser automation, e2e, responsive testing, screenshots |
| [lightpanda-browser](lightpanda-browser/) | Lightpanda как runtime для rendered extraction, CDP automation и MCP browsing под Win/Linux/macOS/WSL | lightpanda, rendered extraction, cdp, mcp, semantic tree, markdown dump, wsl |
| [litellm-guide](litellm-guide/) | LiteLLM: SDK, proxy/gateway, providers, routing, API, MCP/A2A, troubleshooting и repo development | litellm, proxy, gateway, providers, routing, virtual keys, mcp, openai-compatible |
| [omniroute-guide](omniroute-guide/) | OmniRoute: AI router/proxy, 237 providers, combo/auto routing, MCP (94 tools), A2A, resilience, dashboard, CLI setup | omniroute, ai router, llm proxy, combo routing, auto-combo, mcp, a2a, circuit breaker, provider fallback |
| [open-webui-guide](open-webui-guide/) | Open WebUI: architecture, auth, functions, pipelines, API, RAG, scaling | open webui, pipelines, rag, oauth, ldap, jwt, docker-compose |
| [open-terminal-guide](open-terminal-guide/) | Open Terminal: self-hosted terminal REST API for AI agents | open terminal, terminal api, /execute, /files, sandbox api |
| [ollama-search](ollama-search/) | Ollama Web Search / Web Fetch API, SDK, MCP, OpenClaw integration | ollama search, web search, web fetch, mcp, openclaw |
| [qdrant-codebase-search](qdrant-codebase-search/) | Семантический поиск по коду через Qdrant + Ollama + MCP | qdrant, code search, semantic search, vector search, mcp qdrant |
| [nextcloud-admin](nextcloud-admin/) | Управление Nextcloud через OCS API и WebDAV | nextcloud, webdav, ocs api, file sharing, public link |
| [elk-kibana-dashboards](elk-kibana-dashboards/) | Elasticsearch и Kibana: анализ логов, дашборды, Lens/TSVB, KQL/Lucene, DSL aggregations | elasticsearch, kibana, elk, kql, lucene, lens, tsvb, dashboard, logs |

### OpenWrt, networking и anti-censorship

| Skill | Фокус | Trigger keywords |
|------|-------|------------------|
| [amneziawg-openwrt-guide](amneziawg-openwrt-guide/) | AmneziaWG на OpenWrt: пакеты, UCI/LuCI, peers, QR, watchdog | amneziawg, awg, luci-proto-amneziawg, openwrt awg. Linux/Docker AWG → `amnezia-vpn` |
| [podkop-openwrt-guide](podkop-openwrt-guide/) | Podkop + sing-box на OpenWrt: selective routing, FakeIP, Clash API | podkop, sing-box, fakeip, clash api, selector, urltest. Linux PBR → `linux-routing` |
| [zapret-openwrt-guide](zapret-openwrt-guide/) | zapret-openwrt: DPI desync, nfqws, hostlists, LuCI, troubleshooting | zapret, nfqws, dpi desync, autohostlist, openwrt |

## Установка и подключение

Репозиторий оформлен как универсальный источник: его можно подключать как официальный **Claude Code Plugin / Marketplace**, так и устанавливать через **`npx skills`** для `Codex`, `OpenClaw` и других AI-агентов.

### 1. Claude Code (Plugin Marketplace)

```bash
# 1. Добавить маркетплейс в Claude Code
claude plugin marketplace add nordz0r/skills

# 2. Установить бандл или отдельные плагины:
claude plugin install all-skills@nord-skills       # Все 31 скилл
claude plugin install agency-skills@nord-skills    # Только Agency (10 скиллов)
claude plugin install infra-linux@nord-skills      # Linux, Docker, CI/CD, Ansible
claude plugin install ai-tools@nord-skills         # LiteLLM, OmniRoute, WebUI, Playwright
claude plugin install openwrt-routing@nord-skills  # OpenWrt (AmneziaWG, Podkop, zapret)
claude plugin install litellm-guide@nord-skills    # Конкретный скилл

# Внутри интерактивной сессии Claude Code:
/plugin marketplace add nordz0r/skills
/plugin install all-skills@nord-skills
```

### 2. OpenAI Codex, OpenClaw и Agent CLI (`npx skills`)

```bash
# Показать список skills
npx skills add nordz0r/skills -l

# Установить все skills только в текущий проект
npx skills add nordz0r/skills

# Установить все skills глобально
npx skills add nordz0r/skills -g

# Установить конкретный skill
npx skills add nordz0r/skills -s litellm-guide -g
```

| Флаг `npx skills` | Что делает |
|-------------------|------------|
| `-l`, `--list` | Показывает доступные skills без установки |
| `-s`, `--skill <name>` | Устанавливает только один skill |
| `-g`, `--global` | Делает skill доступным глобально |
| `-y`, `--yes` | Пропускает подтверждения |

После установки лучше открыть новую сессию агента: многие CLI читают список доступных skills только при старте.

## Как использовать

### 1. Явный вызов

Самый надежный вариант: назвать skill прямо в первом сообщении.

```text
Используй agency-devops-automator и собери CI/CD для k3s с rollback.
Используй agency-ui-designer и agency-ux-architect для редизайна админки.
Используй qdrant-codebase-search для поиска по коду и git-истории.
Используй basic-memory-workflow и проверь project memory перед изменениями.
```

### 2. Автоподбор по смыслу

Автоматический trigger опирается прежде всего на `description` в `SKILL.md`. Чтобы повысить шанс автоподбора:

- формулируй задачу предметно, а не общими словами
- используй доменные термины из таблиц выше
- если результат должен быть предсказуемым, указывай skill явно

## Как этот README помогает каталогам и агентам

README не заменяет `SKILL.md`, но усиливает discoverability на уровне репозитория.

- В одном месте собраны все skill names, домены и ключевые слова на русском и английском.
- Каждый skill имеет прямую ссылку из корневого README, что удобно для каталогов и индексаторов.
- В верхней части README есть английский abstract, чтобы репозиторий было проще находить по англоязычным запросам.
- Для `Claude Code` и `Codex` источником истины остается `description` в `SKILL.md`; README помогает понять, какой skill устанавливать и вызывать.

Если добавляешь новый skill, держи синхронно три слоя:

1. Имя директории
2. `name` и `description` в `SKILL.md`
3. Запись в `README.md` и `README.en.md`

## Экспериментальная маршрутизация skills

В репозитории есть эксперимент [`tools/a_evolve_router`](tools/a_evolve_router/) — небольшой benchmark для проверки, насколько хорошо тексты `SKILL.md` маршрутизируют пользовательские запросы к нужному skill. Он использует eval cases из `<skill>/evals/evals.json`, дополнительные неоднозначные кейсы из `supplemental_cases.json` и изолированную workspace-копию skills, поэтому реальные директории skills не изменяются во время прогона.

Для чего использовать:

- быстро проверить baseline качества trigger wording после добавления или правки skill;
- стресс-тестировать похожие skills, где автоподбор может путаться;
- запускать локальный `a-evolve` loop, который улучшает routing-сигналы в копии workspace;
- сравнивать `train`/`holdout` accuracy перед переносом формулировок обратно в реальные `SKILL.md`.

Быстрый baseline без установки `a-evolve`:

```bash
python3 -m tools.a_evolve_router.evaluate_baseline --split all
```

Полный локальный прогон через `a-evolve` описан в [`tools/a_evolve_router/README.md`](tools/a_evolve_router/README.md). Обычно используют `--reset-workspace`, чтобы каждый запуск начинался с чистой копии текущих skills.

**Текущие метрики** (пилот 2026-09-01, 25 видимых роутеру skills / 43 кейса):

| Состояние | top1 acc | avg_score |
|-----------|----------|-----------|
| Baseline (line-based `parse_frontmatter`) | **0.9070** (39/43) | 0.9151 |
| После `parse_frontmatter` → PyYAML (откачено) | 0.8372 (36/43) | 0.8698 |
| После `heuristic` engine (3 цикла) | не измерено | не измерено |

Шесть директорий skills на `main` (`administering-linux`, `amnezia-vpn`, `ansible-playbook`, `docker-ops`, `gitlab-ci`, `linux-routing`) содержат только `evals/evals.json` без `SKILL.md`, поэтому роутер их не видит, а их eval-кейсы честно учитываются как фейлы. PyYAML-вариант парсера корректно читает `description: >-`, но регрессирует top-1 на −7 п.п., потому что эвристический роутер полагается на first-line-only overlap для различения соседних skills — фикс откачен, описание в [pilot README](tools/a_evolve_router/README.md). Эвристический движок `a-evolve` остаётся в коде как reference implementation, но в текущем виде нетто-вреден.

## Структура репозитория

```text
skills/
├── .claude-plugin/
│   ├── marketplace.json  # Каталог маркетплейса Claude Code (бандлы + 31 плагин)
│   └── plugin.json       # Корневой манифест плагина для прямой установки
├── scripts/
│   └── validate-skills.js # Валидатор манифестов, frontmatter и путей
├── README.md
├── README.en.md
├── AGENTS.md
├── tools/
│   └── a_evolve_router/  # экспериментальный benchmark маршрутизации skills
└── <skill-name>/
    ├── SKILL.md          # Основные инструкции с YAML frontmatter
    ├── agents/           # OpenAI/Codex agent manifest (openai.yaml)
    ├── evals/            # опционально: тестовые промпты и проверки trigger quality
    ├── scripts/          # опционально: bash-скрипты или automation helpers
    └── references/       # опционально: подробные справочные материалы по темам
```

## Рекомендации для новых skills

- Используй конкретные `description`, а не общие слоганы.
- Добавляй trigger keywords в естественный текст описания, а не отдельным бессмысленным списком.
- Сразу решай, кому адресован skill: оператору, разработчику, on-call инженеру, AI-агенту.
- Если у skill есть внешние зависимости, фиксируй их в `metadata` и показывай в `SKILL.md`.
- Если добавил новый домен, обнови оба README, чтобы каталоги и пользователи видели его с корня репозитория.
