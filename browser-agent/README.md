# Browser Agent Plugin

**Stop fighting your browser automation. Start controlling it.**

Other solutions eat 16k tokens just to tell you what's on a page, or kill your browser the moment a script ends. This plugin gives you a persistent Chrome session that stays open while you work—switch between AI automation and manual browsing whenever you want, without losing your session or burning context.

---

## Quick Start

```bash
# Start browsing
/browser navigate to https://amazon.com

# Interact with page
/browser search for VR headsets
/browser what's the top pick on this page?
/browser click Add to Cart

# Get info
/browser summarize this page
/browser screenshot

# Done
/browser stop
```

## Why This Exists

| Problem | Existing Solutions | This Plugin |
|---------|-------------------|-------------|
| **Context bloat** | Microsoft's [playwright-mcp](https://github.com/microsoft/playwright-mcp) dumps ~16k tokens of accessibility tree on every call | Sends only what you ask for—script results, not the kitchen sink |
| **Browser lifecycle** | [playwright-skill](https://github.com/lackeyjb/playwright-skill) opens/closes browser constantly | Persistent Chrome process via CDP—browser survives script execution |
| **Handoff friction** | Most tools lock you out while automating | Take over manually anytime, then let the agent resume |
| **Limited API** | Predefined commands can't handle edge cases | Full Playwright API—Claude writes custom scripts for each task |

### The Goal

Leverage Claude Code's plugin architecture (agents, skills, commands) to create a **context-friendly** browser automation solution with all the power of MCP tools—without the overhead.

## Commands

### `/browser <action>`

Quick browser control from the command line.

| Action | Examples |
|--------|----------|
| Navigate | `/browser go to amazon.com`, `/browser navigate to https://news.ycombinator.com` |
| Search | `/browser search for gaming laptops` |
| Click | `/browser click Sign In`, `/browser click Add to Cart` |
| Fill | `/browser fill email with test@example.com` |
| Summarize | `/browser summarize page`, `/browser what's on this page?` |
| Extract | `/browser get all links`, `/browser what's the top pick?` |
| Screenshot | `/browser screenshot`, `/browser capture page` |
| Status | `/browser status`, `/browser where am I?` |
| Stop | `/browser stop`, `/browser close browser` |

## How It Works

```
┌─────────────────┐          ┌──────────────────────┐
│  /browser cmd   │──────────│  Chrome (persistent) │
│  or Task agent  │   CDP    │  --remote-debugging  │
└─────────────────┘          └──────────────────────┘
        │                              ▲
        ▼                              │
   script runs                    stays open
   then disconnects              user can interact
```

1. Chrome launches with CDP (Chrome DevTools Protocol) on first use
2. Claude writes Python scripts using full Playwright API
3. Scripts connect to browser, execute, disconnect
4. **Browser stays open**—interact directly anytime
5. Next command reconnects to same session (cookies/logins persist)

## Prerequisites

- **Chrome or Chromium** — Uses your system browser
- **Python 3.11+** — For running Playwright scripts
- **[uv](https://docs.astral.sh/uv/)** — Fast Python package manager

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

1. Install the plugin
2. Verify Chrome is installed (the plugin auto-detects it)

## Agent Usage

For complex tasks, use the browser agent directly:

```
Task tool with subagent_type="browser-agent:browser"
```

Example prompts:
- "Login to GitHub and star the anthropics/claude-code repo"
- "Go to Hacker News, find posts about AI, and summarize the top 5"
- "Fill out the contact form at example.com/contact with my info"

## Browser Commands (CLI)

```bash
# Start browser (auto-starts on first exec if needed)
uv run browser.py start

# Execute a Playwright script
uv run browser.py exec script.py

# Check browser status
uv run browser.py status

# Stop browser
uv run browser.py stop
```

## State Locations

| What | Where |
|------|-------|
| Chrome profile | `~/.claude/browser-state/chrome-profile/` |
| Screenshots | `~/.claude/browser-screenshots/` |
| PID/port files | `~/.claude/browser-state/` |

## Components

```
browser-agent/
├── commands/
│   └── browser.md      # /browser slash command
├── agents/
│   └── browser.md      # Agent with Playwright API reference
├── skills/
│   └── browser.md      # Skill for delegating browser tasks
├── scripts/
│   └── browser.py      # Browser lifecycle manager & executor
└── plugin.json
```

## License

MIT
