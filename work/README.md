# work

A persistent **FIFO work queue** that lives inside each project. Capture tasks as you think of
them, then let isolated worker agents drain the queue one at a time — each task gets a clean
context and a single, traceable commit.

## Install

```
/plugin marketplace add ddrscott/wiz-marketplace
/plugin install work@wiz-marketplace
```

## Commands

| Command | What it does |
|---------|--------------|
| `/work:add <idea>` | Add a task. Asks 1–2 clarifying questions, then appends a `- [ ]` item (and a detail file for complex tasks). |
| `/work:list` | Show the queue with pending / in-progress / done / rejected counts. |
| `/work:next` | Process the next pending task with an isolated worker agent, then auto-continue until the queue is empty. |
| `/work:monitor [start\|stop\|status]` | Watch the queue and **auto-run `/work:next`** whenever pending tasks appear. |

## Where the queue lives

Resolved at the project root:

- `docs/` exists → `docs/work/queue.md`
- otherwise → `work/queue.md`

```markdown
# Work Queue

- [ ] Pending task
- [-] In-progress task
- [x] Completed task
- [~] ~~Rejected task~~ (reason)
```

Complex tasks get a sibling detail file (`<queue-root>/<slug>.md`) with problem, acceptance
criteria, relevant files, and constraints — enough that a worker can execute later with no
further questions.

## How processing works

`/work:next` launches the **`work-queue-worker`** subagent for one task at a time. Each worker:

1. **Claims** the first `- [ ]` item — flips it to `- [-]` and commits immediately (prevents
   double-processing, makes progress visible).
2. **Loads context** from the detail file, `README.md`, and `CLAUDE.md`.
3. **Validates** the task is still relevant and not a duplicate (rejects with a reason if not).
4. **Plans**, then **executes** the minimal change.
5. **Completes** — flips `- [-]` → `- [x]` and commits the work *and* the queue update together.

The orchestrator re-reads the queue after each task (catching anything added mid-run) and only
stops once no `- [ ]` items remain.

## Hands-off mode: `/work:monitor`

`/work:monitor start` arms a background watcher (Claude Code's `Monitor`) on the queue file. It's
**edge-triggered** — it wakes the agent only when the pending count *increases*, so adding a task
from any session kicks off a `/work:next` drain automatically, while a draining queue never
re-triggers itself.

```
/work:monitor start          # arm the watcher (default 3s poll)
/work:monitor start --interval 5
/work:monitor status         # is it running? how many pending?
/work:monitor stop           # disarm
```

Typical loop: arm the monitor once, then just keep running `/work:add` as ideas land — the queue
drains itself in the background.

## Structure

```
work/
├── plugin.json
├── README.md
├── commands/
│   ├── add.md          # /work:add
│   ├── list.md         # /work:list
│   ├── next.md         # /work:next  (orchestrator)
│   └── monitor.md      # /work:monitor
├── agents/
│   └── work-queue-worker.md   # isolated single-task executor
└── skills/
    └── work-queue/
        └── SKILL.md    # queue format & conventions
```

## License

MIT
