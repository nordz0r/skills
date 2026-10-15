<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset=".github/assets/banner-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset=".github/assets/banner-light.svg">
    <img alt="nordz0r/skills — skills для AI-агентов" src=".github/assets/banner-light.svg" width="100%">
  </picture>
</p>

<p align="center"><b>Русский</b> · <a href="README.en.md">English</a></p>

<p align="center">
  <a href="#каталог"><img alt="skills" src="https://img.shields.io/badge/skills-26-58a6ff?style=flat-square"></a>
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude_Code-plugin-d97757?style=flat-square">
  <img alt="Codex" src="https://img.shields.io/badge/Codex-plugin-10a37f?style=flat-square">
  <img alt="Hermes" src="https://img.shields.io/badge/Hermes-skills-8957e5?style=flat-square">
  <img alt="npx skills" src="https://img.shields.io/badge/npx_skills-OpenClaw-555?style=flat-square">
  <a href="https://skills.sh/nordz0r/skills"><img alt="skills.sh" src="https://skills.sh/b/nordz0r/skills"></a>
  <a href="https://github.com/nordz0r/skills/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/nordz0r/skills?style=flat-square&logo=github"></a>
</p>

28 skills для `Claude Code`, `Codex`, `Hermes` и других агентов, которые читают `SKILL.md`. Внутри DevOps и SRE, Linux и Docker, LiteLLM и Open WebUI, Nextcloud и Atlassian, OpenWrt, Telegram и анимированные диаграммы. Каждый skill — папка с `SKILL.md` и, при необходимости, `references/`, `scripts/` и `evals/`.

## ⚡ Быстрый старт

```bash
npx skills add nordz0r/skills
```

Другие агенты, по одной команде:

| Агент | Команда |
|---|---|
| Claude Code | `claude plugin marketplace add nordz0r/skills && claude plugin install all-skills@nord-skills` |
| Codex | `codex plugin marketplace add nordz0r/skills && codex plugin add all-skills@nord-skills` |
| Hermes Agent | `hermes skills install nordz0r/skills/<skill>` |
| Один skill через `npx` | `npx skills add nordz0r/skills -s pr-lens-diagrams -g` |

<details>
<summary><b>Установка подробно: бандлы, флаги, tap для Hermes, обновления</b></summary>

Репозиторий оформлен как универсальный источник: его можно подключать как официальный **Claude Code Plugin / Marketplace**, так и устанавливать через **`npx skills`** для `Codex`, `OpenClaw` и других AI-агентов.

#### 1. Claude Code (Plugin Marketplace)

```bash
# 1. Добавить маркетплейс в Claude Code
claude plugin marketplace add nordz0r/skills

# 2. Установить бандл или отдельные плагины:
claude plugin install all-skills@nord-skills       # Все 28 скиллов
claude plugin install agency-skills@nord-skills    # Agency engineering (6 скиллов)
claude plugin install infra-linux@nord-skills      # Linux, Docker, CI/CD, Ansible
claude plugin install ai-tools@nord-skills         # LiteLLM, WebUI, OpenCodex
claude plugin install nextcloud@nord-skills        # Nextcloud: файлы + Collectives wiki
claude plugin install openwrt-routing@nord-skills  # OpenWrt (AmneziaWG, Podkop, zapret)
claude plugin install telegram-formatting@nord-skills  # Telegram Rich Markdown/HTML
claude plugin install pr-lens-diagrams@nord-skills     # PR Lens animated diagrams

# Внутри интерактивной сессии Claude Code:
/plugin marketplace add nordz0r/skills
/plugin install all-skills@nord-skills
```

#### 2. OpenAI Codex (Plugins — как в ChatGPT)

Codex CLI читает тот же репозиторий как **plugin marketplace**: в корне лежит `.agents/plugins/marketplace.json`, а каждый бандл — отдельный плагин со своим манифестом `.codex-plugin/plugin.json` и скиллами внутри `skills/`. Список плагинов доступен через `/plugins` в интерактивной сессии Codex или в ChatGPT desktop app.

```bash
# 1. Добавить маркетплейс в Codex
codex plugin marketplace add nordz0r/skills

# 2. Установить бандл:
codex plugin add openwrt-routing@nord-skills
codex plugin add nextcloud@nord-skills

# 3. Посмотреть, что установлено:
codex plugin list
```

Внутри интерактивной сессии Codex: `/plugins` — выбрать маркетплейс `nord-skills` и установить любой из шести бандлов (`all-skills`, `agency-skills`, `infra-linux`, `ai-tools`, `nextcloud`, `openwrt-routing`).

После установки скиллы доступны в новых сессиях и вызываются по имени (`openwrt-routing:zapret-openwrt-guide`) или подбираются автоматически по описанию задачи.

> Структуру плагинов генерирует скрипт `scripts/sync-codex-plugins.js` из `.claude-plugin/marketplace.json`: руки в `plugins/` не трогаем, меняем источник и пересобираем.

#### 3. OpenClaw и Agent CLI (`npx skills`)

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

#### 4. Hermes Agent (`hermes skills`)

Репозиторий совместим с Hermes Agent (Nous Research): skills ставятся напрямую из GitHub и обновляются через встроенный механизм хаба.

```bash
# Установить один skill напрямую (owner/repo/<имя-skill>)
hermes skills install nordz0r/skills/open-webui-guide

# Подключить весь репозиторий как tap (навигация в /skills browse)
hermes skills tap add nordz0r/skills
```

`tap add` по умолчанию ищет skills в подкаталоге `skills/`, а в этом репозитории они лежат в корне, поэтому после добавления тапа поправьте путь в `$HERMES_HOME/skills/.hub/taps.json` (по умолчанию `HERMES_HOME` — это `~/.hermes`):

```json
{
  "taps": [
    { "repo": "nordz0r/skills", "path": "" }
  ]
}
```

Категории для страницы Skills Hub берутся из `skills.sh.json` в корне репозитория. Учтите: `search`/`browse` сначала обходит большие встроенные тапы (openai, anthropics, NVIDIA и др.), поэтому свежий тап может не сразу появиться в поиске — прямая установка по идентификатору работает всегда.

```bash
# Проверить, какие установленные skills изменились upstream
hermes skills check

# Обновить только изменившиеся skills (локальные правки не перезаписываются)
hermes skills update

# Принудительно перезаписать один skill
hermes skills update open-webui-guide --force
```

При установке Hermes копирует `SKILL.md` и только те файлы, на которые он ссылается (`references/`, `scripts/`); для приватных репозиториев нужен `GITHUB_TOKEN`. Без токена GitHub API ограничен 60 запросами/час.

</details>

## 🗺️ Как это устроено

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset=".github/assets/architecture-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset=".github/assets/architecture-light.svg">
    <img alt="Как skill попадает в агента: папки skills и marketplace.json → sync-codex-plugins.js, plugins/, skills.sh.json → Claude Code, Codex, npx skills, Hermes" src=".github/assets/architecture-light.svg" width="100%">
  </picture>
</p>

Источник истины — папки skills и `.claude-plugin/marketplace.json`. Скрипт `scripts/sync-codex-plugins.js` собирает из них `plugins/` для Codex, `skills.sh.json` группирует skills для каталогов, Hermes ставит skill прямо из папки. Схема нарисована skill'ом [`pr-lens-diagrams`](pr-lens-diagrams/).

<a id="каталог"></a>
## 📦 Каталог

### 🛠️ Engineering и продуктовая работа

| | Skill | Что делает |
|---|---|---|
| 🚀 | [`agency-devops-automator`](agency-devops-automator/) | CI/CD, Terraform, Kubernetes, Helm, Vault, rollout и rollback |
| 📈 | [`agency-sre`](agency-sre/) | SLO/SLI, алерты, observability, capacity |
| 🚨 | [`agency-incident-response-commander`](agency-incident-response-commander/) | SEV-триаж, откат, постмортем, коммуникация |
| 🔐 | [`agency-security-engineer`](agency-security-engineer/) | Threat modeling, auth, секреты, hardening |
| 🗄️ | [`agency-database-optimizer`](agency-database-optimizer/) | PostgreSQL/MySQL: схемы, индексы, EXPLAIN, миграции |
| ✍️ | [`agency-technical-writer`](agency-technical-writer/) | README, runbook, migration guide, operator docs |
| 🎤 | [`preview-interview`](preview-interview/) | Подготовка к интервью и mock-сессии |

### 🐧 Linux, Docker, CI/CD

| | Skill | Что делает |
|---|---|---|
| 🖥️ | [`administering-linux`](administering-linux/) | systemd, journald, диски, SSH, пакеты |
| 🐳 | [`docker-ops`](docker-ops/) | Dockerfile, Compose v2, healthcheck, сети, тома |
| 🦊 | [`gitlab-ci`](gitlab-ci/) | `.gitlab-ci.yml`, rules, runners, dind, Registry |
| 📜 | [`ansible-playbook`](ansible-playbook/) | Playbooks, roles, inventory, vault, `--check --diff` |
| 🛡️ | [`amnezia-vpn`](amnezia-vpn/) | AmneziaVPN/AWG на Linux и в Docker |
| 🛰️ | [`xray-reality`](xray-reality/) | Xray VLESS + REALITY/XHTTP: сервер, клиенты, версии |
| 🧭 | [`vpn-setup`](vpn-setup/) | Плейбук своего VPN: выбор AWG/Xray, проверка, траблшутинг |
| 🧭 | [`linux-routing`](linux-routing/) | Policy routing, fwmark, nftables NAT, split-tunnel |

### 🤖 AI-инструменты и интеграции

| | Skill | Что делает |
|---|---|---|
| 🔀 | [`litellm-guide`](litellm-guide/) | LiteLLM: SDK, proxy, провайдеры, роутинг, MCP |
| 🧩 | [`opencodex-guide`](opencodex-guide/) | OpenCodex: пулы аккаунтов, роутинг, CLI |
| 💬 | [`open-webui-guide`](open-webui-guide/) | Open WebUI: auth, pipelines, RAG, API, масштабирование |
| ⌨️ | [`open-terminal-guide`](open-terminal-guide/) | Open Terminal: REST API терминала для агентов |
| ☁️ | [`nextcloud-admin`](nextcloud-admin/) | Nextcloud через OCS API и WebDAV |
| 📚 | [`nextcloud-collectives`](nextcloud-collectives/) | Вики Nextcloud Collectives: страницы, поиск, теги |
| 🔎 | [`elk-kibana-dashboards`](elk-kibana-dashboards/) | Elasticsearch/Kibana: логи, дашборды, KQL |
| 🧷 | [`atlassian`](atlassian/) | Jira, Confluence, Bitbucket: Cloud и Data Center |

### ✈️ Telegram и диаграммы

| | Skill | Что делает |
|---|---|---|
| 📨 | [`telegram-formatting`](telegram-formatting/) | Telegram Rich Markdown/HTML, Bot API и картинки |
| 🎞️ | [`pr-lens-diagrams`](pr-lens-diagrams/) | Анимированные схемы через PR Lens → SVG, GIF, MP4 |

### 📡 OpenWrt и сеть

| | Skill | Что делает |
|---|---|---|
| 🔒 | [`amneziawg-openwrt-guide`](amneziawg-openwrt-guide/) | AmneziaWG на OpenWrt: UCI/LuCI, peers, watchdog |
| 🧦 | [`podkop-openwrt-guide`](podkop-openwrt-guide/) | Podkop + sing-box: selective routing, FakeIP |
| 🕳️ | [`zapret-openwrt-guide`](zapret-openwrt-guide/) | zapret: DPI desync, nfqws, hostlists |

## ✨ Витрина

### 🎞️ pr-lens-diagrams — анимированные схемы

Агент пишет `graph.json`, skill проверяет его, рендерит через [PR Lens](https://github.com/coldteadotai/pr-lens) и записывает бесшовные GIF и MP4. Ниже результат для примера из [`examples/bots.graph.json`](pr-lens-diagrams/examples/bots.graph.json); схема выше сделана так же.

<p align="center"><img alt="Пример pr-lens-diagrams: оркестратор и группы ботов" src=".github/assets/pr-lens-example.gif" width="100%"></p>

```bash
bash pr-lens-diagrams/scripts/pr-lens-build.sh graph.json out/   # → out/architecture.{svg,gif,mp4}
```

### 📨 telegram-formatting — Rich Markdown и HTML для Telegram

Таблицы и чек-листы в ответах gateway, Rich HTML для прямого Bot API и TypeScript-builder `tg-rich-messages`: как выбирать путь доставки, валидировать payload, передавать медиа и не раскрывать приватные изображения. Есть evals.

### 🔀 litellm-guide — LiteLLM от SDK до прокси

SDK, proxy/gateway, провайдеры, роутинг, virtual keys, MCP/A2A и разработка в самом репозитории LiteLLM. Шесть файлов в `references/` и evals для бенчмарка маршрутизации.

<details>
<summary><b>Как вызывать skills и как проверяется автоподбор</b></summary>

### 1. Явный вызов

Самый надежный вариант: назвать skill прямо в первом сообщении.

```text
Используй agency-devops-automator и собери CI/CD для k3s с rollback.
Используй agency-technical-writer и перепиши устаревший runbook.
Используй telegram-formatting для Rich Markdown ответа в Telegram.
```

#### 2. Автоподбор по смыслу

Автоматический trigger опирается прежде всего на `description` в `SKILL.md`. Чтобы повысить шанс автоподбора:

- формулируй задачу предметно, а не общими словами
- используй доменные термины из таблиц выше
- если результат должен быть предсказуемым, указывай skill явно

### Бенчмарк маршрутизации

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

**Текущие метрики** (2026-09-20, 26 skill / 48 кейсов):

| Состояние | top1 acc | avg_score |
|-----------|----------|-----------|
| Пилот 2026-09-01 | 0.8364 (46/55) | 0.8745 |
| Quoted `description` + stopword `нужно` | 1.0000 (64/64) | 1.0000 |
| После удаления `basic-memory` / `lightpanda` | 1.0000 (63/63) | 1.0000 |
| После удаления 4 design-agency | **1.0000 (48/48)** | 1.0000 |

Роутер читает только первую строку `description:`. Свёрнутые `>-` блоки для него пустые — держи quoted one-liner. Heuristic engine по-прежнему нетто-вреден. Skillforge (`--engine skillforge`) мутирует только изолированный `.workdir/`.

</details>

## ⭐ Star History

<p align="center">
  <a href="https://www.star-history.com/#nordz0r/skills&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=nordz0r/skills&type=Date&theme=dark">
      <img alt="Star History" src="https://api.star-history.com/svg?repos=nordz0r/skills&type=Date" width="640">
    </picture>
  </a>
</p>

## 🤝 Contributing

Новый skill или правка — через pull request.

1. Папка в `kebab-case`, внутри `SKILL.md` с frontmatter: `name` совпадает с папкой, `description` — конкретная строка в кавычках.
2. Добавьте skill в `.claude-plugin/marketplace.json`, `skills.sh.json` и оба README.
3. Пересоберите плагины и проверьте:
   ```bash
   node scripts/sync-codex-plugins.js
   node scripts/validate-skills.js
   ```
4. Руками в `plugins/` ничего не правьте, эта папка генерируется.

Подробности для агентов — в [`AGENTS.md`](AGENTS.md).

<details>
<summary><b>Структура репозитория</b></summary>

```text
skills/
├── .claude-plugin/
│   ├── marketplace.json  # Каталог маркетплейса Claude Code (бандлы + отдельные скиллы)
│   └── plugin.json       # Корневой манифест плагина для прямой установки
├── .agents/plugins/
│   └── marketplace.json  # Каталог маркетплейса OpenAI Codex / ChatGPT plugins
├── plugins/              # Сгенерированные Codex-плагины (не редактировать руками)
│   └── <bundle>/
│       ├── .codex-plugin/plugin.json
│       └── skills/<skill-name>/SKILL.md
├── scripts/
│   ├── validate-skills.js     # Валидатор манифестов, frontmatter и путей
│   └── sync-codex-plugins.js  # Генератор Codex-плагинов из .claude-plugin/marketplace.json
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

</details>

---

<p align="center">
  <b>Пригодился хоть один skill? Поставьте ⭐ — так репозиторий проще найти другим.</b><br>
  <a href="https://github.com/nordz0r/skills/stargazers"><img alt="Star nordz0r/skills" src="https://img.shields.io/github/stars/nordz0r/skills?style=social"></a>
</p>
