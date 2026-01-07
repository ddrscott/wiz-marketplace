# Fal Agent Plugin

**Generate images, videos, and audio without the research.**

Other tools make you memorize model names, dig through docs, and guess at parameters. This plugin picks the right model for your task—and asks when it's not sure.

---

## Quick Start

```bash
# Casual meme image
/fal create a meme about debugging at 3am, landscape

# Blog featured image
/fal professional landscape image of a futuristic city for my tech blog

# Video (will confirm - it's expensive)
/fal generate a 5 second video of clouds moving across sky

# Image to video
/fal turn this image into a video with gentle zoom: https://example.com/image.jpg

# Upscale existing image
/fal upscale this image 4x: /path/to/image.jpg
```

## Why This Exists

| Problem | Old Way | Fal Agent |
|---------|---------|-----------|
| **Model confusion** | Research 50+ models, compare pricing | Agent picks based on your task |
| **Parameter guessing** | Read docs for each model's args | Agent knows the defaults |
| **Cost surprises** | Run expensive model accidentally | Confirms before costly operations |
| **Outdated info** | Hardcoded model lists go stale | MCP server searches live docs |

## How It Works

1. You describe what you want in plain English
2. Agent selects appropriate model based on:
   - Media type (image/video/audio)
   - Quality hints ("quick", "professional", "best")
   - Size hints ("landscape", "square", "portrait")
3. **If ambiguous or expensive, it asks you to confirm**
4. Generates and delivers the result

## Model Selection

The agent uses these heuristics:

| Your Request | Model Choice | Why |
|--------------|--------------|-----|
| "meme", "quick", "draft" | FLUX 2 Turbo | Fast, cheap |
| "blog", "featured" | FLUX 2 | Good quality |
| "professional", "print" | FLUX 2 Pro | Best quality |
| "text in image" | Ideogram V2 | Specialized |
| "video" | Minimax/Kling | Always confirms |

### Confirmation Required

The agent **always asks** before:
- Video generation (expensive)
- Pro/Ultra tier models
- Ambiguous quality requests ("best" could mean different things)

## Commands

### `/fal <request>`

Quick generation from command line.

```bash
/fal landscape sunset photo, dreamy style
/fal square product shot of headphones on marble
/fal remove background from ./photo.jpg
/fal upscale ./image.png 4x
```

## Prerequisites

- **FAL_KEY** environment variable with your [fal.ai API key](https://fal.ai/dashboard/keys)
- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** package manager

```bash
# Set your API key
export FAL_KEY="your-key-here"

# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Output Location

Generated media is saved to `~/.claude/fal-output/`

## Searching for New Models

The plugin uses fal's MCP server to search their documentation for the latest models:

```
mcp__fal__SearchFal: "flux pro ultra features"
mcp__fal__SearchFal: "video generation pricing 2025"
```

This keeps model info fresh without hardcoding everything.

## Components

```
fal-agent/
├── plugin.json         # Manifest
├── .mcp.json           # Fal MCP server config
├── agents/
│   └── fal.md          # Agent with model selection logic
├── commands/
│   └── fal.md          # /fal slash command
└── skills/
    └── fal.md          # Delegation skill
```

## Troubleshooting

**"FAL_KEY not set"**
```bash
export FAL_KEY="your-key-from-fal-dashboard"
```

**Model not found**
- Models change frequently. Use `/fal search for <model type>` to find current options.

**Unexpected cost**
- The agent should confirm expensive operations. If it didn't, file an issue.

## License

MIT
