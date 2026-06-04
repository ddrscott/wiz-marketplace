---
description: Watch the work queue and auto-run /work:next whenever pending tasks appear
argument-hint: "[start|stop|status] [--interval N]"
---

# /work:monitor

Args: `$ARGUMENTS`

You are running the `/work:monitor` slash command. It keeps a background watcher on the
project's work queue. When new pending tasks (`- [ ]`) appear, the watcher wakes you and you
run the `/work:next` flow to drain them — fully hands-off, the same way `app-feedback-now`
watches its inbox.

## Queue Location

Resolve the queue root at the project root (identical rule used by every `work` command):

- If `docs/` exists → queue root is `docs/work/`
- Otherwise → queue root is `work/`

The queue file is `<queue-root>/queue.md`. Substitute the resolved path everywhere `<QUEUE>`
appears below.

## Routing

Parse `$ARGUMENTS`:
- Empty / starts with `--` → treat as `start` with those flags
- Starts with `start`, `stop`, or `status` → run that subcommand
- Anything else → run `start`

Optional flag (only meaningful for `start`):
- `--interval N` — poll interval in seconds (default `3`). Local file, so keep it small.

## Subcommand: start

1. **Resolve the queue root** and the absolute path to `<QUEUE>`. If the queue file does not
   exist yet, that's fine — the watcher will pick up tasks the moment `/work:add` creates it.
   Tell the user which queue file you're watching.

2. **Check for an existing monitor.** Use `TaskList` and look for a running monitor whose
   description starts with `work-queue monitor`. If one is already running for this project,
   report that and stop — do not start a second watcher.

3. **Start a persistent Monitor** on the queue file. The watcher is edge-triggered: it emits a
   line only when the count of pending `- [ ]` items *increases* (new work added), never while
   the queue is draining. This prevents notification floods while you process tasks.

   Use the `Monitor` tool with `persistent: true` and this command (substitute `<QUEUE>` and the
   interval):

   ```bash
   QUEUE='<QUEUE>'; prev=0
   while true; do
     if [ -f "$QUEUE" ]; then
       cur=$(grep -c '^- \[ \]' "$QUEUE")
     else
       cur=0
     fi
     if [ "$cur" -gt "$prev" ]; then
       echo "work-queue: $cur pending task(s) — run /work:next"
     fi
     prev=$cur
     sleep <interval>
   done
   ```

   Set the Monitor `description` to `work-queue monitor (<queue-root>)` so `stop`/`status` can
   find it via `TaskList`.

   Notes on the trigger logic:
   - `prev` starts at `0`, so if the queue already has pending tasks when you start, it fires on
     the first poll — existing work gets processed immediately.
   - While `/work:next` processes tasks they go `- [ ]` → `- [-]` → `- [x]`, so the pending count
     only ever *decreases* during a drain — no spurious re-triggers.
   - A task added by `/work:add` (or another session) raises the count → one notification.

4. **Tell the user it's armed**, in this shape (fill the placeholders):

   > **work-queue monitor is running.**
   > Watching: `<QUEUE>` · poll: `<interval>s`
   >
   > Add tasks with `/work:add` from anywhere — I'll auto-run `/work:next` and drain the queue
   > whenever pending work appears. Use `/work:monitor stop` to disarm.

## When a notification fires

A monitor notification (`work-queue: N pending task(s) — run /work:next`) is **not** a user
message — it's the watcher waking you. When one arrives:

1. Run the **`/work:next`** flow: launch `work:work-queue-worker` agents one at a time and
   auto-continue until the queue is empty (see `${CLAUDE_PLUGIN_ROOT}/commands/next.md` for the
   exact orchestration — claim, execute, commit, re-read, repeat).
2. `/work:next` already drains the *entire* queue and does a final re-read, so a single
   notification handles a whole batch. If another notification lands while you're mid-drain,
   treat it as a no-op once the queue reads empty — don't launch redundant workers.
3. The watcher stays armed for the next batch. Do not restart it.

## Subcommand: stop

1. Use `TaskList` to find the monitor whose description starts with `work-queue monitor`.
2. `TaskStop` it. If none is running, say so.
3. Confirm which watcher was stopped.

## Subcommand: status

1. Use `TaskList` to report whether a `work-queue monitor` is currently running (and its
   description / queue root).
2. Read `<QUEUE>` and count `- [ ]` (pending), `- [-]` (in-progress), `- [x]` (done), `- [~]`
   (rejected). Report the pending count so the user knows what the watcher would pick up.

## Don't

- Don't poll the queue yourself in a loop — that's the Monitor's job. React only to its
  notifications.
- Don't start more than one watcher per project.
- Don't trigger on the in-progress (`- [-]`) marker — only newly-added pending (`- [ ]`) work
  should wake you, or you'll re-process tasks the worker is already handling.
