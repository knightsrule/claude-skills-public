# Claude Code Skills

A collection of reusable [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills for product management and SRE workflows.

## What Are Skills?

Skills are markdown instruction files that teach Claude Code how to perform specific tasks. When invoked, Claude loads the skill and follows its instructions — like a runbook it executes autonomously. Skills can be triggered via `/slash-commands` or automatically when Claude detects a matching request.

## Skills in This Repo

### Product

| Skill | Slash Command | Description |
|-------|---------------|-------------|
| [incubate](Product/incubate-SKILL.md) | `/incubate` | Product incubation and PRD creation through collaborative discovery. Takes a rough idea and turns it into a validated product concept with market research, competitive analysis, and go-to-market strategy. |
| [feature-design](Product/feature-design-SKILL.md) | `/feature-design` | Feature design conversation that produces a Feature Requirement Document (FRD). Focuses on the *what* and *why* before jumping into implementation. |
| [feature-decompose](Product/feature-decompose-SKILL.md) | `/feature-decompose` | Breaks a feature (from an FRD or idea) into implementable INVEST stories and creates them as trackable tasks. |
| [prioritize](Product/prioritize-SKILL.md) | `/prioritize` | RICE-scores stories in the backlog and recommends priorities with a ranked table and approval workflow. |

**Typical flow:** `/incubate` (PRD) → `/feature-design` (FRD) → `/feature-decompose` (stories) → `/prioritize` (ranking)

### SRE

| Skill | Slash Command | Description |
|-------|---------------|-------------|
| [fastapi-server](SRE/fastapi-server/SKILL.md) | `/fastapi-server` | Scaffolds a production-ready FastAPI server from templates with logging, CORS, request tracking, error handling, and health checks. |
| [infosec-check](SRE/infosec-check-SKILL.md) | `/infosec-check` | Pre-production security audit — checks DNS/email (SPF, DMARC, DKIM), TLS, HTTP security headers, exposed endpoints, rate limiting, and optionally Cloudflare configuration. |
| [promote-to-main](SRE/promote-to-main-SKILL.md) | `/promote-to-main` | Release review across multiple repos — diffs dev vs. main, performs code review, detects new env vars, recommends version bumps, and gives a GO / NO-GO verdict. |

## Installation

### Option 1: Personal Skills (Available in All Projects)

Copy individual skill files into your personal Claude skills directory:

```bash
# Clone the repo
git clone https://github.com/knightsrule/claude-skills-public.git

# Copy a single-file skill
cp claude-skills/Product/incubate-SKILL.md ~/.claude/skills/incubate/SKILL.md

# Copy a directory-based skill (with assets)
cp -r claude-skills/SRE/fastapi-server ~/.claude/skills/fastapi-server
```

Each skill must live in its own directory under `~/.claude/skills/` with the entrypoint named `SKILL.md`:

```
~/.claude/skills/
├── incubate/
│   └── SKILL.md
├── feature-design/
│   └── SKILL.md
├── fastapi-server/
│   ├── SKILL.md
│   ├── assets/
│   ├── references/
│   └── scripts/
└── ...
```

### Option 2: Project-Level Skills (Shared with Your Team)

Copy skills into your project's `.claude/skills/` directory so anyone who clones the repo gets them:

```bash
mkdir -p .claude/skills

# Copy a skill into your project
cp claude-skills/SRE/infosec-check-SKILL.md .claude/skills/infosec-check/SKILL.md
```

### Option 3: Install All Skills at Once

```bash
git clone https://github.com/knightsrule/claude-skills-public.git

# Install all single-file skills
for f in claude-skills/**/*-SKILL.md; do
  name=$(basename "$f" -SKILL.md)
  mkdir -p ~/.claude/skills/"$name"
  cp "$f" ~/.claude/skills/"$name"/SKILL.md
done

# Install directory-based skills
cp -r claude-skills/SRE/fastapi-server ~/.claude/skills/fastapi-server
```

### Verifying Installation

Open Claude Code and type `/` — your installed skills should appear in the autocomplete list.

## Usage

Invoke any skill by typing its slash command in a Claude Code session:

```
/incubate I have an idea for a developer productivity tool that...

/feature-design add dark mode toggle

/infosec-check https://app.example.com https://api.example.com

/promote-to-main

/fastapi-server my-api --description "User management API"
```

Some skills (like `feature-design` and `incubate`) are conversational — they'll ask questions before producing output. Others (like `infosec-check` and `promote-to-main`) run autonomously and produce a report.

## Skill Anatomy

Each skill is a markdown file with YAML frontmatter:

```yaml
---
name: skill-name
description: When and how Claude should use this skill
---

Instructions that Claude follows when the skill is invoked...
```

The `description` field is always in Claude's context and determines when the skill auto-triggers. The full instructions load only when invoked.

### Frontmatter Options

| Field | Purpose |
|-------|---------|
| `name` | Slash command name (defaults to directory name) |
| `description` | When to trigger — Claude reads this to decide relevance |
| `disable-model-invocation` | `true` = only manual `/` invocation, no auto-trigger |
| `allowed-tools` | Tools Claude can use without asking permission |
| `model` | Override the model for this skill (e.g., `opus`) |
| `context` | `fork` = run in isolated subagent context |

## Dependencies

Some skills rely on external tools:

### Beads (Task Management)

The **feature-decompose** and **prioritize** skills use [Beads](https://github.com/cosmosgenius/beads) (`bd`) for task tracking. Beads is a lightweight, git-native task manager that stores tasks as files in your repo.

Install beads before using these skills:

```bash
pip install beads-cli
```

Initialize in your project:

```bash
bd init            # Standard — commits beads files to the repo
bd init --stealth  # Personal — keeps beads files out of git
```

Skills that use beads: `feature-decompose`, `prioritize`

If beads isn't installed, these skills will let you know and suggest setup steps. The other skills (incubate, feature-design, infosec-check, fastapi-server, promote-to-main) have no external dependencies beyond Claude Code itself.

## Contributing

To add a new skill:

1. Create a `SKILL.md` file (or a directory with `SKILL.md` + supporting files)
2. Place it under the appropriate category (`Product/`, `SRE/`, or create a new one)
3. Use the naming convention `<skill-name>-SKILL.md` for single-file skills
4. Include clear `name` and `description` frontmatter
5. Update this README with the new skill

## License

MIT
