# Workflows

Common patterns for using `ext-tool` day-to-day.

---

## Setting up a new machine

Reproduce your exact extension set on a fresh install.

```bash
# On your existing machine (if you haven't already)
ext generate

# Copy or pull your extensions.toml onto the new machine, then:
ext install
```

!!! tip "Keep your registry in version control"
    Commit `~/.config/ext-tool/extensions.toml` to a dotfiles repo.
    On any new machine, clone your dotfiles and run `ext install`.

---

## Keeping extensions in sync

After installing new extensions manually in the editor, re-snapshot and re-install in one step:

```bash
ext update
```

This re-scans what's installed, re-classifies against Open VSX, and installs anything
new or changed.

---

## Switching editors (e.g. Cursor → VS Code)

Your registry is editor-agnostic. To install your Cursor extensions into VS Code:

```bash
ext install --helper code
```

To make VS Code the default going forward:

```toml
# ~/.config/ext-tool/config.toml
helper = "code"
```

---

## Installing only Open VSX extensions

Useful in restricted environments (air-gapped networks, corporate proxies) where
Microsoft VSIX downloads aren't possible:

```bash
ext install --marketplace open-vsx
```

---

## Sharing your extension set with a team

Export your registry to JSON for easy distribution:

```bash
ext export ~/extensions-export.json
```

A teammate imports it and installs:

```bash
ext import ~/extensions-export.json  # merges by default
ext install
```

By default, import **merges** — their existing extensions are preserved and yours are
added (imported entry wins on conflict). To replace their registry entirely:

```bash
ext import ~/extensions-export.json --replace
```

---

## Backing up and restoring

```bash
# Back up with a datestamp
ext export ~/backups/extensions-$(date +%Y%m%d).toml

# Restore from backup
ext import ~/backups/extensions-20250101.toml --replace
ext install
```

---

## Dry-run before committing

Preview what any command would do before it touches disk or spawns subprocesses:

```bash
ext generate --dry-run   # show what would be written
ext install --dry-run    # show what would be installed
ext update --dry-run     # show both steps
```

---

## Using the Python API directly

For scripting or tooling integration, the public API is available without the CLI.

### Query the registry

```python
from ext_tool.models import ExtensionRegistry, Marketplace

registry = ExtensionRegistry.load("/home/user/.config/ext-tool/extensions.toml")

# Filter by marketplace
open_vsx = registry.filter_marketplace(Marketplace.OPEN_VSX)
microsoft = registry.filter_marketplace(Marketplace.MICROSOFT)
print(f"Open VSX: {len(open_vsx)}, Microsoft: {len(microsoft)}")

# Look up a specific extension
ext = registry.by_id("ms-python.python")
if ext:
    print(f"{ext.name} v{ext.version}")
```

### Scan and classify programmatically

```python
import asyncio
from ext_tool.scanner import scan_local_extensions, resolve_extensions_dir
from ext_tool.marketplace import classify_extensions

extensions_dir = resolve_extensions_dir("cursor", override=None)
raw = scan_local_extensions(extensions_dir)
registry = asyncio.run(classify_extensions(raw, concurrency=10))
registry.save("/tmp/my-extensions.toml")
```

### Merge two registries

```python
from ext_tool.models import ExtensionRegistry

base = ExtensionRegistry.load("~/.config/ext-tool/extensions.toml")
incoming = ExtensionRegistry.load("~/share/team.toml")

merged = base.merge(incoming)   # incoming wins on conflict
merged.save("~/.config/ext-tool/extensions.toml")
```
