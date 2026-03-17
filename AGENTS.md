# PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-17 (working tree snapshot)
**Base commit:** 0bc69a8
**Branch:** main

## OVERVIEW

Collection of reusable skills for `Claude Code`, `Codex`, and similar AI-agent CLIs. The repo is documentation-first: each skill is a markdown knowledge package with optional `references/`, `scripts/`, and `evals/`. Distribution is through `npx skills add nordz0r/skills`.

The repository is no longer Russian-only:

- `README.md` is the primary Russian landing page.
- `README.en.md` is the English companion for discovery and catalog indexing.
- `agency-*` skills are English.
- Most product/domain guides are Russian.

## ROOT STRUCTURE

```text
skills/
├── README.md                         # Primary RU landing page + install/use index
├── README.en.md                      # EN companion README for discovery/catalogs
├── AGENTS.md                         # Repo knowledge base for coding agents
├── .gitattributes                    # Shell scripts forced to LF
├── .gitignore                        # IDE-only ignores
├── agency-*/                         # 10 English meta-skills, each with evals/evals.json
├── basic-memory-workflow/            # Local basic-memory operating workflow
├── nextcloud-admin/                  # Nextcloud OCS API + WebDAV
├── ollama-search/                    # Ollama Web Search / Fetch API + scripts
├── playwright-skill/                 # Playwright browser automation + Node runtime
├── open-terminal-guide/              # Open Terminal guide
├── open-webui-guide/                 # Largest reference set
├── amneziawg-openwrt-guide/          # AmneziaWG on OpenWrt
├── podkop-openwrt-guide/             # Podkop / sing-box on OpenWrt
├── qdrant-codebase-search/           # Qdrant + Ollama semantic code search + scripts
└── zapret-openwrt-guide/             # zapret-openwrt guide
```

## CURRENT SKILL INVENTORY

### Agency family

- `agency-devops-automator`
- `agency-sre`
- `agency-incident-response-commander`
- `agency-security-engineer`
- `agency-database-optimizer`
- `agency-technical-writer`
- `agency-ui-designer`
- `agency-ux-architect`
- `agency-ux-researcher`
- `agency-whimsy-injector`

All 10 `agency-*` skills currently follow the same pattern:

- `SKILL.md`
- `evals/evals.json`
- no `references/`
- no `scripts/`

### Domain and workflow skills

- `basic-memory-workflow`
- `nextcloud-admin`
- `ollama-search`
- `playwright-skill`
- `open-terminal-guide`
- `open-webui-guide`
- `amneziawg-openwrt-guide`
- `podkop-openwrt-guide`
- `qdrant-codebase-search`
- `zapret-openwrt-guide`

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Root repo positioning / install / discovery | `README.md`, `README.en.md` | Keep both updated when adding or renaming skills |
| Trigger wording for a skill | `<skill>/SKILL.md` frontmatter | `description` is the main auto-trigger surface for agents |
| Frontmatter example | Any `SKILL.md` | `name` must match directory name; `metadata` is optional |
| Eval prompt examples | `agency-*/evals/evals.json` | Useful for trigger QA and smoke tests |
| OpenClaw metadata example | `ollama-search/SKILL.md` | Currently the clearest `metadata.openclaw` example |
| Script patterns | `ollama-search/scripts/`, `qdrant-codebase-search/scripts/`, `playwright-skill/scripts/` | Bash wrappers, Node executors, and setup helpers |
| Largest reference set | `open-webui-guide/references/` | 11 files; best example of deep multi-file documentation |
| Memory workflow conventions | `basic-memory-workflow/SKILL.md` | How this environment expects project memory to be used |
| OpenWrt skill patterns | `amneziawg-openwrt-guide/`, `podkop-openwrt-guide/`, `zapret-openwrt-guide/` | Good templates for Russian infra/network docs |

## CONVENTIONS

### Skill layout

```text
<skill-name>/
├── SKILL.md
├── evals/         # optional; used heavily by agency-* skills
├── scripts/       # optional; currently present in ollama-search, qdrant-codebase-search, and playwright-skill
└── references/    # optional; one topic per file
```

### Frontmatter

```yaml
---
name: skill-name
description: "Natural-language trigger surface for agent matching"
metadata: {...}   # optional
---
```

### Naming and content

- Skill directories use `kebab-case`.
- `name` in `SKILL.md` matches the directory name.
- `description` should be concrete and rich in domain terms; avoid vague slogans.
- Reference files use lowercase topic names such as `api.md`, `config.md`, `troubleshooting.md`.
- Shell scripts follow `<skill>-<action>.sh` when they are skill-specific.
- Code snippets and variable names stay in English even inside Russian docs.

### Language model

- Root docs are bilingual: Russian primary, English companion.
- `agency-*` content is English.
- Most product-specific guides are Russian.
- Do not assume "all docs are Russian" anymore.

### Git and repo hygiene

- Conventional commit style fits the repo well: `feat(scope):`, `fix(scope):`, `docs(scope):`.
- `.gitattributes` enforces LF for `*.sh`.
- `.gitignore` only ignores `.idea` and `.vscode`.
- No `package.json`, no GitHub Actions, no `LICENSE` file, and no `.claude/settings.local.json` are currently present in the repo root.

## NOTABLE PATTERNS

- Documentation-first repo: the skills are the product.
- Repo-level discovery matters: `README.md` and `README.en.md` are part of search/catalog visibility, not just human docs.
- Runtime auto-triggering still depends primarily on each skill's `SKILL.md`, especially `description`.
- Env-based configuration is common for integration skills: `OLLAMA_SEARCH_API_KEY`, `NEXTCLOUD_URL`, and similar variables are documented in-skill.
- `ollama-search`, `qdrant-codebase-search`, and `playwright-skill` currently ship executable `scripts/`.
- `playwright-skill` is an imported third-party runtime skill with a root `package.json`, a Node executor, and a large reference file.
- `open-webui-guide` has the deepest reference tree and is the best template for a large guide.
- `basic-memory-workflow` is a workflow skill, not a product/API guide.

## COMMANDS

```bash
# List available skills
npx skills add nordz0r/skills -l

# Install all skills into the current project
npx skills add nordz0r/skills

# Install all skills globally
npx skills add nordz0r/skills -g

# Install one skill globally
npx skills add nordz0r/skills -s open-webui-guide -g
```

## NOTES

- Current inventory: 20 skills total.
- `agency-*` accounts for 10 of those 20 skills.
- `open-webui-guide` has 11 reference files and is still the largest single documentation set.
- `ollama-search` has 4 reference files and 2 scripts.
- `playwright-skill` has 1 reference file, 2 script files, and a root `package.json`.
- `qdrant-codebase-search` has 2 reference files and 2 scripts.
- `basic-memory-workflow` has only `SKILL.md`; no `references/`, `scripts/`, or `evals/`.
- The old AGENTS snapshot was stale: it described only 5 skills and predated the bilingual root README.
