# Code Examples

## Using the Python API

### Scan local extensions

```python
from ext_tool.scanner import scan_local_extensions

extensions = scan_local_extensions()
for ext in extensions:
    print(ext["id"], ext["version"])
```

### Classify extensions against Open VSX

```python
import asyncio
from ext_tool.scanner import scan_local_extensions
from ext_tool.marketplace import classify_extensions

raw = scan_local_extensions()
registry = asyncio.run(classify_extensions(raw))

for ext in registry.extensions:
    print(f"{ext.id}  →  {ext.marketplace.value}")
```

### Load and query the saved registry

```python
from ext_tool.config import EXTENSIONS_FILE
from ext_tool.models import ExtensionRegistry

registry = ExtensionRegistry.from_toml(EXTENSIONS_FILE)
open_vsx = registry.filter_marketplace("open-vsx")
print(f"{len(open_vsx)} Open VSX extensions")
```
