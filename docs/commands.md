# Command Reference

All commands share a common set of global options:

```
ext [OPTIONS] COMMAND [ARGS]...

Global options:
  --version                    Show version and exit.
  --debug                      Write a debug log to ./ext.debug-<id>.log.
  --helper TEXT                VS Code-compatible CLI binary  [default: cursor]
  --extensions-file PATH       Path to the registry TOML file.
  --help                       Show this message and exit.
```

---

## ext generate

Scan locally installed extensions, classify each one via Open VSX, and write the registry.

```bash
ext generate [--dry-run]
```

| Flag | Description |
| --- | --- |
| `--dry-run` | Print the classified table without saving |

**What happens:**

1. Resolves the extensions directory for your system and helper binary
2. Reads `extensions.json` from each installed extension sub-directory
3. Queries Open VSX in parallel (up to `concurrency` simultaneous requests)
4. Writes `~/.config/ext-tool/extensions.toml`

```bash
ext generate               # scan and save
ext generate --dry-run     # preview only
ext --helper code generate # use VS Code instead of Cursor
```

---

## ext install

Install extensions from the registry onto the current machine.

```bash
ext install [--marketplace {all|open-vsx|microsoft}] [--dry-run]
```

| Flag | Default | Description |
| --- | --- | --- |
| `--marketplace` | `all` | Restrict to `open-vsx` or `microsoft` extensions only |
| `--dry-run` | — | Print what would be installed without executing anything |

**Routing logic:**

| Marketplace | Install method |
| --- | --- |
| `open-vsx` | `$helper --install-extension <id>` |
| `microsoft` | Download `.vsix` from `gallery.vsassets.io`, then `$helper --install-vsix <path>` |

```bash
ext install                          # install everything
ext install --marketplace open-vsx   # Open VSX only
ext install --marketplace microsoft  # Microsoft VSIX only
ext install --dry-run                # preview
```

---

## ext update

Shortcut for `ext generate` followed by `ext install`. Keeps the registry and
local installations in sync in a single step.

```bash
ext update [--marketplace {all|open-vsx|microsoft}] [--dry-run]
```

Accepts the same flags as `ext install`.

---

## ext export

Export the registry to a portable file.

```bash
ext export OUTPUT [--format {toml|json|csv}]
```

| Argument/Flag | Description |
| --- | --- |
| `OUTPUT` | Destination file path |
| `--format` / `-f` | Override format (inferred from file suffix if omitted) |

**Format inference:**

| Suffix | Format |
| --- | --- |
| `.toml` | TOML (same format as the registry itself) |
| `.json` | JSON with an `extensions` array |
| `.csv` | CSV with one row per extension |

```bash
ext export ~/backup.toml
ext export ~/share.json --format json
ext export ~/share.csv
```

---

## ext import

Import a previously exported registry file.

```bash
ext import SOURCE [--format {toml|json|csv}] [--merge|--replace]
```

| Flag | Default | Description |
| --- | --- | --- |
| `--format` / `-f` | *(inferred from suffix)* | Override format detection |
| `--merge` | ✓ default | Merge imported entries into the existing registry; imported entry wins on conflict |
| `--replace` | — | Overwrite the entire registry (prompts for confirmation) |

```bash
ext import ~/share.toml              # merge (default)
ext import ~/share.json --replace    # replace with confirmation prompt
ext import ~/share.csv --format csv  # explicit format
```

---

## ext completions

Emit a shell completion script for the current shell.

```bash
ext completions {bash|zsh|fish} [--show-install]
```

| Flag | Description |
| --- | --- |
| `--show-install` | Print installation instructions instead of the script |

See [Shell Completions](completions.md) for per-shell setup details.
