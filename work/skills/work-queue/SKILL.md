---
name: work-queue
description: "Persistent FIFO work queue for managing tasks within a project. Use when the user mentions 'work queue', asks about pending tasks, wants to add work items, or needs to process queued tasks. Provides the queue format, conventions, and task processing workflow."
---

# Work Queue System

A persistent FIFO (first-in, first-out) work queue that lives in each project. Tasks are processed one at a time by isolated worker agents, ensuring clean commits and traceable progress.

## Queue Location

Resolve the queue root at the project root:

- If `docs/` exists → queue root is `docs/work/`
- Otherwise → queue root is `work/`

Create the queue root directory if it doesn't exist. All path examples below use `docs/work/` — substitute the resolved root.

## Queue File

Location: `<queue-root>/queue.md`

```markdown
# Work Queue

- [ ] Fix authentication timeout in session middleware
- [-] Add rate limiting to public API endpoints
- [x] Update dependencies to latest patch versions
- [~] ~~Add caching layer~~ (rejected: premature, no performance data yet)
```

### Status Markers

- `- [ ]` — Pending (not yet started)
- `- [-]` — In progress (actively being worked on)
- `- [x]` — Completed
- `- [~]` — Rejected (title struck through, reason in parentheses)

### Order

FIFO — tasks are processed top-to-bottom. New tasks are appended after existing pending items but before completed/rejected items.

## Detail Files

Location: `<queue-root>/` (same directory as `queue.md`)

For complex tasks that need more context than a checklist line, create a detail file:

```
docs/work/
├── queue.md
├── fix-auth-timeout.md
└── add-rate-limiting.md
```

Filenames are slugified versions of the task title. Content:

```markdown
# Fix Authentication Timeout

## Problem
Sessions expire after 5 minutes even with active use.

## Acceptance Criteria
- Sessions extend on activity
- Default timeout: 30 minutes of inactivity
- Configurable via environment variable

## Relevant Files
- src/middleware/auth.ts
- src/config/session.ts

## Constraints
- Maintain backward compatibility with existing session tokens
```

## Task Processing Workflow

Each task goes through this pipeline:

1. **Claim** — Pick the first `- [ ]` item, immediately mark it `- [-]` and commit
2. **Load Context** — Read detail file if it exists
3. **Validate** — Still needed? Duplicate?
4. **Plan** — Best approach?
5. **Execute** — Do the work
6. **Complete** — Mark `- [-]` → `- [x]` (or `- [~]` if rejected), commit with the work

**Critical:** The queue file MUST be updated at both the start (in-progress) and end (completed/rejected) of every task.

## Commands

- `/work:list` — Display the current queue
- `/work:add <idea>` — Add a task (asks clarifying questions first)
- `/work:next` — Process next pending task (auto-continues until empty)
- `/work:monitor [start|stop|status]` — Watch the queue and auto-run `/work:next` whenever pending tasks appear
