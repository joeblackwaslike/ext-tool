# Getting Started

Install `ext-tool` via `uv` or `pipx`:

```bash
uv tool install ext-tool
# or
pipx install ext-tool
```

Then generate your extension registry from your currently-installed extensions:

```bash
ext generate
```

This scans your local VS Code / Cursor extensions directory, classifies each extension
against the Open VSX registry, and writes a TOML registry to
`~/.config/ext-tool/extensions.toml`.

To install all extensions from an existing registry on a new machine:

```bash
ext install
```
