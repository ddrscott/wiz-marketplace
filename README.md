# Wiz Marketplace

A collection of Claude Code plugins that extend Claude's capabilities with specialized tools and agents.

## Plugins

| Plugin | Description |
|--------|-------------|
| [browser-agent](./browser-agent) | Browser automation with persistent Chrome sessions. Full Playwright API access without the context bloat. |
| [book-creator](./book-creator) | Create structured books and documents with chapters, formatting, and export options. |

## Prerequisites

Most plugins require:

- **[uv](https://docs.astral.sh/uv/)** — Fast Python package manager (for Python-based plugins)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

See individual plugin READMEs for specific requirements.

## Installation

Plugins can be installed from this marketplace using Claude Code's plugin system.

```bash
# Example: Install browser-agent
claude plugin install wiz-marketplace/browser-agent
```

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
