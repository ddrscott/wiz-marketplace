---
name: fal
description: "Generate images, videos, audio with AI. Examples: /fal meme image, /fal landscape photo for blog, /fal video from this image"
arguments:
  - name: request
    description: "What to generate: image, video, audio. Include style, size, model hints."
    required: true
---

# Fal Media Generation

Generate: **$ARGUMENTS**

## Your Task

1. **Parse the request** - What media type? What style/quality?
2. **Select model** - Use the guide below. **Confirm if ambiguous or expensive.**
3. **Look up params** - Use `mcp__fal__SearchFal` if unsure about model parameters
4. **Execute** - Write inline Python, run with `uv run`
5. **Report** - Show the user their generated media

## Quick Model Reference

| Request Type | Recommended Model | Cost |
|--------------|-------------------|------|
| Quick/meme/draft image | `fal-ai/flux-2/turbo` | $ |
| Quality image | `fal-ai/flux-2` | $$ |
| Professional image | `fal-ai/flux-2-pro` | $$$ |
| Qwen quality | `fal-ai/qwen-image-2512` | $$ |
| Text in image | `fal-ai/ideogram/v2` | $$ |
| Quick video | `fal-ai/minimax/video-01` | $$ |
| Quality video | `fal-ai/kling-video/v1.5/pro/text-to-video` | $$$$ |
| Image to video | `fal-ai/minimax/video-01/image-to-video` | $$ |
| Upscale | `fal-ai/esrgan` | $ |
| Remove background | `fal-ai/imageutils/rembg` | $ |
| Image editing | `fal-ai/qwen-image-edit-2511` | $$ |

## Size Hints

- "landscape" → `landscape_16_9`
- "portrait" → `portrait_4_3`
- "square" → `square_hd`

## Execution

Write inline Python to /tmp, run with uv:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["fal-client", "httpx"]
# ///
import fal_client
import httpx
from pathlib import Path

result = fal_client.run("MODEL_ID", arguments={
    "prompt": "...",
    "image_size": "landscape_16_9"
})

# Download result
url = result["images"][0]["url"]  # or result["video"]["url"]
output = Path.home() / ".claude" / "fal-output" / "filename.png"
output.parent.mkdir(parents=True, exist_ok=True)
with httpx.stream("GET", url, follow_redirects=True) as r:
    with open(output, "wb") as f:
        for chunk in r.iter_bytes():
            f.write(chunk)
print(f"Saved: {output}")
```

Run: `uv run /tmp/fal_gen.py`

## Rules

1. **Confirm expensive models** - Video, Pro, Ultra models need user confirmation
2. **Default to fast/cheap** - Unless user asks for quality
3. **Show the result** - Always report the output path
4. **Search if needed** - Use `mcp__fal__SearchFal` to find new models or params
