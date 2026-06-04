# Wiz Marketplace

A collection of Claude Code plugins that extend Claude's capabilities with specialized tools and agents.

## Plugins

| Plugin | Description |
|--------|-------------|
| [browser-agent](./browser-agent) | Browser automation with persistent Chrome sessions. Full Playwright API access without the context bloat. |
| [fal-agent](./fal-agent) | AI media generation using fal.ai. Smart model selection for images, videos, and audio without the research. |
| [book-creator](./book-creator) | Create structured books and documents with chapters, formatting, and export options. |
| [app-feedback-now](./app-feedback-now) | Leave inline comments on a live web app without touching the source. Bookmarklet + localhost sidecar; Claude edits source files in response. Fork of [make-pages-interactive](https://github.com/paraschopra/make-pages-interactive) adapted for wrangler/vite/astro dev servers. |
| [work](./work) | Persistent FIFO work queue for isolated, sequential task execution. Add tasks, drain them one at a time with isolated worker agents, or auto-process with a `/work:monitor` watcher. |

## Prerequisites

Most plugins require:

- **[uv](https://docs.astral.sh/uv/)** — Fast Python package manager (for Python-based plugins)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

See individual plugin READMEs for specific requirements.

## Installation

Installing plugins is a two-step process: first add the marketplace, then install individual plugins.

### Step 1: Add the marketplace

From within Claude Code, run:

```
/plugin marketplace add ddrscott/wiz-marketplace
```

### Step 2: Install plugins

Install the plugins you want using the `plugin-name@marketplace-name` format:

```
/plugin install browser-agent@wiz-marketplace
/plugin install fal-agent@wiz-marketplace
```

**Or use the interactive UI:** Run `/plugin`, go to the **Discover** tab, and select plugins to install.

### Troubleshooting

- **`/plugin` command not recognized?** Update Claude Code to version 1.0.33 or later
- **Marketplace not loading?** Verify you have internet access and the repository is public
- **Plugin not appearing?** Try `/plugin marketplace update wiz-marketplace`

## Philosophy

These plugins are built with a focus on:

- **Context efficiency** — Send only what's needed, not kitchen-sink tool definitions
- **Native patterns** — Leverage Claude Code's agents, skills, and commands properly
- **User control** — Let users take over when needed, don't lock them out

## Structure

Each plugin follows the Claude Code plugin convention:

```
plugin-name/
├── plugin.json          # Manifest with name, version, description
├── agents/              # Specialized subagents
├── skills/              # Knowledge and delegation patterns
├── commands/            # Slash commands (/command)
├── scripts/             # Supporting scripts
└── README.md            # Plugin documentation
```

## Contributing

1. Create a new directory for your plugin
2. Add `plugin.json` with name, version, description
3. Add agents, skills, commands as needed
4. Document in README.md
5. Submit PR

## License

MIT
