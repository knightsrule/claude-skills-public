# Claude Code Skills

A collection of reusable [Agent Skills](https://code.claude.com/docs/en/skills) for product management and SRE workflows. They follow the open [Agent Skills](https://agentskills.io) format, so they work in **Claude Code** and in **OpenAI Codex CLI** (and other runtimes that adopt the standard).

## What Are Skills?

Skills are markdown instruction files that teach an AI coding agent how to perform a specific task. Each skill is a directory containing a `SKILL.md` file. The agent reads the `description` from the frontmatter to decide when a skill is relevant, then loads the full instructions on demand — like a runbook it executes autonomously. Skills can be triggered via `/slash-commands` or automatically when the agent detects a matching request.

## Skills in This Repo

### Product

| Skill | Slash Command | Description |
|-------|---------------|-------------|
| [incubate](Product/incubate/SKILL.md) | `/incubate` | Product incubation and PRD creation through collaborative discovery. Takes a rough idea and turns it into a validated product concept with market research, competitive analysis, and go-to-market strategy. |
| [feature-design](Product/feature-design/SKILL.md) | `/feature-design` | Feature design conversation that produces a Feature Requirement Document (FRD) and updates the parent PRD. Focuses on the *what* and *why* before jumping into implementation. |
| [feature-decompose](Product/feature-decompose/SKILL.md) | `/feature-decompose` | Breaks a feature (from an FRD or idea) into implementable INVEST stories and creates them as trackable tasks in beads. |
| [prioritize](Product/prioritize/SKILL.md) | `/prioritize` | RICE-scores stories in the backlog and recommends priorities with a ranked table and approval workflow. |

**Typical flow:** `/incubate` (PRD) → `/feature-design` (FRD) → `/feature-decompose` (stories) → `/prioritize` (ranking)

### SRE

| Skill | Slash Command | Description |
|-------|---------------|-------------|
| [nextjs-saas](SRE/nextjs-saas/SKILL.md) | `/nextjs-saas` | Scaffolds a production-quality Next.js SaaS app from a name and brief — marketing site plus authenticated dashboard, Server-Component-first, semantic design tokens, mobile-first responsive, a data-access boundary, and tests. Drives the create-next-app and shadcn CLIs. |
| [fastapi-server](SRE/fastapi-server/SKILL.md) | `/fastapi-server` | Scaffolds a production-ready FastAPI server from templates with logging, CORS, request tracking, error handling, and health checks. |
| [infosec-check](SRE/infosec-check/SKILL.md) | `/infosec-check` | Pre-production security audit — checks DNS/email (SPF, DMARC, DKIM), TLS, HTTP security headers, exposed endpoints, rate limiting, and optionally Cloudflare configuration. Manual-invocation only; runs active tests, so authorization is required. |
| [promote-to-main](SRE/promote-to-main/SKILL.md) | `/promote-to-main` | Release review across multiple repos — diffs a branch vs. the default branch, performs code review, detects new env vars, recommends version bumps, and gives a GO / NO-GO verdict. |

### General

| Skill | Slash Command | Description |
|-------|---------------|-------------|
| [context-audit](general/context-audit/SKILL.md) | `/context-audit` | Audits a Claude Code setup for token waste and context bloat — MCP servers, CLAUDE.md rules, skills, settings, and file permissions — and returns a health score with specific fixes. |

## Installation

Every skill is a directory containing `SKILL.md`, so installing is a copy or symlink — no renaming.

### Claude Code

**Personal (all projects):** copy or symlink into `~/.claude/skills/`.

```bash
git clone https://github.com/knightsrule/claude-skills-public.git

# One skill
cp -r claude-skills/Product/incubate ~/.claude/skills/incubate

# All skills
find claude-skills -name SKILL.md -exec dirname {} \; | while read d; do
  cp -r "$d" ~/.claude/skills/"$(basename "$d")"
done
```

**Project-level (shared with your team):** copy into the project's `.claude/skills/`.

```bash
mkdir -p .claude/skills
cp -r claude-skills/SRE/infosec-check .claude/skills/infosec-check
```

### OpenAI Codex CLI

Same skill directories, different location — Codex discovers skills from `~/.agents/skills/` (personal) or `.codex/skills/` (project):

```bash
cp -r claude-skills/Product/incubate ~/.agents/skills/incubate
```

### Verifying Installation

Open your agent and type `/` — installed skills should appear in the autocomplete list.

## Usage

Invoke any skill by typing its slash command:

```
/incubate I have an idea for a developer productivity tool that...
/feature-design add dark mode toggle
/infosec-check https://app.example.com https://api.example.com
/promote-to-main
/fastapi-server my-api --description "User management API"
/nextjs-saas Acme Analytics — B2B analytics dashboard for SaaS founders
```

Some skills (like `feature-design` and `incubate`) are conversational — they'll ask questions before producing output. Others (like `infosec-check` and `promote-to-main`) run autonomously and produce a report. `infosec-check` and `promote-to-main` are manual-invocation only (`disable-model-invocation: true`) because they send active traffic or run expensive multi-repo reviews.

## Skill Anatomy

Each skill is a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: skill-name
description: When and how the agent should use this skill
argument-hint: "<expected> [args]"
---

Instructions the agent follows when the skill is invoked...
```

The `description` field is always in the agent's context and determines when the skill auto-triggers. The full instructions load only when invoked. Larger skills (like `nextjs-saas`) keep `SKILL.md` lean and push detail into `references/` files that load on demand.

### Frontmatter Options

| Field | Purpose | Standard? |
|-------|---------|-----------|
| `name` | Slash command name (defaults to directory name) | Agent Skills standard |
| `description` | When to trigger — the agent reads this to decide relevance | Agent Skills standard |
| `allowed-tools` | Tools the agent can use without asking permission | Agent Skills standard |
| `argument-hint` | Placeholder shown in slash-command autocomplete | Claude Code |
| `disable-model-invocation` | `true` = only manual `/` invocation, no auto-trigger | Claude Code |
| `model` | Override the model for this skill (e.g., `opus`) | Claude Code |
| `context` | `fork` = run in isolated subagent context | Claude Code |

Claude Code extension fields are ignored by runtimes that don't recognize them, so they're safe to keep for cross-tool skills.

## Dependencies

### Beads (task management)

The **feature-decompose** and **prioritize** skills use [Beads](https://github.com/gastownhall/beads) (`bd`) for task tracking — a lightweight, git-native task manager that stores tasks in your repo.

Install:

```bash
brew install beads        # macOS/Linux (Homebrew) — provides the `bd` command
```

Initialize in your project:

```bash
bd init            # Standard — commits beads files to the repo
bd init --stealth  # Personal — keeps beads files out of git
```

If beads isn't installed, these skills will tell you and suggest setup steps. The skills defensively run `bd --help` when a subcommand's syntax differs across versions. The other skills have no external dependencies beyond the agent itself.

### Runtime notes

Some skills reference Claude Code capabilities that other runtimes lack — subagents (`Explore`, `general-purpose`), plan mode. Each of those spots includes an inline fallback ("if subagents aren't available, do the work inline"), so the skills degrade gracefully under Codex or other agents.

## Contributing

To add a new skill:

1. Create a directory with a `SKILL.md` file (plus `references/` / `scripts/` / `assets/` if needed)
2. Place it under the appropriate category (`Product/`, `SRE/`, `general/`, or create a new one)
3. Include clear `name` and `description` frontmatter, and an `argument-hint` if the skill takes arguments
4. Keep `SKILL.md` lean; push long detail into `references/` files
5. Update this README with the new skill

## License

MIT
