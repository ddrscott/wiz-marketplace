---
name: app-feedback-now
description: Run a localhost sidecar that lets you leave inline comments on a LIVE web app (wrangler dev, Astro dev, anything) without touching the app's source. A bookmarklet drops the feedback library onto any page; comments POST to the sidecar, land in a JSONL inbox the agent monitors, and trigger source-file edits with a walkthrough on reload. Trigger phrases — "make this app interactive", "add feedback to this app", "/app-feedback-now". Sister skill to make-pages-interactive (static HTML) — use this one for SSR / SPA / wrangler-dev / multi-port dev setups.
---

# app-feedback-now

Fork of [`make-pages-interactive`](https://github.com/paraschopra/make-pages-interactive) adapted for live dev servers. That skill mutates static HTML files in place and serves them from its own server — fine for a directory of standalone reports, but wrong for a complex web app where pages come from JSX/Astro/server-rendered handlers and a dev server already owns the port.

This skill flips the model. The app source is **never modified**. A small **sidecar server** (default port 5050) hosts the feedback library and a JSONL inbox; a **bookmarklet** loads the library into any page at runtime. Comments POST cross-origin to the sidecar (CORS `*`). The agent monitors the inbox and edits the **source files** of the app (Astro pages, JSX components, Hono handlers), then HMR or a manual reload picks up the change and the page surfaces a walkthrough — same UX as the static skill.

## When to invoke

User says any of:
- `/app-feedback-now` or `/app-feedback-now start` → **Start flow**
- `/app-feedback-now stop` → **Stop flow**
- `/app-feedback-now status` → **Status flow**
- `/app-feedback-now list` → **List flow** (scan ports for running sidecars)
- "make this app interactive" / "add feedback to this app" / "let me comment on my app" → **Start flow**
- "stop app-feedback-now" / "kill the feedback sidecar" → **Stop flow**

If they say "make this PAGE interactive" or point at a directory of static HTML, that's the **static** skill (`make-pages-interactive`), not this one. Quick test: does the user have a running dev server (wrangler/vite/astro/parcel/next)? Then this skill. A folder of `.html` files? Then the static skill.

## Start flow

1. **Derive a slug** from `pwd`:
   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/slug.py
   ```
   Prefers git remote basename, falls back to `pwd` basename. E.g. inside `~/code/bulletin-mail` → `bulletin-mail`.
2. **Pick a port** (default 5050). Before starting, check what's there:
   ```
   curl -s --max-time 2 http://localhost:5050/info
   ```
   - JSON with `skill: app-feedback-now` and matching `slug` → reuse it, skip to step 4.
   - JSON with a different slug or a different skill → port is held by something else. Try 5051, 5052, … (tell the user which port you chose).
   - No response → port is free.
3. **Start the sidecar in the background** via Bash with `run_in_background: true`:
   ```
   python ${CLAUDE_PLUGIN_ROOT}/lib/server.py --slug <slug> --port <port>
   ```
   Auto-shuts-down on parent death or 10 min idle, so no manual cleanup needed.
4. **Tell the user to open the landing page** to install the bookmarklet:
   ```
   http://localhost:<port>/
   ```
   Mention they need to drag the orange `app-feedback-now` button to their bookmark bar, then open their dev app in another tab and click the bookmark. (One-time per session — re-clicking on each page is fine but unnecessary; the library survives in-page navigation in SPAs.)
5. **Start a Monitor on the inbox** so new comments notify you immediately:
   ```
   Monitor on path: ~/.claude/feedback/<slug>/inbox.jsonl
   ```
   Do NOT poll the file. Let the Monitor notification arrive.

## Responding to a feedback batch

When a new batch arrives in `~/.claude/feedback/<slug>/inbox.jsonl`:

### Step 1 — read the batch

Each entry looks like this (annotated; **field names matter, see Step 4**):

```jsonc
{
  "slug": "askscottpierce.com",
  "submitted_at": "2026-05-28T22:46:22.939Z",
  "page": {                                    // route the user was on
    "href":     "http://localhost:4321/",
    "host":     "localhost:4321",
    "pathname": "/",                           // ← use this to find the source file
    "search":   "",
    "hash":     "",
    "title":    "AI Investment Reviews | …"
  },
  "comments": [
    {
      "id":         "c-1780008327188-im4x",    // ← the COMMENT id (you echo this back)
      "type":       "elements",                // selection | elements | general
      "comment":    "make this more succinct", // the user's text
      "created_at": "2026-05-28T22:45:27.188Z",

      // For type=elements: array of selected DOM nodes.
      "elements": [
        {
          "cf_id":        "el-5",              // ← DOM anchor id, NOT the comment id
          "selector":     "[data-cf-id=\"el-5\"]",
          "tag":          "p",
          "id":           null,
          "classes":      ["fade-in-up", "font-serif", "text-lg", "…"],
          "text_snippet": "An independent, technical, skeptical pass over your AI plan …",
          "outer_html":   "<p class=\"…\" data-cf-id=\"el-5\">…</p>",
          "ancestors":    [{"tag": "div", "classes": ["max-w-3xl", "mx-auto", "…"]},
                           {"tag": "section", "classes": ["min-h-screen", "…"]}]
        }
      ]

      // For type=selection: single `anchor` field shaped like one elements[] entry,
      //                     plus `quote` (the highlighted text).
      // For type=general:   no anchor — comment is page-level, not region-anchored.
    }
  ]
}
```

> **CRITICAL — two different ids, do not confuse them:**
> - **`id` on a comment** (e.g. `c-1780008327188-im4x`) → the stable COMMENT id. This is what `in_response_to` must reference in Step 4.
> - **`cf_id` on an element** (e.g. `el-5`) → the DOM-element anchor id. Useful only for re-finding the element in the live page. **Never** put `cf_id` values in `in_response_to`.

### Step 2 — map the comment to the source file

The rendered DOM is not the file you'll edit. Use these signals in order:
- `page.pathname` → the route. Find the handler / page / component for that route. Examples:
  - Astro: `src/pages/<route>.astro` or `src/pages/<route>/index.astro`
  - Hono: a route in `src/index.ts` or wherever the app exports JSX
  - Cloudflare Worker + assets: a server-rendered handler in `src/worker/routes/` or static asset in `dist/`
- `anchor.outer_html` + `ancestors[].classes` → grep the source for distinctive class names or text. Tailwind utility classes are noisy; prefer component-specific classes or visible text strings.
- `anchor.text_snippet` → grep verbatim. Often the fastest path.
- If still ambiguous, ask the user which file owns the route.

### Step 3 — edit the source and add an anchor

Wrap the changed region with `<span data-cf-change="ch-<short-slug>">…</span>`, or add `data-cf-change="ch-<short-slug>"` as an attribute on an existing wrapping element. One anchor per change. The anchor lives in the SOURCE FILE (JSX / `.astro` / handler), which is what gets rendered into the DOM. After HMR / reload, verify the rendered HTML contains `data-cf-change="ch-<slug>"` — if it doesn't, the walkthrough breaks too, not just the banner.

### Step 4 — append a batch to history.json

`~/.claude/feedback/<slug>/history.json` — newest = LAST. Append, do not prepend.

```jsonc
{
  "batch_id":  "b-<short-slug>",
  "timestamp": "2026-05-28T22:47:00.000Z",
  "page_url":  "/",                         // pathname from the inbox entry
  "comments": [
    // Echo enough of the original comment that the walkthrough sidebar can
    // display it. The MUST-HAVE fields are `id` and `comment`. Anything else
    // is just for the audit trail.
    {
      "id":      "c-1780008327188-im4x",    // ← MUST be the COMMENT's `id`, not its cf_id
      "comment": "make this more succinct"
    }
  ],
  "changes": [
    {
      "id":              "ch-hero-subhead",
      "in_response_to":  ["c-1780008327188-im4x"],  // ← list of COMMENT ids (the `c-…` form)
      "anchor":          "ch-hero-subhead",         // ← must match a `data-cf-change` in the rendered DOM
      "title":           "Tightened the hero subheadline",
      "description":     "Cut the four-sentence subhead down to two. …"
    }
  ]
}
```

**Why `in_response_to` matters:** the in-page library shows "Claude is processing…" until at least one `change.in_response_to` references a comment id from the most recently submitted batch. If you put `cf_id` (`el-5`) there instead of the comment `id` (`c-1780…`), the banner stays stuck forever even though your edit landed correctly. This is the #1 way to break the UX — be precise.

### Step 5 — let the page take over

The page polls `/history` every ~4 s. New batch detected → 🔔 banner + tab-title bell → user clicks reload (or HMR reloads automatically) → walkthrough opens, highlighting each `data-cf-change` anchor in sequence. You don't need to do anything else.

## Status / List flow

- `status`: `curl http://localhost:<port>/info` to confirm the slug, then `wc -l ~/.claude/feedback/<slug>/inbox.jsonl` and inspect history to summarize unprocessed comments.
- `list`: scan ports 5050–5059 with `curl /info` (parallel Bash calls); report any `skill: app-feedback-now` instances and their slugs.

## Stop flow

1. Identify the port (from this session, or `curl /info` against 5050+).
2. `lsof -ti:<port> | xargs kill` (the watchdog's `os._exit` makes graceful shutdown reliable).
3. Confirm: `lsof -i :<port>` should be silent.

In most cases the user doesn't need to manually stop — the sidecar self-shuts-down within 5–10 s of Claude Code exiting or after 10 min of no client traffic.

## Re-entering a directory that already has feedback

If `~/.claude/feedback/<slug>/inbox.jsonl` and `history.json` exist and this skill has been invoked in this session:
1. Diff inbox comment ids against history `changes[*].in_response_to`. Unprocessed = in inbox but not yet referenced.
2. If unprocessed exist, tell the user the count and ask whether to process now.
3. Either way, set up the Monitor on the inbox.

## Files in this plugin

```
${CLAUDE_PLUGIN_ROOT}/
├── plugin.json
├── README.md
├── LICENSE
├── skills/
│   └── app-feedback-now.md     # this file (agent-facing)
├── commands/
│   └── app-feedback-now.md     # /app-feedback-now slash command
├── lib/
│   ├── feedback.js             # cross-origin client library
│   ├── feedback.css            # styles
│   ├── server.py               # stdlib-only CORS sidecar
│   └── index.html              # bookmarklet landing page
└── scripts/
    └── slug.py                 # derive slug from git remote / pwd
```

## Gotchas

- **Slug determines storage**, not the port. Two different slugs on the same port number across different sessions = different inboxes. The slug is the join key.
- **Source mapping is the hard part.** A `<td class="bg-zinc-50">` in a 200-component app could come from anywhere. Lean on `page.pathname` first, then visible-text grep, then ancestor class chain. Don't guess.
- **Anchor values must match a `data-cf-change` attribute actually present in the rendered DOM** (which means the attribute must be in the *source file* whose output renders to that element). Typos or wrong-source-file edits cause the post-reload "anchor still missing" warning the library surfaces.
- **CSP**: some dev configurations block cross-origin scripts. wrangler/vite/astro defaults don't, but if the bookmarklet fires and nothing happens, check the browser console — a CSP error there is the signal to relax the dev-only policy to allow `localhost:5050`.
- **Bookmarklet on SPA navigations**: the `__claudeFeedbackInit` guard prevents double-init within a single document. A *full* navigation (hard nav, not pushState) tears the library down; the bookmarklet must be re-clicked. This is rare in practice for SPAs.
