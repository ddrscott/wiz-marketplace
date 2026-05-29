# app-feedback-now

A Claude Code skill that turns any **live web app** into a commenting surface, without modifying the app's source.

> **Built on top of [`make-pages-interactive`](https://github.com/paraschopra/make-pages-interactive) by Paras Chopra.** That skill pioneered the "highlight → comment → agent edits → page reloads with walkthrough" UX for static HTML reports. `app-feedback-now` is a fork that keeps the same UX but flips the architecture to fit *live dev servers* (wrangler / vite / astro / parcel) where the original's approach — rewriting `*.html` files in place and serving them from its own port — doesn't work. Same MIT license, both copyrights preserved. Real credit for the in-page library and the round-trip design belongs to Paras.

---

## What's different from `make-pages-interactive`

| | `make-pages-interactive` | `app-feedback-now` |
|---|---|---|
| Target | Folder of static `*.html` | Live dev server (wrangler/vite/astro/parcel/etc.) |
| Library delivery | `inject.py` modifies HTML files | Bookmarklet loads at runtime — zero source changes |
| Where pages are served | The skill's own server | Your existing dev server |
| Where comments POST to | Same origin | Cross-origin (CORS-enabled sidecar) |
| Storage location | `<artifact>/feedback/` next to HTML | `~/.claude/feedback/<slug>/` outside the repo |
| Slug | (not needed) | Auto-derived from git remote / `pwd` basename |
| What Claude edits | Rendered HTML files | Source files (`.astro`, `.jsx`, route handlers) |
| Stale-warning logic | 90 s timer, no detection | `lsof`-based monitor detection (no false alarms) + 180 s timer as fallback |

If you're working with static HTML reports → use the original. If you're working with a real app that has its own dev server → use this one.

---

## How it works

```
┌─────────────────┐      ┌──────────────────────────┐
│ wrangler dev    │ 8787 │ your dev app, untouched  │
└─────────────────┘      └──────────────────────────┘
        │
        │  open page, click bookmarklet
        ▼
┌─────────────────┐    CORS POST     ┌──────────────────────────┐
│  feedback.js    │ ───────────────▶ │ app-feedback-now sidecar │
│  (in your page) │ ◀─── polls ──── │ port 5050 (default)      │
└─────────────────┘   /history       │ CORS *  ·  CSP-free dev  │
                                     └────────────┬─────────────┘
                                                  │ append
                                     ┌────────────▼──────────────┐
                                     │ ~/.claude/feedback/<slug> │
                                     │   inbox.jsonl             │
                                     │   history.json            │
                                     └────────────┬──────────────┘
                                                  │ Monitor (tail -F)
                                     ┌────────────▼──────────────┐
                                     │ Claude (the agent)        │
                                     │ edits SOURCE files in the │
                                     │ repo (jsx/astro/handlers) │
                                     └───────────────────────────┘
```

Three real pieces:

| File | Role |
|---|---|
| `lib/feedback.js` | In-page library injected by the bookmarklet. Text + element + general comments, batched submit, history polling, walkthrough tour. Forked from `make-pages-interactive` with cross-origin endpoint resolution, richer ancestor context (for source mapping), and an expanded element-mode whitelist (buttons, links, form fields, semantic regions). |
| `lib/server.py` | Stdlib-only sidecar. CORS `*`. Serves `/lib/{feedback.js,feedback.css}`, `/`, `/info`, `/history` (GET) and `/feedback` (POST). Slug-keyed storage at `~/.claude/feedback/<slug>/`. `lsof`-based monitor detection. Auto-shuts-down on parent-death or 10 min idle. |
| `lib/index.html` | Landing page rendered at `/`. Drag-to-bookmark-bar bookmarklet with the port + slug + endpoint templated in at request time, wrapped in `void(...)` so it doesn't navigate the page. |

Plus glue:

| File | Role |
|---|---|
| `skills/app-feedback-now.md` | What Claude reads to know when and how to invoke the skill. |
| `commands/app-feedback-now.md` | `/app-feedback-now [start\|stop\|status\|list]` slash command. |
| `scripts/slug.py` | Derives a project slug from `git remote` → `pwd` basename. |

---

## Install

The recommended path is via the Wiz Marketplace:

```
/plugin marketplace add ddrscott/wiz-marketplace
/plugin install app-feedback-now@wiz-marketplace
```

Or clone directly for development:

```bash
git clone https://github.com/ddrscott/app-feedback-now \
  ~/.claude/skills/app-feedback-now
```

Claude Code auto-discovers any folder under `~/.claude/skills/` containing a `SKILL.md`.

---

## Usage

Inside a Claude Code session in your app's directory:

```
/app-feedback-now
```

(or natural language: "make this app interactive")

Claude will:

1. Derive a slug from your git remote (or `pwd` basename).
2. Pick a free port (5050, falls back to 5051+).
3. Start the sidecar in the background.
4. Print the landing URL.
5. Start a Monitor on the inbox so any comment you leave gets picked up immediately.

Then:

1. Open the landing URL (e.g. <http://localhost:5050/>).
2. Drag the orange `app-feedback-now` button to your bookmark bar.
3. Open your dev app in another tab (e.g. <http://localhost:8787/>).
4. Click the bookmark. A floating `feedback` button appears bottom-right.
5. Comment away.

---

## Slash command

| Subcommand | What it does |
|---|---|
| `/app-feedback-now` or `/app-feedback-now start` | Pick a slug + port, start sidecar in background, start Monitor on inbox. |
| `/app-feedback-now stop` | Find the sidecar (default port 5050, walks up) and kill it. Usually not needed — sidecar self-shuts-down. |
| `/app-feedback-now status` | Sidecar info + unprocessed-comment count. |
| `/app-feedback-now list` | Scan ports 5050–5059 for running sidecars across projects. |

Flags: `--port N`, `--slug NAME`.

---

## How the sidecar shuts down

Same three-way teardown as the static skill:

1. **Parent-process death** *(automatic, ~5–10 s)*. The sidecar records its parent PID at startup and polls every 5 s. When the parent dies (close the Claude Code window), the kernel reparents the sidecar to PID 1 — the watchdog notices and calls `os._exit(0)`. Skipped when started detached.
2. **Idle timeout** *(automatic, default 10 min)*. The page polls `/history` every ~4 s, so any open browser tab keeps the sidecar alive. When no client requests have arrived for `--idle-timeout` seconds, it exits.
3. **Manual**: `/app-feedback-now stop`, or `lsof -ti:5050 | xargs kill`, or Ctrl-C the foreground log.

You generally don't need to think about this.

---

## Status accuracy via lsof

The page's "Claude is processing…" banner only flips to a stale warning ("no agent picked this up") when the inbox file is **not** being held open by any process. The sidecar runs `lsof -t <inbox.jsonl>` (cached for 3 s, own-PID filtered) and reports the result on every `/history` response via the `X-Inbox-Monitored: true|false|unknown` header. When the Claude Code Monitor's `tail -F` is alive, the page knows — and never falsely warns you that no agent is watching.

If `lsof` isn't available (some restricted environments), the page falls back to a pure 180 s timer for the same warning.

---

## Storage

Each project gets its own slug-keyed directory:

```
~/.claude/feedback/
├── bulletin-mail/
│   ├── inbox.jsonl        # append-only stream of comment batches
│   ├── history.json       # batches Claude has processed
│   └── meta.json          # {slug, port, started_at, cwd}
├── justright.fm/
│   ├── inbox.jsonl
│   ├── history.json
│   └── meta.json
└── ...
```

Override the root with `APP_FEEDBACK_HOME=...`. Wipe a slug's history by deleting its directory.

---

## What gets sent in a comment batch

```jsonc
{
  "slug": "bulletin-mail",
  "submitted_at": "2026-05-27T18:30:00.000Z",
  "page": {
    "href": "http://localhost:8787/admin/lists",
    "host": "localhost:8787",
    "pathname": "/admin/lists",
    "search": "",
    "hash": "",
    "title": "Lists · BulletinMail Admin"
  },
  "comments": [
    {
      "id": "c-1738012345-abc1",
      "type": "elements",            // selection | elements | general
      "comment": "this column is too narrow",
      "quote": "Subscribers",
      "anchor": {
        "selector": "[data-cf-id=\"el-42\"]",
        "tag": "th",
        "classes": ["px-3", "py-2", "text-zinc-600"],
        "text_snippet": "Subscribers",
        "outer_html": "<th class=\"px-3 py-2 text-zinc-600\">Subscribers</th>",
        "ancestors": [
          {"tag": "tr", "classes": ["bg-zinc-50"]},
          {"tag": "thead", "classes": []},
          {"tag": "table", "id": "lists-table", "classes": ["w-full"]}
        ]
      }
    }
  ]
}
```

Claude uses `page.pathname` to find the route handler, then `anchor.text_snippet` + `ancestors` to grep for the right source file.

---

## Repo layout

```
app-feedback-now/
├── plugin.json
├── README.md
├── LICENSE
├── lib/
│   ├── feedback.js
│   ├── feedback.css
│   ├── server.py
│   └── index.html
├── commands/
│   └── app-feedback-now.md
├── skills/
│   └── app-feedback-now.md
└── scripts/
    └── slug.py
```

---

## Credits

- **Original work**: [Paras Chopra](https://github.com/paraschopra) — [`make-pages-interactive`](https://github.com/paraschopra/make-pages-interactive). The client library, the round-trip protocol, the auto-shutdown watchdog, the walkthrough mechanic — all his design. This fork inherits all of it.
- **This fork**: Scott Pierce — adapted for live dev servers, added bookmarklet delivery, slug-keyed cross-project storage, cross-origin support, and `lsof`-based monitor detection.

If you're using static HTML, please use the original. If you want to send improvements back upstream where it makes sense, please do — Paras's design deserves the credit.

---

## License

MIT. See [LICENSE](LICENSE). Copyright preserved for both the original work (Paras Chopra) and this fork (Scott Pierce).
