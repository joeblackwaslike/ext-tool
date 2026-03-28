# ext-tool

**`ext`** — a unified CLI for managing VS Code / Cursor extensions from a single source-of-truth TOML registry.

## Features

- **`ext generate`** — scan installed extensions, query Open VSX, build `extensions.toml`
- **`ext install`** — install all/filtered extensions, routing each to the right marketplace
- **`ext update`** — re-generate and re-install in one step
- **`ext export`** — export registry as TOML, JSON, or CSV
- **`ext import`** — import an exported file into the registry
- **`ext completions`** — generate shell completions (bash / zsh / fish)
- Sleek Rich-powered terminal UI
- Config lives at `~/.config/ext-tool/` (config.toml + extensions.toml)
- `--debug` flag or `EXT_DEBUG=1` env var writes a detailed debug log

## Install

```bash
# via uv tool (recommended)
uv tool install ext-tool

# via pipx
pipx install ext-tool
```

## Quick Start

```bash
# Scan installed extensions and build the registry
ext generate

# Install everything on a new machine
ext install

# Only install Microsoft-marketplace extensions
ext install --marketplace microsoft

# Export registry as JSON
ext export registry.json --format json

# Shell completions (add to ~/.zshrc)
ext completions zsh >> ~/.zshrc
```

## Configuration

Default config file: `~/.config/ext-tool/config.toml`

```toml
helper = "cursor"           # CLI to use: cursor | code | code-insiders
extensions_dir = ""         # leave empty for auto-detection
concurrency = 10            # Open VSX check concurrency
```

## Development

```bash
git clone https://github.com/joeblackwaslike/ext-tool
cd ext-tool
uv sync
uv run ext --help
```

## License

MIT © Joe Black
