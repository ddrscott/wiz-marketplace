---
name: browser
description: "Quick browser commands - /browser <action>. Examples: summarize page, screenshot, navigate to <url>, click <element>, search for <query>"
arguments:
  - name: action
    description: "What to do: summarize, screenshot, navigate <url>, click <text>, search <query>, status, stop"
    required: true
---

# Browser Command

Execute the following browser action: **$ARGUMENTS**

Use the browser agent to accomplish this. The browser runs as a persistent process - connect, do the work, report back.

## Quick Reference

| Action | Example |
|--------|---------|
| Summarize current page | `summarize`, `summarize page`, `what's on this page` |
| Take screenshot | `screenshot`, `capture page` |
| Navigate | `navigate to https://example.com`, `go to amazon.com` |
| Search on current site | `search for VR headsets` |
| Click element | `click Sign In`, `click the cart button` |
| Fill form | `fill email with test@example.com` |
| Check status | `status`, `where am I` |
| Stop browser | `stop`, `close browser` |

## Execution

Write a Python script using Playwright API to accomplish: **$ARGUMENTS**

Execute via: `uv run ${CLAUDE_PLUGIN_ROOT}/scripts/browser.py exec <script.py>`

For simple status checks, use: `uv run ${CLAUDE_PLUGIN_ROOT}/scripts/browser.py status`

Report results concisely to the user.
