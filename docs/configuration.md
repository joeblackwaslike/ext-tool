# Configuration

`ext-tool` resolves settings in this priority order (highest wins):

1. **CLI flags** — `ext --helper code generate`
2. **Environment variables** — `EXT_HELPER=code`
3. **Config file** — `~/.config/ext-tool/config.toml`
4. **Built-in defaults**

---

## Config file

The config file lives at `~/.config/ext-tool/config.toml`.
It is created automatically on first run.

```toml
helper = "cursor"
extensions_file = "/home/user/.config/ext-tool/extensions.toml"
concurrency = 10
```

---

## Settings reference

| Key | Env var | Default | Description |
| --- | --- | --- | --- |
| `helper` | `EXT_HELPER` | `cursor` | VS Code-compatible CLI binary |
| `extensions_file` | `EXT_EXTENSIONS_FILE` | `~/.config/ext-tool/extensions.toml` | Registry file path |
| `extensions_dir` | `EXT_EXTENSIONS_DIR` | *(auto-detected)* | Override the extensions directory |
| `concurrency` | `EXT_CONCURRENCY` | `10` | Max parallel Open VSX API requests (1–50) |
| `debug` | `EXT_DEBUG` | `false` | Write a debug log to `./ext.debug-<id>.log` |

---

## Choosing a helper binary

=== "Cursor"
    ```toml
    helper = "cursor"
    ```

=== "VS Code"
    ```toml
    helper = "code"
    ```

=== "VS Code Insiders"
    ```toml
    helper = "code-insiders"
    ```

=== "VSCodium"
    ```toml
    helper = "codium"
    ```

Override per-invocation without touching the config file:

```bash
ext --helper code generate
```

---

## Extensions directory

`ext-tool` auto-detects the extensions directory from the helper binary.
Default locations:

| Platform | Path |
| --- | --- |
| macOS (Cursor) | `~/.cursor/extensions` |
| macOS (VS Code) | `~/.vscode/extensions` |
| Linux (Cursor) | `~/.cursor/extensions` |
| Linux (VS Code) | `~/.vscode/extensions` |
| Windows (VS Code) | `%USERPROFILE%\.vscode\extensions` |

Override for non-standard locations (containers, portable installs):

```bash
ext --extensions-dir /custom/path/extensions generate
```

Or persistently:

```toml
extensions_dir = "/custom/path/extensions"
```

---

## Concurrency

`concurrency` controls how many Open VSX API requests are made in parallel during
`ext generate`. The default of `10` is conservative; increase it if you have many
extensions and a fast connection:

```toml
concurrency = 25
```

Maximum allowed value is `50`.

---

## Debug logging

Enable debug mode to write a detailed log file to the current directory:

```bash
EXT_DEBUG=1 ext generate
# or
ext --debug generate
```

The log file is named `ext.debug-<6hexchars>.log`.
