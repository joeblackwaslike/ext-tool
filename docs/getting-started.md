# Getting Started

This guide walks you from zero to a working registry in under five minutes.

## Prerequisites

- Python 3.12 or later
- VS Code or Cursor with the `code` or `cursor` CLI accessible in your `$PATH`

Verify your CLI is accessible:

```bash
cursor --version   # or: code --version
```

## 1. Install ext-tool

=== "uv (recommended)"
    ```bash
    uv tool install ext-tool
    ```

=== "pipx"
    ```bash
    pipx install ext-tool
    ```

Verify:

```bash
ext --version
```

## 2. Scan your installed extensions

```bash
ext generate
```

This:

1. Finds the VS Code / Cursor extensions directory for your system
2. Reads the installed extension manifests
3. Queries Open VSX in parallel to classify each extension
4. Writes `~/.config/ext-tool/extensions.toml`

!!! tip
    `ext generate --dry-run` prints the classified table without saving anything.

## 3. Inspect your registry

```bash
cat ~/.config/ext-tool/extensions.toml
```

Each entry looks like:

```toml
[[extension]]
id = "ms-python.python"
name = "Python"
description = "Python language support with IntelliSense, Debugging, linting..."
publisher = "ms-python"
publisher_display_name = "Microsoft"
version = "2024.4.0"
marketplace = "microsoft"

[[extension]]
id = "charliermarsh.ruff"
name = "Ruff"
description = "A Visual Studio Code extension with support for the Ruff linter."
publisher = "charliermarsh"
publisher_display_name = "Charlie Marsh"
version = "2024.26.0"
marketplace = "open-vsx"
```

Extensions with `marketplace = "open-vsx"` install via your helper CLI.
Extensions with `marketplace = "microsoft"` are downloaded as VSIX files.

## 4. Reproduce on another machine

Copy or commit your `extensions.toml` to your dotfiles repo, then on the new machine:

```bash
ext install
```

`ext-tool` routes each extension to the correct installer automatically.

## Next steps

- [Configuration](configuration.md) — change the helper binary, concurrency, or registry path
- [Workflows](workflows.md) — dotfiles sync, team sharing, editor switching, and more
- [Commands](commands.md) — full command reference
