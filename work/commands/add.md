---
description: Add a task to the work queue
argument-hint: <idea or task description>
---

You are adding a new task to the project's work queue.

The user's idea: `$ARGUMENTS`

If no arguments were provided, ask the user what task they'd like to add.

## Queue Location

Resolve the queue root at the project root:

- If `docs/` exists → queue root is `docs/work/`
- Otherwise → queue root is `work/`

The queue file is `<queue-root>/queue.md`. Detail files live in `<queue-root>/`. All path examples below assume `docs/work/` — substitute the resolved root.

## Process

### Step 1: Understand the Task

Ask the user clarifying questions using AskUserQuestion to fully understand the task BEFORE adding it. The goal is to capture enough context that a worker agent can execute this task later without needing to ask anything.

Consider asking about (pick 1-2 relevant questions, not all):
- **What problem does this solve?** (if not obvious)
- **What's the expected outcome?** (acceptance criteria)
- **Any constraints or things to avoid?**
- **Which files or areas of the codebase are relevant?** (if the user knows)

Simple, self-explanatory tasks (like "update README", "fix typo in header", "remove unused import in foo.ts") don't need clarification — just add them directly.

### Step 2: Create the Queue File (if needed)

If `<queue-root>/queue.md` doesn't exist, create the directory and file:

```markdown
# Work Queue
```

### Step 3: Add the Task

Append the task as a new `- [ ]` item to the queue. Insert it AFTER existing pending items but BEFORE any completed/rejected items. If all items are pending or the queue is new, append at the end.

Write a clear, concise task title for the checklist line.

### Step 4: Create Detail File (if needed)

If the task is complex enough to warrant additional context (based on the clarifying questions), save a detail file at `<queue-root>/<slug>.md`:

```markdown
# Task Title

## Problem
What problem this solves.

## Acceptance Criteria
- Specific, testable outcomes

## Relevant Files
- file paths if known

## Constraints
- Things to avoid or maintain
```

Simple tasks don't need a detail file — the checklist line is enough.

### Step 5: Confirm

Show the user what was added:
- The checklist line that was appended
- Whether a detail file was created (and where)
- Current queue position (e.g., "3rd in queue, 2 tasks ahead")
