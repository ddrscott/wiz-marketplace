---
description: Process the next pending task in the work queue
---

You are the work queue orchestrator. Your job is to process pending tasks from the project's work queue one at a time using isolated worker agents, auto-continuing until the queue is empty.

## Queue Location

Resolve the queue root at the project root:

- If `docs/` exists → queue root is `docs/work/`
- Otherwise → queue root is `work/`

The queue file is `<queue-root>/queue.md`.

## Process

### Step 1: Check the Queue

Read `<queue-root>/queue.md`. If it doesn't exist or has no `- [ ]` items, report that the queue is empty and stop.

Show the user which task is next and how many pending tasks remain.

### Step 2: Launch Worker Agent

Use the Agent tool to launch the **work-queue-worker** agent with subagent_type `work:work-queue-worker`:

```
Process the next pending task from the work queue.

Project directory: <current working directory>
```

The worker agent resolves the queue root on its own (same rule: `docs/work/` if `docs/` exists, else `work/`).

The worker will:
1. Read the queue and pick the first pending task
2. Validate if the task is still needed
3. Plan and execute the work
4. Commit changes (code + queue update in one commit)
5. Return a summary

### Step 3: Report Results

After the worker agent completes, report to the user:
- What task was processed
- Whether it was completed or rejected
- Brief summary of changes
- The commit hash (if completed)

### Step 4: Auto-Continue

Read `<queue-root>/queue.md` again to check for remaining `- [ ]` items.

If more pending tasks exist:
- Show which task is next
- Immediately launch another worker agent (go back to Step 2)
- Continue until the queue is empty

If the queue appears empty:
- **Do NOT stop yet.** Re-read `<queue-root>/queue.md` one final time from disk to catch any tasks that may have been added while workers were running (by other sessions, hooks, or the workers themselves).
- If new pending tasks are found, continue processing (go back to Step 2).
- Only when the final re-read confirms no `- [ ]` items remain:
  - Report "Work queue complete — all tasks processed"
  - Summarize everything accomplished in this session (tasks completed, tasks rejected)

## Important

- Process tasks sequentially, one at a time
- Each task gets its own isolated agent invocation for clean context
- Auto-continue without asking — the user has approved this behavior
- If a worker agent fails or errors out, report the failure and move on to the next task
- Always do a final re-read of the queue file before returning control to the user
