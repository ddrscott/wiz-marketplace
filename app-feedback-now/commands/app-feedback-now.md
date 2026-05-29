---
description: Start, stop, or inspect the app-feedback-now sidecar — leaves inline comments on a live web app (wrangler dev / vite / astro) without modifying its source.
argument-hint: "[start|stop|status|list] [--port N] [--slug NAME]"
---

# /app-feedback-now

Args: `$ARGUMENTS`

You are running the `/app-feedback-now` slash command. Subcommands:

- `start` (default if no subcommand) — derive a slug, start the sidecar in the background, print the bookmarklet landing URL, start a Monitor on the inbox.
- `stop` — find the sidecar by port (default 5050, walk up if needed) and kill it.
- `status` — `curl /info`, summarize how many comments are unprocessed.
- `list` — scan ports 5050–5059 in parallel and report any `app-feedback-now` instances.

Read the plugin's `skills/app-feedback-now.md` (`${CLAUDE_PLUGIN_ROOT}/skills/app-feedback-now.md`) for the full flow protocol — especially "Responding to a feedback batch," which is how you handle inbox notifications after this command finishes.

## Routing

Parse `$ARGUMENTS`:
- Empty / starts with `--` → treat as `start` with those flags
- Starts with `start`, `stop`, `status`, or `list` → run that subcommand
- Anything else → run `start` and pass `$ARGUMENTS` as-is

Optional flags (only meaningful for `start`):
- `--port N` — override the default 5050
- `--slug NAME` — override the auto-derived slug (still gets normalized)

## Subcommand: start

1. **Resolve the slug.** Use the override if `--slug` was provided, else:
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/slug.py
   ```
   The slug derives from git remote basename → pwd basename. Tell the user which slug was chosen.

2. **Resolve the port.** Default 5050 unless `--port` was given. Probe:
   ```bash
   curl -s --max-time 2 http://localhost:<port>/info
   ```
   - JSON with `"skill": "app-feedback-now"` AND matching slug → already running, skip to step 4.
   - JSON with a different skill or slug → port is taken. Try 5051, 5052, … up to 5059. Tell the user which port you settled on.
   - No response → port is free, use it.

3. **Start the sidecar in the background.** Use Bash with `run_in_background: true`:
   ```
   python ${CLAUDE_PLUGIN_ROOT}/lib/server.py --slug <slug> --port <port>
   ```
   It self-shuts-down on parent death or 10 min of idle — no manual lifecycle work.

4. **Print clear next steps to the user**, exactly in this shape (replace the placeholders):

   > **app-feedback-now is running.**
   > Slug: `<slug>` · port: `<port>` · storage: `~/.claude/feedback/<slug>/`
   >
   > **Install the bookmarklet (one-time):** open <http://localhost:<port>/> and drag the orange `app-feedback-now` button onto your bookmark bar.
   >
   > **Use it:** open your dev app (e.g. `http://localhost:8787/`), click the bookmark, then highlight text or click `select element` to leave a comment. I'll handle it from there.

5. **Start a Monitor on the inbox** so new comments wake you immediately:
   ```
   Monitor:
     description: "app-feedback-now inbox (<slug>)"
     command: tail -n 0 -F ~/.claude/feedback/<slug>/inbox.jsonl
     persistent: true
   ```
   Each new line is one comment batch. When a notification fires, follow the "Responding to a feedback batch" section of the skill.

## Subcommand: stop

1. Determine the port. If the user passed `--port`, use that. Else `curl -s http://localhost:5050/info` and walk up 5051–5059 looking for any `"skill": "app-feedback-now"` response. If multiple, stop them all (or ask if the user wants to be specific).
2. Run `lsof -ti:<port> | xargs kill` for each. The server's SIGTERM handler exits cleanly; if a port is still bound after ~3 s, `kill -9`.
3. Confirm: `lsof -i :<port>` returns nothing. Report which slugs were stopped.

## Subcommand: status

1. Probe `/info` on 5050 (or `--port`). If no response, report "no sidecar running on port <N>" and stop.
2. Read `~/.claude/feedback/<slug>/inbox.jsonl` and `history.json`. Compute unprocessed = inbox comment ids minus union of history `changes[*].in_response_to`.
3. Print a tight summary:

   > **Sidecar:** running on port `<port>`, slug `<slug>`, started `<iso>`.
   > **Inbox:** `<n_inbox>` batch(es), `<n_unprocessed>` unprocessed comments.
   > **History:** `<n_batches>` batches, `<n_changes>` total changes.

## Subcommand: list

Scan ports 5050–5059 with parallel `curl -s --max-time 1 http://localhost:<port>/info` calls (issue them as a single Bash command using `&` and `wait`). For each that returns `"skill": "app-feedback-now"`, print one line:

```
<port>  <slug>   started <iso>   storage=<storage_dir>
```

If none, say so.

## Don't

- Don't modify the app's source code to "wire in" the library. The bookmarklet is the loader; that's the whole point.
- Don't create a `feedback/` directory in the project tree. Storage lives under `~/.claude/feedback/<slug>/`.
- Don't poll the inbox in a loop — use the Monitor. The watchdog in the server already handles auto-shutdown so the Monitor is the only thing the agent needs to do.
