---
name: feature-decompose
description: |
  Break a feature into implementable INVEST stories and create them in beads. Use this skill after /feature-design produces an FRD, after a plan mode session, or when the user has a clear feature idea and wants it decomposed into stories. Triggers on: "break this into stories", "decompose this feature", "create stories for...", "add to beads", or any variation where the intent is to produce implementable work items from a defined feature. Accepts an optional FRD path or URL as input — if one exists, use it as the source of truth for scope and acceptance criteria.
---

# Feature Decompose

You are a product engineer. Your job is to take a feature — whether described in an FRD, a plan mode output, or a rough idea — and break it into implementable INVEST stories, grounded in the actual codebase, then create them in beads.

## Input

The user invokes `/feature-decompose` with an optional feature description or FRD reference:

- `/feature-decompose` — you'll ask for context upfront
- `/feature-decompose add dark mode toggle` — feature idea, no FRD
- `/feature-decompose path/to/FRD-dark-mode.md` — local FRD
- `/feature-decompose https://...` — public FRD or doc URL

## Before You Start

### 1. Get the FRD (if one exists)

Ask upfront:

> "Is there an FRD or design doc for this feature? If so, share the file path or URL — I'll use it as the source of truth for scope and acceptance criteria. If not, no problem — describe what you want to build and I'll work from that."

If the user provides:
- A **local path**: read the file before proceeding
- A **URL**: fetch the content before proceeding
- **Nothing**: proceed from the feature description in `$ARGUMENTS` or the user's description

If you just finished a plan mode session, use the approved plan as the basis for story breakdown instead of starting from scratch.

### 2. Understand the codebase

Read `CLAUDE.md` for project context, architecture, and conventions. Then explore the relevant areas of the codebase — backend and/or frontend — to understand:

- What already exists that this feature builds on
- What's genuinely new work vs. extending existing code
- Which sub-repos are involved (backend, frontend, etc.)

This step ensures stories reflect reality, not just the FRD's idealized view.

## Phase 1: Story Plan

Present a breakdown to the user **before creating anything**.

### Story table

| # | Story Title | Type | Sub-repo | Estimate | Acceptance Criteria Summary | Dependencies |
|---|-------------|------|----------|----------|-----------------------------|--------------|

Include only stories that represent **genuinely new work** given what already exists in the codebase. Flag any FRD scope items that are already implemented.

### Story rules

Each story must be **INVEST**:

- **Independent**: Can be built and delivered without depending on other stories in the set (or declare the dependency explicitly)
- **Negotiable**: Captures the outcome, not the implementation — there's room for conversation during development
- **Valuable**: Delivers something a user can see, use, or benefit from on its own — a vertical slice, not a layer
- **Estimable**: Scoped enough to size in person-days
- **Small**: Completable in 1-3 days by one developer
- **Testable**: Has clear, verifiable acceptance criteria

Avoid horizontal stories like "build the database layer" or "create the API." Every story should touch all layers needed to deliver one complete, usable capability.

### Sizing

- Prefer **3-6 stories** per feature. More than 6 suggests the feature is too large — offer to split into phases.
- Backend and frontend work for the same user-facing feature should be **separate stories** (they go to different sub-repos and can be worked in parallel).
- Estimate in minutes: 480 = 1 day, 960 = 2 days, 1440 = 3 days.
- Use type `feature` for new functionality, `task` for technical work, `bug` for fixes, `chore` for maintenance.

### Quality checks (do before presenting)

- Can each story be **demo'd independently**? If not, it's not vertical enough.
- Does the full set **cover the FRD scope**? Flag gaps.
- Are stories **ordered sensibly**? Core-value stories first; edge cases and polish last.
- Is there a **"glue" story**? Check that a story exists for the entry point — how the user navigates to or discovers this feature. This is the most commonly forgotten story.
- Does any story feel like it could take **weeks**? Break it down further.

## Phase 2: User Approval

Wait for user approval before creating anything in beads. The user may:

- Approve all stories
- Remove, split, or merge stories
- Adjust acceptance criteria or estimates
- Change sub-repo assignments

## Phase 3: Create in Beads

### Check for overlap first

Before creating anything, check what already exists:

```bash
bd ready
```

Scan existing tasks for overlap with the stories you're about to create. If you find similar or related tasks, flag them: "I see an existing task `bd-c2f1` — 'User login flow' — which looks related to Story 3. Should I link to it, skip creating a duplicate, or is this genuinely different?" Don't blindly create duplicates.

### Create the epic

Create an epic for the feature, linking it to the FRD so anyone who finds the epic can trace back to the full design context:

```bash
bd create "<Feature Name>" -p <priority>
```

Then update it with the FRD reference:

```bash
bd update <epic-id> --description "FRD: <path-or-url>

<Brief problem statement from the FRD or user description>"
```

If there's no FRD, use a brief summary of the feature instead.

### Create each story

Beads uses dotted hierarchical IDs under the epic:
- `bd-a3f8` → Epic
- `bd-a3f8.1` → Story 1
- `bd-a3f8.1.1` → Sub-task of Story 1 (if needed)

For each story, embed the FRD link in the description so the context travels with the task:

```bash
bd create "<Story title>" -t <type> -p <priority>
bd update <story-id> --description "As a <user>, I want to <action>, so that <outcome>.

Acceptance Criteria:
- <criterion 1>
- <criterion 2>

FRD: <path-or-url>" --acceptance "<criteria separated by semicolons>" -e <minutes> --label proposed
```

The FRD link at the bottom of every story means a developer picking up a story weeks later can always trace back to the broader "what and why."

### Set up dependencies

```bash
bd dep add <child-id> <parent-id>
```

Only add dependencies where ordering is genuinely blocking (e.g., "user can log in" blocks "user can view their dashboard"). Don't over-link.

### Priority mapping

- `-p 0` — Critical / must-have for launch (core-value stories)
- `-p 1` — Important / core functionality
- `-p 2` — Nice-to-have / polish (edge cases, refinement stories)

### Confirm

Run `bd list --label proposed` and show the user what was created.

### If beads isn't initialized

If `bd` commands fail, the user may need to run `bd init` first (or `bd init --stealth` for personal use without committing beads files to the repo). Let them know and offer to help set it up.

If anything doesn't work as expected, run `bd --help` or `bd create --help` to check the exact syntax and adapt accordingly.
