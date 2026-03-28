# Usage

## Commands

### `ext generate`

Scan the local extensions directory, classify each extension via Open VSX,
and write the registry to `~/.config/ext-tool/extensions.toml`.

```bash
ext generate
ext generate --dry-run   # print what would be written without saving
```

### `ext install`

Install all (or filtered) extensions from the registry.

```bash
ext install                        # install all
ext install --marketplace open-vsx # only Open VSX extensions
ext install --marketplace microsoft # only Microsoft extensions
ext install --dry-run               # print what would be installed
```

### `ext update`

Shortcut for running `ext generate` followed by `ext install`.

```bash
ext update
```

### `ext export`

Export the registry to a file.

```bash
ext export registry.toml
ext export registry.json --format json
ext export registry.csv  --format csv
```

### `ext import`

Import extensions from an export file.

```bash
ext import registry.toml
```

## Configuration

All configuration lives in `~/.config/ext-tool/config.toml` and can also be
set via environment variables prefixed with `EXT_`.

| Key | Default | Description |
|-----|---------|-------------|
| `helper` | `cursor` | VS Code-compatible CLI binary |
| `extensions_file` | `~/.config/ext-tool/extensions.toml` | Registry path |
| `concurrency` | `10` | Max concurrent Open VSX requests |
| `debug` | `false` | Enable debug logging |
