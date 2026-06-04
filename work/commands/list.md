---
description: Display the current work queue
---

## Queue Location

Resolve the queue root at the project root:

- If `docs/` exists → queue root is `docs/work/`
- Otherwise → queue root is `work/`

The queue file is `<queue-root>/queue.md`. Detail files live in the same directory.

## Display

Read `<queue-root>/queue.md` and display it to the user.

If the file doesn't exist, report that no work queue has been created yet and suggest using `/work:add` to create the first task.

Count and summarize:
- Pending tasks (`- [ ]`)
- In-progress tasks (`- [-]`)
- Completed tasks (`- [x]`)
- Rejected tasks (`- [~]`)

Also check `<queue-root>/` for any detail files and note which pending tasks have additional context available.
