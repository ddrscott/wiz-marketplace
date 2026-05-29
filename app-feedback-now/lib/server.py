"""
Sidecar HTTP server for the app-feedback-now skill.

Unlike the static `make-pages-interactive` server (which serves a directory of
HTML), this server hosts NO application content. It exists only to:

  - GET  /                   render the bookmarklet landing page (drag-to-bar)
  - GET  /lib/feedback.js    deliver the in-page library to a cross-origin app
  - GET  /lib/feedback.css   ditto, styles
  - GET  /info               diagnostic JSON ({slug, port, storage, started_at})
  - GET  /history            current contents of history.json (cross-origin OK)
  - POST /feedback           append a comment batch to inbox.jsonl

All responses set `Access-Control-Allow-Origin: *` so the dev app (running on
some other localhost port, or even a remote URL) can talk to us without CORS
pain.

Storage is slug-keyed under ~/.claude/feedback/<slug>/:

    ~/.claude/feedback/<slug>/
        inbox.jsonl     # append-only stream of comment batches (Monitor target)
        history.json    # array of batches Claude has processed (page polls this)
        meta.json       # {slug, port, started_at, cwd}

The slug is chosen by the launcher (the /app-feedback-now slash command via
scripts/slug.py) and passed to this server with --slug. Re-runs in the same
project find the same inbox by re-deriving the same slug.

Stdlib only — no pip install required, just `python lib/server.py`.

Usage:
    python lib/server.py --slug <slug> [--port 5050] [--idle-timeout 600]
"""
import argparse
import http.server
import json
import mimetypes
import os
import socketserver
import subprocess
import sys
import threading
import time
from html import escape as html_escape
from pathlib import Path
from urllib.parse import urlparse

# Where this file lives — used to serve /lib/* and to read the bookmarklet
# landing template (lib/index.html).
LIB_DIR = Path(__file__).resolve().parent

# Only these names may be fetched via /lib/<name>. Hardcoded so we never
# accidentally serve server.py itself, or future config files that land in
# lib/. Index.html is rendered via GET / (not /lib/index.html) and so isn't
# in this list.
PUBLIC_LIB_FILES = frozenset({"feedback.js", "feedback.css"})

# Slug-keyed storage root. We deliberately keep app feedback OUT of the app's
# own source tree — these are dev-time artifacts, not project content.
STORAGE_ROOT = Path(os.environ.get("APP_FEEDBACK_HOME") or
                    (Path.home() / ".claude" / "feedback"))

# ---------- Auto-shutdown bookkeeping ----------
# Same dual watchdog as the static skill: parent-death + idle timeout. Without
# this, sidecars launched as Claude Code background tasks would outlive the
# session (orphaned to launchd/init) and pile up across days of use.
INITIAL_PPID = os.getppid()
_activity_lock = threading.Lock()
_last_activity = time.monotonic()


def _touch_activity():
    global _last_activity
    with _activity_lock:
        _last_activity = time.monotonic()


def _idle_seconds():
    with _activity_lock:
        return time.monotonic() - _last_activity


def _with_charset(content_type: str) -> str:
    """Append `; charset=utf-8` to text-ish content types when missing. Without
    this, browsers fall back to Latin-1 and emojis / non-ASCII glyphs garble."""
    if not content_type:
        return content_type
    needs = (
        content_type.startswith("text/")
        or content_type in ("application/javascript", "application/json", "application/xml")
    )
    if needs and "charset=" not in content_type.lower():
        return f"{content_type}; charset=utf-8"
    return content_type


# ---------- Monitor detection ----------
# The in-page library shows a "no agent picked this up yet" warning if it
# doesn't see a history.json update within ~3 minutes. That warning is wrong
# when an agent IS actively working (just slowly). lsof on the inbox file
# tells us reliably whether any external process has it open for reading
# (the Claude Code Monitor's tail -F, typically). Cached for a few seconds to
# avoid spawning lsof on every 4 s history poll.
_LSOF_TTL_S = 3.0
_lsof_lock = threading.Lock()
# None = never populated. We can't use 0.0 as a sentinel because
# `time.monotonic()` returns small values right after process start, which
# would pass the freshness check and return the initial cache value (None)
# for the first 3 s — that produced "unknown" responses to every history poll
# until 3 s after launch.
_lsof_cache_at: "float | None" = None
_lsof_cache_value: "bool | None" = None


def _is_inbox_monitored(inbox_path: Path) -> "bool | None":
    """True if some other process has the inbox open, False if not, None if
    lsof isn't available (Windows, restricted env). Filters out our own PID."""
    global _lsof_cache_at, _lsof_cache_value
    now = time.monotonic()
    with _lsof_lock:
        if _lsof_cache_at is not None and now - _lsof_cache_at < _LSOF_TTL_S:
            return _lsof_cache_value
    try:
        proc = subprocess.run(
            ["lsof", "-t", str(inbox_path)],
            capture_output=True, text=True, timeout=2,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        with _lsof_lock:
            _lsof_cache_at = now
            _lsof_cache_value = None
        return None
    # lsof exits 0 if any pid matches, 1 if none. Both are normal.
    pids = {p for p in proc.stdout.split() if p.strip().isdigit()}
    pids.discard(str(os.getpid()))
    monitored = bool(pids)
    with _lsof_lock:
        _lsof_cache_at = now
        _lsof_cache_value = monitored
    return monitored


def _slug_dir(slug: str) -> Path:
    return STORAGE_ROOT / slug


def _ensure_slug_storage(slug: str, port: int) -> Path:
    d = _slug_dir(slug)
    d.mkdir(parents=True, exist_ok=True)
    inbox = d / "inbox.jsonl"
    if not inbox.exists():
        inbox.touch()
    history = d / "history.json"
    if not history.exists():
        history.write_text("[]")
    meta = d / "meta.json"
    meta.write_text(json.dumps({
        "slug": slug,
        "port": port,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "cwd": os.getcwd(),
        "lib_dir": str(LIB_DIR),
    }, indent=2))
    return d


class FeedbackHandler(http.server.BaseHTTPRequestHandler):
    slug: str = "default"
    storage_dir: Path = None  # type: ignore
    started_at: str = ""

    # ---------- CORS / cache headers on every response ----------
    def end_headers(self):
        # Any response is proof of a live client — push idle deadline back.
        _touch_activity()
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        # CORS: dev app lives on a DIFFERENT origin (e.g. http://localhost:8787)
        # and needs to fetch / POST to us at http://localhost:5050. The wildcard
        # is fine because everything we serve is non-secret and localhost-only.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/" or path == "":
            self._serve_landing()
            return
        if path == "/info":
            self._json(200, {
                "skill": "app-feedback-now",
                "slug": self.slug,
                "storage_dir": str(self.storage_dir),
                "lib_dir": str(LIB_DIR),
                "port": self.server.server_address[1],  # type: ignore[index]
                "started_at": self.started_at,
            })
            return
        if path == "/history":
            self._serve_history()
            return
        if path.startswith("/lib/"):
            self._serve_from_lib(path[len("/lib/"):])
            return
        self.send_error(404, "unknown path")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/feedback":
            self._accept_feedback()
            return
        self._json(404, {"ok": False, "error": "unknown endpoint"})

    # ---------- handlers ----------
    def _serve_landing(self):
        tmpl_path = LIB_DIR / "index.html"
        if not tmpl_path.exists():
            self.send_error(500, "index.html template missing")
            return
        template = tmpl_path.read_text(encoding="utf-8")
        port = self.server.server_address[1]  # type: ignore[index]
        endpoint = f"http://localhost:{port}"
        # The bookmarklet must be a single javascript: URL that loads the
        # library and tags the loader <script> with the slug + endpoint. Built
        # here so the rendered page always matches the running sidecar.
        #
        # CRITICAL: wrap in void(...) so the IIFE's return value is discarded.
        # Without void(), the IIFE's last expression (`appendChild(l)` →
        # returns the <link> element) becomes the bookmarklet's return value;
        # browsers respond by NAVIGATING to a new document containing the
        # stringified return ("[object HTMLLinkElement]"), which replaces the
        # page and breaks Cmd-R. Classic bookmarklet pitfall.
        bookmarklet = (
            "javascript:void((function(){"
            "if(window.__claudeFeedbackInit){alert('app-feedback-now is already running on this page.');return;}"
            "var s=document.createElement('script');"
            f"s.src='{endpoint}/lib/feedback.js';"
            f"s.dataset.cfEndpoint='{endpoint}';"
            f"s.dataset.cfSlug='{self.slug}';"
            "document.head.appendChild(s);"
            "var l=document.createElement('link');"
            "l.rel='stylesheet';"
            f"l.href='{endpoint}/lib/feedback.css';"
            "document.head.appendChild(l);"
            "})());"
        )
        rendered = (template
                    .replace("{{SLUG}}", html_escape(self.slug))
                    .replace("{{PORT}}", str(port))
                    .replace("{{ENDPOINT}}", html_escape(endpoint))
                    .replace("{{STORAGE_DIR}}", html_escape(str(self.storage_dir)))
                    .replace("{{STARTED_AT}}", html_escape(self.started_at))
                    .replace("{{BOOKMARKLET_HREF}}", html_escape(bookmarklet, quote=True)))
        body = rendered.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_history(self):
        history_path = self.storage_dir / "history.json"
        if not history_path.exists():
            body = b"[]"
        else:
            body = history_path.read_bytes() or b"[]"
        inbox_path = self.storage_dir / "inbox.jsonl"
        monitored = _is_inbox_monitored(inbox_path)
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # Headers the in-page library reads on each poll so it can show an
        # accurate "Claude is processing" vs "no agent watching" state.
        if monitored is True:
            self.send_header("X-Inbox-Monitored", "true")
        elif monitored is False:
            self.send_header("X-Inbox-Monitored", "false")
        else:
            self.send_header("X-Inbox-Monitored", "unknown")
        self.send_header("X-Storage-Dir", str(self.storage_dir))
        self.send_header("X-Slug", self.slug)
        self.send_header("Access-Control-Expose-Headers",
                         "X-Inbox-Monitored, X-Storage-Dir, X-Slug")
        self.end_headers()
        self.wfile.write(body)

    def _serve_from_lib(self, rel: str):
        # Whitelist + path-traversal guard. The whitelist is the real defence;
        # the resolve() check is a belt-and-braces in case the whitelist ever
        # grows to include subpaths.
        if rel not in PUBLIC_LIB_FILES:
            self.send_error(404)
            return
        try:
            target = (LIB_DIR / rel).resolve()
        except Exception:
            self.send_error(404); return
        if not str(target).startswith(str(LIB_DIR) + os.sep) and target != LIB_DIR:
            self.send_error(403, "forbidden"); return
        if not target.exists() or not target.is_file():
            self.send_error(404); return
        mime, _ = mimetypes.guess_type(str(target))
        if mime is None:
            mime = "application/octet-stream"
        mime = _with_charset(mime)
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _accept_feedback(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8") if length else ""
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._json(400, {"ok": False, "error": "invalid json"})
            return
        data["received_at"] = time.time()
        data["received_iso"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        # Reaffirm the slug so a misconfigured client can't poison another
        # slug's inbox by including a different `slug` in the body.
        data["slug"] = self.slug
        inbox = self.storage_dir / "inbox.jsonl"
        with open(inbox, "a") as f:
            f.write(json.dumps(data) + "\n")
        n = len(data.get("comments", []))
        page = (data.get("page") or {}).get("href", "?")
        sys.stdout.write(f"[feedback] {n} comment(s) on {page} -> {inbox}\n")
        sys.stdout.flush()
        self._json(200, {"ok": True})

    def _json(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # Silence default request logging — only log POSTs and errors. The page's
    # 4s history poll would otherwise drown the terminal.
    #
    # NOTE: args[0] is a str for normal request logs ("GET /foo HTTP/1.0") but
    # an int for send_error() ("code %d, message %s" → (404, "Not Found")).
    # The upstream make-pages-interactive server has this same bug latent
    # because it only ever calls send_error() through inherited paths that
    # also bypass log_message — but our explicit /lib whitelist hits it.
    # Coerce to str defensively.
    def log_message(self, format, *args):
        if not args:
            return
        joined = " ".join(map(str, args))
        first = str(args[0])
        if first.startswith("POST") or " 4" in joined or " 5" in joined:
            sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))


def _watchdog(idle_timeout_s: int):
    """Daemon: exit when (a) parent process dies (we'd be reparented to PID 1)
    or (b) no client requests for idle_timeout_s. os._exit because srv.shutdown
    can hang on per-request thread join — for a dev sidecar that's no upside."""
    watch_parent = (INITIAL_PPID != 1)
    while True:
        time.sleep(5)
        reason = None
        if watch_parent and os.getppid() == 1:
            reason = "parent process exited"
        elif idle_timeout_s > 0 and _idle_seconds() > idle_timeout_s:
            reason = f"idle for >{idle_timeout_s}s with no clients"
        if reason:
            sys.stdout.write(f"[server] {reason}; shutting down\n")
            sys.stdout.flush()
            os._exit(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True,
                    help="project slug — keys storage at ~/.claude/feedback/<slug>/")
    ap.add_argument("--port", type=int, default=5050)
    ap.add_argument("--idle-timeout", type=int, default=600,
                    help="exit if no client requests for this many seconds (0 = disable). Default 600.")
    args = ap.parse_args()

    storage = _ensure_slug_storage(args.slug, args.port)
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S")

    FeedbackHandler.slug = args.slug
    FeedbackHandler.storage_dir = storage
    FeedbackHandler.started_at = started_at

    class ReuseTCP(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    try:
        srv = ReuseTCP(("", args.port), FeedbackHandler)
    except OSError as e:
        print(f"[server] FATAL: port {args.port} is unavailable ({e}).")
        print(f"[server]  - check what's running there:  curl -s http://localhost:{args.port}/info")
        print(f"[server]  - or kill it:                  lsof -ti:{args.port} | xargs kill")
        print(f"[server]  - or run me on a different port: --port {args.port + 1}")
        sys.exit(1)

    threading.Thread(target=_watchdog, args=(args.idle_timeout,), daemon=True).start()

    with srv:
        print(f"[server] app-feedback-now sidecar")
        print(f"[server] slug:     {args.slug}")
        print(f"[server] storage:  {storage}")
        print(f"[server] landing:  http://localhost:{args.port}/")
        print(f"[server] inbox:    {storage / 'inbox.jsonl'}")
        print(f"[server] history:  {storage / 'history.json'}")
        if args.idle_timeout > 0:
            print(f"[server] auto-shutdown: parent-death OR {args.idle_timeout}s idle. --idle-timeout 0 to disable")
        else:
            print(f"[server] auto-shutdown: parent-death only")
        print(f"[server] Ctrl-C to stop")
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\n[server] stopping")


if __name__ == "__main__":
    main()
