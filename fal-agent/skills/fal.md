---
name: fal
description: "Delegate media generation tasks to the fal agent. Use for images, videos, audio, upscaling, background removal."
---

# Fal Media Generation

Delegate media generation to the fal agent:

```
Task tool with subagent_type="fal-agent:fal"
```

Or use the `/fal` command directly.

## Example Delegations

**Quick meme image:**
```
"Create a funny meme image about debugging code, landscape format"
```

**Blog featured image:**
```
"Generate a professional landscape image for my blog post about AI agents"
```

**Video from image:**
```
"Turn this image into a 5 second video with gentle motion"
```

**Quality matters:**
```
"Create a high-quality product shot of a smartwatch on white background"
```

## Model Selection

The agent picks models based on your request:

- **Casual/meme** → Fast, cheap models
- **Blog/professional** → Quality models
- **Video** → Will confirm (expensive)
- **Specific model** → Honors your choice

If ambiguous, the agent will ask you to confirm.
