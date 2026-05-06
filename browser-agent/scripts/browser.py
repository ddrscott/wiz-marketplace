#!/usr/bin/env python3
"""
Playwright browser executor with persistent browser process.

The browser runs as a separate process that survives script execution.
Scripts connect, do work, and disconnect - the browser stays open for user interaction.

Usage:
    uv run browser.py start                    - Start browser (if not running)
    uv run browser.py exec <script.py>         - Execute script in browser
    uv run browser.py snapshot                 - Get accessibility snapshot
    uv run browser.py focus                    - Bring browser window to front
    uv run browser.py status                   - Check browser status
    uv run browser.py stop                     - Close browser

Environment:
    BROWSER_AGENT_BROWSER  - Path to a Chromium-based browser binary to use.
                             Overrides the auto-detection order.

The executed script has access to:
    - page: The current Playwright Page object
    - browser: The Browser object
    - context: The BrowserContext object
    - playwright: The Playwright instance
    - json: The json module (for output)
    - Path, SCREENSHOT_DIR: For file operations

Example script:
    page.goto("https://example.com")
    print(json.dumps({"url": page.url, "title": page.title()}))
"""

import sys
import json
import os
import platform
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
BROWSER_PATH_FILE = STATE_DIR / "browser_path"
SCREENSHOT_DIR = Path.home() / ".claude" / "browser-screenshots"

DEFAULT_CDP_PORT = 9222
CDP_CONNECT_TIMEOUT_MS = 5000
DEFAULT_ACTION_TIMEOUT_MS = 10000
DEFAULT_NAVIGATION_TIMEOUT_MS = 15000

# Preference order: browsers with distinct dock icons come first,
# so the AI-controlled instance is visually distinguishable from
# the user's everyday Chrome.
BROWSER_CANDIDATES = [
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta",
    "/Applications/Google Chrome Dev.app/Contents/MacOS/Google Chrome Dev",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Arc.app/Contents/MacOS/Arc",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "chromium",
    "google-chrome-canary",
    "google-chrome-beta",
    "google-chrome",
    "chrome",
]


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def get_chrome_path():
    """Find a Chromium-based browser to launch."""
    env_path = os.environ.get("BROWSER_AGENT_BROWSER")
    if env_path and Path(env_path).exists():
        return env_path

    for path in BROWSER_CANDIDATES:
        if Path(path).exists():
            return path
        result = subprocess.run(["which", path], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    return None


def app_name_from_path(chrome_path: str) -> str | None:
    """Extract macOS app name from a binary path inside an .app bundle."""
    if not chrome_path:
        return None
    for part in chrome_path.split("/"):
        if part.endswith(".app"):
            return part[:-4]
    return None


def activate_browser_window():
    """Bring the running browser to the foreground (macOS only)."""
    if platform.system() != "Darwin":
        return
    chrome_path = None
    if BROWSER_PATH_FILE.exists():
        chrome_path = BROWSER_PATH_FILE.read_text().strip()
    if not chrome_path:
        chrome_path = get_chrome_path()
    app_name = app_name_from_path(chrome_path or "")
    if not app_name:
        return
    try:
        subprocess.run(
            ["osascript", "-e", f'tell application "{app_name}" to activate'],
            capture_output=True,
            timeout=2,
        )
    except Exception:
        pass


def get_cdp_endpoint():
    """Return the CDP WebSocket endpoint, or None if CDP isn't responding."""
    import urllib.request

    port = DEFAULT_CDP_PORT
    if CDP_PORT_FILE.exists():
        try:
            port = int(CDP_PORT_FILE.read_text().strip())
        except ValueError:
            pass

    try:
        with urllib.request.urlopen(
            f"http://localhost:{port}/json/version", timeout=2
        ) as resp:
            data = json.loads(resp.read())
            return data.get("webSocketDebuggerUrl")
    except Exception:
        return None


def is_browser_running() -> bool:
    """Browser is 'running' only if its PID is alive AND CDP responds.

    Checking the PID alone produces false positives: a wedged renderer or a
    stuck CDP listener will keep the process alive while leaving Playwright
    unable to connect. That state used to cause multi-minute hangs because
    connect_over_cdp() has no implicit timeout.
    """
    if not BROWSER_PID_FILE.exists():
        return False
    try:
        pid = int(BROWSER_PID_FILE.read_text().strip())
        os.kill(pid, 0)
    except (ProcessLookupError, ValueError, FileNotFoundError):
        BROWSER_PID_FILE.unlink(missing_ok=True)
        CDP_PORT_FILE.unlink(missing_ok=True)
        BROWSER_PATH_FILE.unlink(missing_ok=True)
        return False

    return get_cdp_endpoint() is not None


def kill_stale_browser():
    """Force-kill a browser whose PID exists but whose CDP is wedged."""
    if not BROWSER_PID_FILE.exists():
        return
    try:
        pid = int(BROWSER_PID_FILE.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.3)
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    except (ProcessLookupError, ValueError):
        pass
    BROWSER_PID_FILE.unlink(missing_ok=True)
    CDP_PORT_FILE.unlink(missing_ok=True)
    BROWSER_PATH_FILE.unlink(missing_ok=True)


def cmd_start():
    """Start browser with CDP enabled. Recovers from wedged state."""
    ensure_dirs()

    if is_browser_running():
        endpoint = get_cdp_endpoint()
        print(json.dumps({
            "status": "success",
            "message": "Browser already running",
            "endpoint": endpoint,
        }))
        return

    if BROWSER_PID_FILE.exists():
        kill_stale_browser()

    chrome_path = get_chrome_path()
    if not chrome_path:
        print(json.dumps({
            "status": "error",
            "error": "No Chromium-based browser found. Install Chromium, Chrome, Brave, or Edge.",
        }))
        sys.exit(1)

    user_data_dir = STATE_DIR / "chrome-profile"
    user_data_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        chrome_path,
        f"--remote-debugging-port={DEFAULT_CDP_PORT}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-features=ChromeWhatsNewUI",
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    BROWSER_PID_FILE.write_text(str(process.pid))
    CDP_PORT_FILE.write_text(str(DEFAULT_CDP_PORT))
    BROWSER_PATH_FILE.write_text(chrome_path)

    for _ in range(50):  # 5s max
        time.sleep(0.1)
        endpoint = get_cdp_endpoint()
        if endpoint:
            activate_browser_window()
            print(json.dumps({
                "status": "success",
                "message": "Browser started",
                "pid": process.pid,
                "endpoint": endpoint,
                "browser": chrome_path,
            }))
            return

    print(json.dumps({
        "status": "error",
        "error": "Browser started but CDP not responding within 5s",
    }))
    sys.exit(1)


def get_browser_and_page():
    """Connect to running browser via CDP. Restarts if state is wedged."""
    from playwright.sync_api import sync_playwright

    if not is_browser_running():
        # Either nothing is running, or there's a stale/wedged process.
        # cmd_start() handles both.
        cmd_start()

    endpoint = get_cdp_endpoint()
    if not endpoint:
        print(json.dumps({
            "status": "error",
            "error": "Cannot connect to browser CDP. Try: uv run browser.py stop && uv run browser.py start",
        }))
        sys.exit(1)

    p = sync_playwright().start()

    try:
        browser = p.chromium.connect_over_cdp(endpoint, timeout=CDP_CONNECT_TIMEOUT_MS)
    except Exception as e:
        p.stop()
        print(json.dumps({
            "status": "error",
            "error": f"CDP connect failed: {e}. Try: uv run browser.py stop && uv run browser.py start",
        }))
        sys.exit(1)

    contexts = browser.contexts
    if contexts:
        context = contexts[0]
        pages = context.pages
        page = pages[0] if pages else context.new_page()
    else:
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

    # Cap default waits so a bad selector fails in 10s, not 30s.
    # Without this, retries by the agent compound: 3 bad selectors = 90s.
    context.set_default_timeout(DEFAULT_ACTION_TIMEOUT_MS)
    context.set_default_navigation_timeout(DEFAULT_NAVIGATION_TIMEOUT_MS)

    return p, browser, context, page


def cmd_exec(script_path: str):
    """Execute a Python script with browser context available."""
    ensure_dirs()

    p, browser, context, page = get_browser_and_page()
    try:
        # Bring the controlled tab forward so the user can see what's happening.
        try:
            page.bring_to_front()
        except Exception:
            pass

        script_content = Path(script_path).read_text()

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
            "traceback": traceback.format_exc(),
        }))
        sys.exit(1)
    finally:
        # Activate the browser app on macOS so the user actually sees the result.
        # Without this, "navigate to amazon.com" succeeds but the window stays
        # behind the terminal and looks like nothing happened.
        activate_browser_window()
        p.stop()


def cmd_snapshot():
    """Get page snapshot - useful for understanding page state."""
    ensure_dirs()

    p, browser, context, page = get_browser_and_page()
    try:
        snapshot = page.evaluate("""() => {
            const result = {
                links: [],
                buttons: [],
                inputs: [],
                headings: [],
                text: ''
            };

            document.querySelectorAll('a[href]').forEach((a, i) => {
                if (i < 20 && a.innerText.trim()) {
                    result.links.push({text: a.innerText.trim().slice(0, 50), href: a.href});
                }
            });

            document.querySelectorAll('button, [role="button"], input[type="submit"]').forEach((b, i) => {
                if (i < 10) {
                    result.buttons.push(b.innerText?.trim() || b.value || b.getAttribute('aria-label') || 'unnamed');
                }
            });

            document.querySelectorAll('input, textarea, select').forEach((inp, i) => {
                if (i < 10) {
                    result.inputs.push({
                        type: inp.type || inp.tagName.toLowerCase(),
                        name: inp.name || inp.placeholder || inp.getAttribute('aria-label') || 'unnamed',
                        value: inp.value?.slice(0, 30) || ''
                    });
                }
            });

            document.querySelectorAll('h1, h2, h3').forEach((h, i) => {
                if (i < 10 && h.innerText.trim()) {
                    result.headings.push(h.innerText.trim().slice(0, 80));
                }
            });

            result.text = document.body?.innerText?.slice(0, 1000) || '';

            return result;
        }""")

        print(json.dumps({
            "status": "success",
            "url": page.url,
            "title": page.title(),
            "snapshot": snapshot,
        }, indent=2))
    finally:
        p.stop()


def cmd_focus():
    """Bring the browser window to the foreground."""
    if not is_browser_running():
        print(json.dumps({"status": "error", "error": "Browser is not running"}))
        sys.exit(1)
    activate_browser_window()
    print(json.dumps({"status": "success", "message": "Browser activated"}))


def cmd_stop():
    """Stop the browser process."""
    if not BROWSER_PID_FILE.exists():
        print(json.dumps({"status": "success", "message": "Browser not running"}))
        return

    try:
        pid = int(BROWSER_PID_FILE.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.5)
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    except (ProcessLookupError, ValueError):
        pass

    BROWSER_PID_FILE.unlink(missing_ok=True)
    CDP_PORT_FILE.unlink(missing_ok=True)
    BROWSER_PATH_FILE.unlink(missing_ok=True)

    print(json.dumps({"status": "success", "message": "Browser stopped"}))


def cmd_status():
    """Check browser status."""
    ensure_dirs()

    if is_browser_running():
        endpoint = get_cdp_endpoint()
        pid = int(BROWSER_PID_FILE.read_text().strip()) if BROWSER_PID_FILE.exists() else None
        browser_path = BROWSER_PATH_FILE.read_text().strip() if BROWSER_PATH_FILE.exists() else None
        print(json.dumps({
            "status": "success",
            "running": True,
            "pid": pid,
            "endpoint": endpoint,
            "browser": browser_path,
        }))
    else:
        print(json.dumps({"status": "success", "running": False}))


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
    elif cmd == "focus":
        cmd_focus()
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
