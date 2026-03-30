# Installation

## Requirements

- **Python 3.12+**
- **VS Code or Cursor** with a compatible CLI binary in your `$PATH`

| Editor | CLI binary |
| --- | --- |
| Cursor | `cursor` |
| VS Code | `code` |
| VS Code Insiders | `code-insiders` |
| VSCodium | `codium` |

Verify your CLI works before installing ext-tool:

```bash
cursor --version   # or: code --version
```

---

## Install via uv (recommended)

[uv](https://docs.astral.sh/uv/) is the fastest way to install Python CLI tools.
It manages an isolated environment automatically.

```bash
uv tool install ext-tool
```

Upgrade later with:

```bash
uv tool upgrade ext-tool
```

---

## Install via pipx

```bash
pipx install ext-tool
```

Upgrade later with:

```bash
pipx upgrade ext-tool
```

---

## Install from source

```bash
git clone https://github.com/joeblackwaslike/ext-tool.git
cd ext-tool
uv sync
uv run ext --help
```

When installing from source, prefix all commands with `uv run`:

```bash
uv run ext generate
uv run ext install
```

---

## Verify installation

```bash
ext --version
ext --help
```
