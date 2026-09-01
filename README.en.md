# Skills for Claude Code, Codex, and AI Agents

[Русская версия](README.md)

Reusable skills for `Claude Code`, `Codex`, and other agentic CLIs. This repository is distributed via `npx skills add nordz0r/skills` and organized for both human readability and catalog discovery.

Most domain guides live inside each skill directory. The main repository README is Russian-first; this English companion exists for repo-level discoverability in catalogs and search.

**Catalogs and discovery:** [skills.sh](https://skills.sh) · [SkillsMP](https://skillsmp.com)

**Search keywords:** Claude Code skills, Codex skills, AI agent skills, DevOps, SRE, incident response, security review, UX research, UI design, technical writing, Playwright, Lightpanda, browser automation, rendered extraction, CDP, MCP, E2E testing, screenshot testing, responsive testing, Open WebUI, Open Terminal, OmniRoute, AI router, LLM proxy, combo routing, auto-combo, Ollama Search, Qdrant code search, Nextcloud, WebDAV, OCS API, Linux, systemd, Docker, Docker Compose, GitLab CI, Ansible, AmneziaVPN, AmneziaWG, policy routing, iproute2, nftables, OpenWrt, Podkop, zapret, basic-memory, project memory.

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
| [agency-ui-designer](agency-ui-designer/) | Visual hierarchy, components, accessibility, responsive polish | ui design, typography, spacing, responsive |
| [agency-ux-architect](agency-ux-architect/) | IA, flows, layout systems, implementation-ready UX structure | ux architecture, ia, flow, layout system |
| [agency-ux-researcher](agency-ux-researcher/) | Research planning, usability testing, validation | ux research, usability test, interview guide |
| [agency-whimsy-injector](agency-whimsy-injector/) | Delight, personality, playful copy, micro-interactions | delight, micro-interactions, playful ui |
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
| [basic-memory-workflow](basic-memory-workflow/) | Project memory workflow, ADRs, meeting notes, stable facts | basic-memory, project memory, adr, recall context |
| [playwright-skill](playwright-skill/) | Playwright browser automation for screenshots, responsive checks, login flows, forms, and dev-server detection | playwright, browser automation, e2e, responsive testing, screenshots |
| [lightpanda-browser](lightpanda-browser/) | Lightpanda runtime for rendered extraction, CDP automation, and MCP browsing across Windows, Linux, macOS, and WSL | lightpanda, rendered extraction, cdp, mcp, semantic tree, markdown dump, wsl |
| [litellm-guide](litellm-guide/) | LiteLLM SDK, proxy/gateway, providers, routing, APIs, MCP/A2A, troubleshooting, and repo development | litellm, proxy, gateway, providers, routing, virtual keys, mcp, openai-compatible |
| [omniroute-guide](omniroute-guide/) | OmniRoute unified AI router: 237 providers, combo/auto routing, MCP (94 tools), A2A, resilience, dashboard, CLI integrations | omniroute, ai router, llm proxy, combo routing, auto-combo, mcp, a2a, circuit breaker, provider fallback |
| [open-webui-guide](open-webui-guide/) | Open WebUI architecture, auth, functions, pipelines, API, RAG, scaling | open webui, pipelines, rag, oauth, ldap, jwt |
| [open-terminal-guide](open-terminal-guide/) | Open Terminal self-hosted REST API for AI agents | open terminal, terminal api, /execute, sandbox api |
| [ollama-search](ollama-search/) | Ollama Web Search and Web Fetch API, SDK, MCP, OpenClaw integration | ollama search, web fetch, mcp, openclaw |
| [qdrant-codebase-search](qdrant-codebase-search/) | Semantic code search with Qdrant, Ollama, and MCP | qdrant, code search, semantic search, vector search |
| [nextcloud-admin](nextcloud-admin/) | Nextcloud administration via OCS API and WebDAV | nextcloud, webdav, ocs api, file sharing |
| [elk-kibana-dashboards](elk-kibana-dashboards/) | Elasticsearch and Kibana: log analysis, dashboards, Lens/TSVB, KQL/Lucene, DSL aggregations | elasticsearch, kibana, elk, kql, lucene, lens, tsvb, dashboard, logs |

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
claude plugin install all-skills@nord-skills       # Complete 31 skills collection
claude plugin install agency-skills@nord-skills    # Agency engineering & product bundle
claude plugin install infra-linux@nord-skills      # Linux, Docker, CI/CD, Ansible
claude plugin install ai-tools@nord-skills         # LiteLLM, OmniRoute, WebUI, Playwright
claude plugin install openwrt-routing@nord-skills  # OpenWrt (AmneziaWG, Podkop, zapret)
claude plugin install litellm-guide@nord-skills    # Specific skill plugin

# Inside an active Claude Code interactive session:
/plugin marketplace add nordz0r/skills
/plugin install all-skills@nord-skills
```

### 2. OpenAI Codex, OpenClaw, and Agent CLIs (`npx skills`)

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

## How to use

### Explicit invocation

Call the skill by name in your first prompt.

```text
Use agency-devops-automator and build CI/CD for k3s with rollback.
Use agency-ui-designer and agency-ux-architect for an admin UI redesign.
Use qdrant-codebase-search to search code and git history semantically.
Use basic-memory-workflow and check project memory before making changes.
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

## Repository structure

```text
skills/
├── .claude-plugin/
│   ├── marketplace.json  # Claude Code plugin marketplace catalog (bundles + 31 plugins)
│   └── plugin.json       # Root plugin manifest for direct installation
├── scripts/
│   └── validate-skills.js # Validation tool for manifests, frontmatter, and paths
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
