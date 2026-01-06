#!/usr/bin/env python3
"""
Playwright browser executor with persistent browser process.

The browser runs as a separate process that survives script execution.
Scripts connect, do work, and disconnect - the browser stays open for user interaction.

Usage:
    uv run browser.py start                    - Start browser (if not running)
    uv run browser.py exec <script.py>         - Execute script in browser
    uv run browser.py snapshot                 - Get accessibility snapshot
    uv run browser.py stop                     - Close browser

The executed script has access to:
    - page: The current Playwright Page object
    - browser: The Browser object
    - context: The BrowserContext object
    - json: The json module (for output)
    - Path, SCREENSHOT_DIR: For file operations

Example script:
    page.goto("https://example.com")
    print(json.dumps({"url": page.url, "title": page.title()}))
"""

import sys
import json
import os
import subprocess
import time
import signal
from pathlib import Path

# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///

STATE_DIR = Path.home() / ".claude" / "browser-state"
CDP_PORT_FILE = STATE_DIR / "cdp_port"
BROWSER_PID_FILE = STATE_DIR / "browser_pid"
SCREENSHOT_DIR = Path.home() / ".claude" / "browser-screenshots"

DEFAULT_CDP_PORT = 9222


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def get_chrome_path():
    """Find Chrome executable."""
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "google-chrome",
        "chromium",
        "chrome",
    ]
    for path in candidates:
        if Path(path).exists():
            return path
        # Check if it's in PATH
        result = subprocess.run(["which", path], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    return None


def is_browser_running():
    """Check if browser is running and accessible."""
    if not BROWSER_PID_FILE.exists():
        return False

    try:
        pid = int(BROWSER_PID_FILE.read_text().strip())
        # Check if process exists
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, ValueError, FileNotFoundError):
        # Clean up stale files
        BROWSER_PID_FILE.unlink(missing_ok=True)
        CDP_PORT_FILE.unlink(missing_ok=True)
        return False


def get_cdp_endpoint():
    """Get the CDP WebSocket endpoint."""
    import urllib.request
    port = DEFAULT_CDP_PORT
    if CDP_PORT_FILE.exists():
        port = int(CDP_PORT_FILE.read_text().strip())

    try:
        with urllib.request.urlopen(f"http://localhost:{port}/json/version", timeout=2) as resp:
            data = json.loads(resp.read())
            return data.get("webSocketDebuggerUrl")
    except Exception:
        return None


def cmd_start():
    """Start browser with CDP enabled."""
    ensure_dirs()

    if is_browser_running():
        endpoint = get_cdp_endpoint()
        if endpoint:
            print(json.dumps({
                "status": "success",
                "message": "Browser already running",
                "endpoint": endpoint
            }))
            return

    chrome_path = get_chrome_path()
    if not chrome_path:
        print(json.dumps({
            "status": "error",
            "error": "Chrome not found. Install Google Chrome or Chromium."
        }))
        sys.exit(1)

    # User data dir for persistent sessions
    user_data_dir = STATE_DIR / "chrome-profile"
    user_data_dir.mkdir(parents=True, exist_ok=True)

    # Launch Chrome with remote debugging
    cmd = [
        chrome_path,
        f"--remote-debugging-port={DEFAULT_CDP_PORT}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
    ]

    # Start detached process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    # Save PID and port
    BROWSER_PID_FILE.write_text(str(process.pid))
    CDP_PORT_FILE.write_text(str(DEFAULT_CDP_PORT))

    # Wait for CDP to be ready
    for _ in range(30):  # 3 seconds max
        time.sleep(0.1)
        endpoint = get_cdp_endpoint()
        if endpoint:
            print(json.dumps({
                "status": "success",
                "message": "Browser started",
                "pid": process.pid,
                "endpoint": endpoint
            }))
            return

    print(json.dumps({
        "status": "error",
        "error": "Browser started but CDP not responding"
    }))
    sys.exit(1)


def get_browser_and_page():
    """Connect to running browser via CDP."""
    from playwright.sync_api import sync_playwright

    # Ensure browser is running
    if not is_browser_running():
        cmd_start()

    endpoint = get_cdp_endpoint()
    if not endpoint:
        print(json.dumps({
            "status": "error",
            "error": "Cannot connect to browser. Run 'browser.py start' first."
        }))
        sys.exit(1)

    p = sync_playwright().start()

    # Connect to existing browser
    browser = p.chromium.connect_over_cdp(endpoint)

    # Get or create context and page
    contexts = browser.contexts
    if contexts:
        context = contexts[0]
        pages = context.pages
        page = pages[0] if pages else context.new_page()
    else:
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

    return p, browser, context, page


def cmd_exec(script_path: str):
    """Execute a Python script with browser context available."""
    ensure_dirs()

    p, browser, context, page = get_browser_and_page()
    try:
        script_content = Path(script_path).read_text()

        # Globals available to the executed script
        exec_globals = {
            "__builtins__": __builtins__,
            "page": page,
            "browser": browser,
            "context": context,
            "playwright": p,
            "json": json,
            "Path": Path,
            "SCREENSHOT_DIR": SCREENSHOT_DIR,
        }

        exec(script_content, exec_globals)

    except FileNotFoundError:
        print(json.dumps({"status": "error", "error": f"Script not found: {script_path}"}))
        sys.exit(1)
    except Exception as e:
        import traceback
        print(json.dumps({
            "status": "error",
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }))
        sys.exit(1)
    finally:
        # Disconnect but don't close - browser stays running
        p.stop()


def cmd_snapshot():
    """Get page snapshot - useful for understanding page state."""
    ensure_dirs()

    p, browser, context, page = get_browser_and_page()
    try:
        # Get a useful summary of the page via JavaScript
        snapshot = page.evaluate("""() => {
            const result = {
                links: [],
                buttons: [],
                inputs: [],
                headings: [],
                text: ''
            };

            // Get links
            document.querySelectorAll('a[href]').forEach((a, i) => {
                if (i < 20 && a.innerText.trim()) {
                    result.links.push({text: a.innerText.trim().slice(0, 50), href: a.href});
                }
            });

            // Get buttons
            document.querySelectorAll('button, [role="button"], input[type="submit"]').forEach((b, i) => {
                if (i < 10) {
                    result.buttons.push(b.innerText?.trim() || b.value || b.getAttribute('aria-label') || 'unnamed');
                }
            });

            // Get inputs
            document.querySelectorAll('input, textarea, select').forEach((inp, i) => {
                if (i < 10) {
                    result.inputs.push({
                        type: inp.type || inp.tagName.toLowerCase(),
                        name: inp.name || inp.placeholder || inp.getAttribute('aria-label') || 'unnamed',
                        value: inp.value?.slice(0, 30) || ''
                    });
                }
            });

            // Get headings
            document.querySelectorAll('h1, h2, h3').forEach((h, i) => {
                if (i < 10 && h.innerText.trim()) {
                    result.headings.push(h.innerText.trim().slice(0, 80));
                }
            });

            // Get main text content (truncated)
            result.text = document.body?.innerText?.slice(0, 1000) || '';

            return result;
        }""")

        print(json.dumps({
            "status": "success",
            "url": page.url,
            "title": page.title(),
            "snapshot": snapshot
        }, indent=2))
    finally:
        p.stop()


def cmd_stop():
    """Stop the browser process."""
    if not BROWSER_PID_FILE.exists():
        print(json.dumps({"status": "success", "message": "Browser not running"}))
        return

    try:
        pid = int(BROWSER_PID_FILE.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.5)
        # Force kill if still running
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    except (ProcessLookupError, ValueError):
        pass

    # Clean up state files
    BROWSER_PID_FILE.unlink(missing_ok=True)
    CDP_PORT_FILE.unlink(missing_ok=True)

    print(json.dumps({"status": "success", "message": "Browser stopped"}))


def cmd_status():
    """Check browser status."""
    ensure_dirs()

    if is_browser_running():
        endpoint = get_cdp_endpoint()
        pid = int(BROWSER_PID_FILE.read_text().strip()) if BROWSER_PID_FILE.exists() else None
        print(json.dumps({
            "status": "success",
            "running": True,
            "pid": pid,
            "endpoint": endpoint
        }))
    else:
        print(json.dumps({
            "status": "success",
            "running": False
        }))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "start":
        cmd_start()
    elif cmd == "exec":
        if not args:
            print("Usage: browser.py exec <script.py>")
            sys.exit(1)
        cmd_exec(args[0])
    elif cmd == "snapshot":
        cmd_snapshot()
    elif cmd == "stop":
        cmd_stop()
    elif cmd == "status":
        cmd_status()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
