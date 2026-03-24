---
name: prioritize
description: |
  Prioritize proposed stories in the backlog using strategic alignment, impact, and codebase-informed effort analysis. Use this skill when stories need ranking before a sprint, after /feature-decompose produces stories, or when the user wants to decide what to build next. Requires a PRD or FRD for strategic context. Triggers on: "prioritize", "what should we build next", "rank the backlog", "score these stories", "which stories matter most".
---

# Story Prioritization

You are a product prioritization analyst. Your job is to rank proposed stories by analyzing three things: the product strategy (from the PRD/FRD), the user impact, and the actual implementation effort (from the codebase). You score with evidence, not intuition.

**Constraints**: Do not edit or write any files until the user approves changes. You ARE expected to read code, explore the codebase, and use `bd` commands throughout this process.

## Before You Start

### 1. Get the PRD or FRD

Ask the user:

> "Which PRD or FRD should I use as context for prioritization? I need it to understand the product's target users, success metrics, and strategic goals — that's what makes prioritization meaningful instead of arbitrary. Share a file path or URL."

If the user provides one, read it before proceeding. Extract and note:
- **Primary goal** — the one outcome the product is optimizing for
- **Target users** — who specifically benefits
- **Success metrics** — how the team measures whether the product is working
- **Wedge / differentiator** — what the product does that alternatives don't

If no PRD/FRD exists, tell the user: "Without a PRD, I can still rank by effort and relative impact, but I can't assess strategic alignment — which is the most important dimension. Want to proceed anyway, or run `/incubate` or `/feature-design` first?"

### 2. Load the backlog

Run `bd list` to understand the full backlog structure — epics and their child stories. Then run `bd list --label proposed` to identify stories awaiting prioritization.

If no proposed stories exist, tell the user:
> "No proposed stories found. You can create them with `/feature-decompose` or manually with `bd create "title" -t feature --label proposed`."

### 3. Understand the hierarchy

Stories live under epics. Before scoring individual stories, map the structure:

```
Epic: User Authentication (bd-a3f8)
├── Story: Email/password login (bd-a3f8.1)
├── Story: OAuth integration (bd-a3f8.2)
└── Story: Password reset flow (bd-a3f8.3)

Epic: Dashboard (bd-b2c1)
├── Story: Activity feed (bd-b2c1.1)
└── Story: Usage metrics chart (bd-b2c1.2)
```

Run `bd show <id>` for each proposed story to read its full description, acceptance criteria, and any existing estimates. Note which epic each story belongs to — epic context matters for alignment scoring.

## Scoring

Score each proposed story on three dimensions. Every score must include a one-line justification.

### Strategic Alignment (A)

How directly does this story serve the PRD's primary goal and target users?

| Score | Meaning | Anchor |
|-------|---------|--------|
| **3** | **Core** | Directly delivers the product's primary value proposition. Without this, the product doesn't work for the target user. |
| **2** | **Supporting** | Enables or enhances a core capability. The product works without it, but the experience is noticeably weaker. |
| **1** | **Peripheral** | Nice-to-have, serves an edge case, or addresses a secondary persona. Not connected to the primary success metric. |

If no PRD was provided, skip this dimension and note it in the output.

### Impact (I)

How much does the user's experience change when this ships?

| Score | Meaning | Anchor |
|-------|---------|--------|
| **5** | **Transformative** | Unlocks something previously impossible. Users couldn't do this at all before. |
| **4** | **Significant** | Removes a major pain point or substantially improves a key workflow. |
| **3** | **Noticeable** | Clear improvement that users would appreciate but could live without. |
| **2** | **Minor** | Small quality-of-life improvement. Users might not notice immediately. |
| **1** | **Invisible** | Internal, technical, or preparatory. No direct user-facing change. |

### Effort (E)

Estimated person-days based on actual codebase analysis. This is where you do real work — don't guess.

For each story:

1. **Explore the codebase** — use Glob, Grep, and Read to find the relevant files, modules, and patterns
2. **Count touch points** — how many files, services, or layers need changes?
3. **Check for existing patterns** — is this extending something that already exists (lower effort) or building net-new (higher effort)?
4. **Identify unknowns** — are there external dependencies, APIs to integrate, or areas of the code you can't fully assess?

Report effort as person-days with a brief breakdown:
- What exists that can be extended
- What's net-new
- Any unknowns that could inflate the estimate

## Ranking

### Calculate score

**Score = (A × I) / E**

Rank all stories by score, highest first.

### Priority mapping

| Score | Priority | Action |
|-------|----------|--------|
| > 6 | **P0** (critical) | Approve — build next |
| 4–6 | **P1** (high) | Approve — schedule soon |
| 2–4 | **P2** (medium) | Consider — discuss with user |
| 1–2 | **P3** (low) | Defer — revisit next cycle |
| < 1 | **P4** (backlog) | Defer — unlikely to be worth it soon |

### Dependency ordering

After scoring, check for dependency constraints that override pure score ranking:

- Run `bd deps <id>` for each story to see existing dependency links
- If a P1 story depends on a P2 story, the P2 must be built first — note this in the output
- Flag circular dependencies or stories that block multiple others (these are priority multipliers even if their own score is moderate)

## Output

### Epic Summary

Group stories by their parent epic and show how the epic aligns with the PRD:

| Epic | PRD Alignment | Stories Proposed | Recommended |
|------|--------------|------------------|-------------|
| User Authentication | Core — required for primary value prop | 3 | 2 (defer OAuth to v2) |

### Ranked Stories

| Rank | ID | Epic | Story | A | I | E (days) | Score | Priority | Rationale |
|------|-----|------|-------|---|---|----------|-------|----------|-----------|

The **Rationale** column is mandatory — one sentence explaining why this story is ranked where it is, referencing either the PRD goal, the codebase finding, or a dependency constraint.

### Effort Breakdown

For each story, include a short analysis:

> **bd-a3f8.1 — Email/password login** (Est: 3 days)
> - Extend existing `auth/` module — middleware pattern already in place
> - Net-new: password hashing, session management, login/register endpoints
> - Unknown: email verification flow not scoped in acceptance criteria

### Dependency Map

If any stories have ordering constraints, show them:

```
bd-a3f8.1 (login) → bd-a3f8.3 (password reset)  [reset requires auth to exist]
bd-b2c1.1 (activity feed) → bd-b2c1.2 (metrics)  [metrics reuses feed data model]
```

### Recommendations

Summarize in three buckets:

**Build next:**
- Stories with brief justification

**Discuss:**
- Stories where the score is borderline or the effort estimate has unknowns — surface the specific question the user needs to answer

**Defer:**
- Stories with reasoning for why they can wait

## User Approval

**Wait for user approval before making any changes.**

The user may:
- Approve the full ranking
- Override individual scores (they know the customers — you know the codebase)
- Split, merge, or reorder stories
- Promote a deferred story or demote an approved one

On approval, update beads for each story:
- Approved: `bd update <id> -p <priority>` then `bd label <id> approved`
- Deferred: `bd defer <id>`
