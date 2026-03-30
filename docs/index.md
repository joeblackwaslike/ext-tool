# ext-tool

**Manage VS Code and Cursor extensions from a single source-of-truth TOML registry.**

[![Release](https://img.shields.io/github/v/release/joeblackwaslike/ext-tool)](https://github.com/joeblackwaslike/ext-tool/releases)
[![Build status](https://img.shields.io/github/actions/workflow/status/joeblackwaslike/ext-tool/main.yml?branch=main)](https://github.com/joeblackwaslike/ext-tool/actions/workflows/main.yml?query=branch%3Amain)
[![License](https://img.shields.io/github/license/joeblackwaslike/ext-tool)](https://github.com/joeblackwaslike/ext-tool/blob/main/LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue)](https://www.python.org/)

`ext-tool` solves the friction of keeping VS Code and Cursor extensions in sync across
machines. It scans your locally installed extensions, classifies each one as Open VSX or
Microsoft-only, persists the result to a portable TOML file, and reproduces the full setup
on any new machine with a single command.

---

## Why ext-tool?

| Problem | Solution |
| --- | --- |
| Extensions differ between machines | One TOML registry as the source of truth |
| Microsoft extensions can't be installed via Open VSX | Automatic marketplace routing |
| Sharing a dev environment with teammates | Export to JSON or CSV, import anywhere |
| Manual extension management is tedious | `ext update` does generate + install in one step |

---

## Quick example

```bash
# Snapshot what's installed right now
ext generate

# On a new machine — reproduce everything
ext install
```

The registry lives at `~/.config/ext-tool/extensions.toml` — a human-readable TOML file
designed to be committed to your dotfiles repo.

---

## Features

- **Automatic classification** — queries Open VSX in parallel to determine which extensions
  are available there vs. Microsoft-only
- **Smart routing** — Open VSX extensions installed via `$helper --install-extension`;
  Microsoft-only extensions downloaded as VSIX and installed directly
- **Portable registry** — human-readable TOML, version-control friendly
- **Export / import** — share your registry as TOML, JSON, or CSV
- **Configurable** — override helper binary, extensions directory, concurrency, and more
- **Shell completions** — bash, zsh, and fish

---

[Get started :octicons-arrow-right-24:](getting-started.md){ .md-button .md-button--primary }
[Browse commands :octicons-terminal-24:](commands.md){ .md-button }
