# API Reference

`ext-tool` exposes a public Python API that can be used without the CLI.
The core modules are documented below.

| Module | Description |
| --- | --- |
| [`ext_tool.models`](models.md) | `Extension`, `ExtensionRegistry`, `ExportFormat`, `Marketplace` |
| [`ext_tool.config`](config.md) | `AppConfig` — settings loaded from file, env, and CLI flags |
| [`ext_tool.marketplace`](marketplace.md) | Open VSX classification and VSIX install helpers |
| [`ext_tool.scanner`](scanner.md) | Local extension directory reader |
| [`ext_tool.cache`](cache.md) | Disk-backed TTL cache used during Open VSX queries |
| [`ext_tool.cli`](cli.md) | Typer application entrypoint |
| [`ext_tool.logging`](logging.md) | Logging configuration helpers |

## Quick example

```python
import asyncio
from ext_tool.scanner import resolve_extensions_dir, scan_local_extensions
from ext_tool.marketplace import classify_extensions
from ext_tool.models import ExtensionRegistry, Marketplace

# Scan and classify
extensions_dir = resolve_extensions_dir("cursor", override=None)
raw = scan_local_extensions(extensions_dir)
registry = asyncio.run(classify_extensions(raw, concurrency=10))

# Query
ms_extensions = registry.filter_marketplace(Marketplace.MICROSOFT)
print(f"{len(ms_extensions)} Microsoft-only extensions")

# Persist
registry.save("/tmp/my-extensions.toml")

# Reload
loaded = ExtensionRegistry.load("/tmp/my-extensions.toml")
```
