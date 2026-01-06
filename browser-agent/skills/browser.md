---
name: browser
description: "Delegate browser tasks to the browser automation agent. Use for web scraping, screenshots, form filling, login flows, or any task requiring a real browser."
---

# Browser Automation

Delegate browser tasks to the specialized browser agent using the Task tool:

```
Task tool with subagent_type="browser-agent:browser"
```

The browser agent has full Playwright API access and can handle any browser automation task.

## Example Delegations

**Interactive browsing (user wants to see browser):**
```
"Open https://amazon.com so I can browse the sales. Use --keep-open so I can interact with it."
```

**Take a screenshot:**
```
"Navigate to https://example.com and take a full-page screenshot"
```

**Login and extract data:**
```
"Login to https://app.example.com as guest@test.com with password 'test123', then extract my account settings"
```

**Scrape content:**
```
"Go to https://news.ycombinator.com and get the top 20 article titles and links"
```

**Fill a form:**
```
"Navigate to https://example.com/contact, fill the form with name 'John Doe', email 'john@example.com', message 'Hello', then submit"
```

**Complex multi-step workflow:**
```
"Go to the pricing page on stripe.com, find the enterprise plan details, take a screenshot, and extract all the features listed"
```

## Browser State

The browser maintains state between agent invocations:
- Cookies persist
- Login sessions are remembered
- Can resume where you left off

**Check current state:** `"Get a snapshot of the current browser page"`
**Clear state:** `"Close the browser and clear all state"`

## Screenshots Location

Screenshots are saved to: `~/.claude/browser-screenshots/`
