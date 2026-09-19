# Skills for Claude Code, Codex, and AI Agents

[Русская версия](README.md)

Reusable skills for `Claude Code`, `Codex`, and other agentic CLIs. This repository is distributed via `npx skills add nordz0r/skills` and organized for both human readability and catalog discovery.

Most domain guides live inside each skill directory. The main repository README is Russian-first; this English companion exists for repo-level discoverability in catalogs and search.

**Catalogs and discovery:** [skills.sh](https://skills.sh) · [SkillsMP](https://skillsmp.com)

**Search keywords:** Claude Code skills, Codex skills, AI agent skills, DevOps, SRE, incident response, security review, UX research, UI design, technical writing, Open WebUI, Open Terminal, OmniRoute, AI router, LLM proxy, combo routing, auto-combo, Nextcloud, WebDAV, OCS API, Collectives, wiki, knowledge base, Linux, systemd, Docker, Docker Compose, GitLab CI, Ansible, AmneziaVPN, AmneziaWG, policy routing, iproute2, nftables, OpenWrt, Podkop, zapret.

## Repository at a glance

| Item | Value |
|------|-------|
| Format | Each skill has its own directory with `SKILL.md` and optional `references/`, `scripts/`, and `evals/` |
| Distribution | `npx skills add nordz0r/skills` |
| Primary audiences | `Claude Code`, `Codex`, OpenClaw, and other tools that understand `SKILL.md`-style skills |
| Auto-trigger source of truth | `name` and especially `description` inside each `SKILL.md` |
| Languages | Russian-first repo README with an English companion; skill bodies may be written in Russian or English depending on the domain |

## Skill index

### Engineering, platform, and product work

| Skill | Scope | Keywords |
|------|-------|----------|
| [agency-devops-automator](agency-devops-automator/) | CI/CD, Terraform, Ansible, Kubernetes, Helm, Vault, rollout and rollback | devops, ci/cd, deploy, kubernetes, helm, ansible, vault |
| [agency-sre](agency-sre/) | Reliability engineering, SLO/SLI, alerts, observability, scaling | sre, slo, sli, alerts, reliability, observability |
| [agency-incident-response-commander](agency-incident-response-commander/) | Incident handling, SEV triage, rollback decisions, postmortems | incident, outage, sev, rollback, postmortem |
| [agency-security-engineer](agency-security-engineer/) | Threat modeling, auth, secrets, hardening, cloud and Kubernetes security | security, threat model, authn, authz, secrets |
| [agency-database-optimizer](agency-database-optimizer/) | PostgreSQL, MySQL, MariaDB, indexing, EXPLAIN, migrations | postgres, mysql, mariadb, indexing, explain |
| [agency-technical-writer](agency-technical-writer/) | READMEs, runbooks, migration guides, architecture notes | readme, runbook, migration guide, docs |
| [preview-interview](preview-interview/) | Interview preparation: question banks, answer structuring, mock sessions | interview, prep, mock interview, behavioral, technical interview, resume |

### Linux, Docker, GitLab, Ansible, and host routing

| Skill | Scope | Keywords |
|------|-------|----------|
| [administering-linux](administering-linux/) | systemd, journald, disks, SSH, packages, host troubleshooting | linux, systemd, journalctl, sshd, disk full, oom, apt, dnf |
| [docker-ops](docker-ops/) | Dockerfile, Compose v2, healthchecks, networks, volumes, registry | docker, dockerfile, compose.yaml, healthcheck, docker logs |
| [gitlab-ci](gitlab-ci/) | `.gitlab-ci.yml`, rules, runners, dind, GitLab Registry | gitlab, gitlab-ci, runner, CI_REGISTRY, CI_JOB_TOKEN, rules |
| [ansible-playbook](ansible-playbook/) | playbooks, roles, inventory, vault, `--check --diff`, FQCN | ansible, playbook, vault, ansible-lint, inventory, handler |
| [amnezia-vpn](amnezia-vpn/) | AmneziaVPN/AWG on Linux and Docker, not OpenWrt UCI | amnezia, amneziawg, awg-quick, /opt/amnezia, Jc, handshake |
| [linux-routing](linux-routing/) | `ip rule`/`ip route`, fwmark, nft NAT, split-tunnel, conntrack | policy routing, fwmark, rt_tables, nftables, masquerade, rp_filter |

### AI tooling, knowledge workflows, and integrations

| Skill | Scope | Keywords |
|------|-------|----------|
| [litellm-guide](litellm-guide/) | LiteLLM SDK, proxy/gateway, providers, routing, APIs, MCP/A2A, troubleshooting, and repo development | litellm, proxy, gateway, providers, routing, virtual keys, mcp, openai-compatible |
| [opencodex-guide](opencodex-guide/) | OpenCodex CLI guide: account pools, routing, models | opencodex, ocx, proxy, llm proxy |
| [omniroute-guide](omniroute-guide/) | OmniRoute unified AI router: 237 providers, combo/auto routing, MCP (94 tools), A2A, resilience, dashboard, CLI integrations | omniroute, ai router, llm proxy, combo routing, auto-combo, mcp, a2a, circuit breaker, provider fallback |
| [open-webui-guide](open-webui-guide/) | Open WebUI architecture, auth, functions, pipelines, API, RAG, scaling | open webui, pipelines, rag, oauth, ldap, jwt |
| [open-terminal-guide](open-terminal-guide/) | Open Terminal self-hosted REST API for AI agents | open terminal, terminal api, /execute, sandbox api |
| [nextcloud-admin](nextcloud-admin/) | Nextcloud administration via OCS API and WebDAV | nextcloud, webdav, ocs api, file sharing |
| [nextcloud-collectives](nextcloud-collectives/) | Nextcloud Collectives wiki via OCS API and WebDAV: collectives, markdown pages, page tree, search, tags, attachments, public shares, trash, versions | collectives, nextcloud wiki, knowledge base, wiki page, readme.md |
| [elk-kibana-dashboards](elk-kibana-dashboards/) | Elasticsearch and Kibana: log analysis, dashboards, Lens/TSVB, KQL/Lucene, DSL aggregations | elasticsearch, kibana, elk, kql, lucene, lens, tsvb, dashboard, logs |
| [atlassian](atlassian/) | Jira (issues, JQL, workflows, sprints, worklogs), Confluence (pages, CQL, labels, rich storage-format articles), Bitbucket Server/DC (PRs, commits). Cloud + Data Center | jira, confluence, bitbucket, atlassian, jql, cql, issue, ticket, sprint, wiki page |

### Telegram

| Skill | Scope | Keywords |
|------|-------|----------|
| [telegram-formatting](telegram-formatting/) | Telegram Rich Markdown: syntax, banners, inline images, delivery | telegram, formatting, rich-messages, bot-api, placehold, media |

### OpenWrt, networking, and anti-censorship

| Skill | Scope | Keywords |
|------|-------|----------|
| [amneziawg-openwrt-guide](amneziawg-openwrt-guide/) | AmneziaWG on OpenWrt: packages, UCI/LuCI, peers, QR, watchdog | amneziawg, awg, luci-proto-amneziawg, openwrt. Linux/Docker AWG → `amnezia-vpn` |
| [podkop-openwrt-guide](podkop-openwrt-guide/) | Podkop plus sing-box on OpenWrt: selective routing, FakeIP, Clash API | podkop, sing-box, fakeip, clash api, urltest. Linux PBR → `linux-routing` |
| [zapret-openwrt-guide](zapret-openwrt-guide/) | zapret-openwrt: DPI desync, nfqws, hostlists, LuCI, troubleshooting | zapret, nfqws, dpi desync, autohostlist |

## Install and Setup

This repository is structured for universal integration: install it directly as an official **Claude Code Plugin / Marketplace** or via **`npx skills`** for `Codex`, `OpenClaw`, and other AI agents.

### 1. Claude Code (Plugin Marketplace)

```bash
# 1. Register marketplace in Claude Code
claude plugin marketplace add nordz0r/skills

# 2. Install bundle or individual plugins:
claude plugin install all-skills@nord-skills       # Complete 26 skills collection
claude plugin install agency-skills@nord-skills    # Agency engineering bundle
claude plugin install infra-linux@nord-skills      # Linux, Docker, CI/CD, Ansible
claude plugin install ai-tools@nord-skills         # LiteLLM, OmniRoute, WebUI, OpenCodex
claude plugin install nextcloud@nord-skills        # Nextcloud: files + Collectives wiki
claude plugin install openwrt-routing@nord-skills  # OpenWrt (AmneziaWG, Podkop, zapret)
claude plugin install telegram-formatting@nord-skills  # Telegram Rich Markdown

# Inside an active Claude Code interactive session:
/plugin marketplace add nordz0r/skills
/plugin install all-skills@nord-skills
```

### 2. OpenAI Codex (Plugins — same packages as ChatGPT)

Codex CLI reads this repository as a **plugin marketplace**: `.agents/plugins/marketplace.json` sits at the repo root, and each bundle is a standalone plugin with its own `.codex-plugin/plugin.json` manifest and skills under `skills/`. Plugins are browsable via `/plugins` in an interactive Codex session or in the ChatGPT desktop app.

```bash
# 1. Add the marketplace to Codex
codex plugin marketplace add nordz0r/skills

# 2. Install a bundle:
codex plugin add openwrt-routing@nord-skills
codex plugin add nextcloud@nord-skills

# 3. See what is installed:
codex plugin list
```

Inside an interactive Codex session: `/plugins` — pick the `nord-skills` marketplace and install any of the six bundles (`all-skills`, `agency-skills`, `infra-linux`, `ai-tools`, `nextcloud`, `openwrt-routing`).

Installed skills become available in new sessions and are invoked by name (`openwrt-routing:zapret-openwrt-guide`) or matched automatically from the task description.

> The plugin layout is generated by `scripts/sync-codex-plugins.js` from `.claude-plugin/marketplace.json`: do not hand-edit `plugins/`, change the source and re-sync instead.

### 3. OpenClaw and Agent CLIs (`npx skills`)

```bash
# List available skills
npx skills add nordz0r/skills -l

# Install all skills into the current project
npx skills add nordz0r/skills

# Install all skills globally
npx skills add nordz0r/skills -g

# Install one skill
npx skills add nordz0r/skills -s litellm-guide -g
```

| Flag | Description |
|------|-------------|
| `-l`, `--list` | Lists available skills without installing |
| `-s`, `--skill <name>` | Installs only the specified skill |
| `-g`, `--global` | Installs skill globally |
| `-y`, `--yes` | Skips confirmation prompts |

Restart the agent session after installation when possible. Many CLIs only load the available skill list on startup.

### 4. Hermes Agent (`hermes skills`)

The repository is compatible with Hermes Agent (Nous Research): skills install straight from GitHub and update through the built-in hub lifecycle.

```bash
# Install a single skill directly (owner/repo/<skill-dir>)
hermes skills install nordz0r/skills/open-webui-guide

# Add the whole repository as a tap (browsable via /skills browse)
hermes skills tap add nordz0r/skills
```

`tap add` defaults to scanning a `skills/` subdirectory, while this repository keeps skills at the root — so after adding the tap, set the path in `$HERMES_HOME/skills/.hub/taps.json` (`HERMES_HOME` defaults to `~/.hermes`):

```json
{
  "taps": [
    { "repo": "nordz0r/skills", "path": "" }
  ]
}
```

Skills Hub categories are read from `skills.sh.json` at the repository root. Note that `search`/`browse` walks the large built-in taps first (openai, anthropics, NVIDIA, etc.), so a freshly added tap may not surface in search immediately — direct install by identifier always works.

```bash
# Check which installed skills changed upstream
hermes skills check

# Update only skills with upstream changes (local edits are preserved)
hermes skills update

# Force-overwrite a single skill
hermes skills update open-webui-guide --force
```

On install Hermes copies `SKILL.md` plus only the files it references (`references/`, `scripts/`); private repos need `GITHUB_TOKEN`. Without a token the GitHub API is limited to 60 requests/hour.

## How to use

### Explicit invocation

Call the skill by name in your first prompt.

```text
Use agency-devops-automator and build CI/CD for k3s with rollback.
Use agency-technical-writer and rewrite a stale runbook.
Use telegram-formatting for a Telegram Rich Markdown reply.
```

### Automatic triggering

Automatic triggering usually depends on `description` inside `SKILL.md`. To improve matching:

- use domain-specific wording
- include concrete product or technology names
- call the skill explicitly when the outcome must be deterministic

## Why this README helps discovery

README is not the runtime trigger source, but it improves repository-level search and catalog indexing.

- It exposes all skill names, domains, and keywords in one place.
- Every skill has a direct link from the root README.
- The Russian main README includes an English abstract for mixed-language search.
- `SKILL.md` remains the source of truth for Claude Code and Codex auto-triggering.

When adding a new skill, keep these three layers in sync:

1. Directory name
2. `name` and `description` in `SKILL.md`
3. Entries in `README.md` and `README.en.md`

## Experimental skill routing

The repository includes [`tools/a_evolve_router`](tools/a_evolve_router/), a small benchmark for checking whether `SKILL.md` wording routes user prompts to the right skill. It reads eval cases from top-level `<skill>/evals/evals.json`, adds ambiguous stress cases from `supplemental_cases.json`, and runs against an isolated workspace copy so real skill directories are not mutated during the experiment.

Use it to:

- check trigger-wording baseline after adding or editing a skill;
- stress-test nearby skills that may be confused by auto-routing;
- run a local `a-evolve` loop that improves routing signals in the workspace copy;
- compare `train`/`holdout` accuracy before copying phrasing back into real `SKILL.md` files.

Quick baseline without installing `a-evolve`:

```bash
python3 -m tools.a_evolve_router.evaluate_baseline --split all
```

The full local `a-evolve` workflow is documented in [`tools/a_evolve_router/README.md`](tools/a_evolve_router/README.md). Use `--reset-workspace` for clean reruns from the current skill catalog.

**Current metrics** (2026-09-20, 26 skills / 48 cases):

| State | top1 acc | avg_score |
|-------|----------|-----------|
| Pilot 2026-09-01 | 0.8364 (46/55) | 0.8745 |
| Quoted `description` + `нужно` stopword | 1.0000 (64/64) | 1.0000 |
| After dropping `basic-memory` / `lightpanda` | 1.0000 (63/63) | 1.0000 |
| After dropping 4 design-agency skills | **1.0000 (48/48)** | 1.0000 |

The router still reads only the first `description:` line, so folded `>-` blocks look empty — keep a quoted one-liner. The heuristic engine remains net-negative. Skillforge (`--engine skillforge`) mutates only the isolated `.workdir/`.

## Repository structure

```text
skills/
├── .claude-plugin/
│   ├── marketplace.json  # Claude Code plugin marketplace catalog (bundles + individual skills)
│   └── plugin.json       # Root plugin manifest for direct installation
├── .agents/plugins/
│   └── marketplace.json  # OpenAI Codex / ChatGPT plugins marketplace catalog
├── plugins/              # Generated Codex plugins (do not edit by hand)
│   └── <bundle>/
│       ├── .codex-plugin/plugin.json
│       └── skills/<skill-name>/SKILL.md
├── scripts/
│   ├── validate-skills.js     # Validation tool for manifests, frontmatter, and paths
│   └── sync-codex-plugins.js  # Codex plugin generator driven by .claude-plugin/marketplace.json
├── README.md
├── README.en.md
├── AGENTS.md
├── tools/
│   └── a_evolve_router/  # experimental skill-routing benchmark
└── <skill-name>/
    ├── SKILL.md          # Primary instruction entrypoint + YAML frontmatter
    ├── agents/           # OpenAI/Codex agent manifest (openai.yaml)
    ├── evals/            # optional: benchmark prompts and routing evals
    ├── scripts/          # optional: bash scripts or automation helpers
    └── references/       # optional: in-depth domain documentation
```
