# ext-tool — CLAUDE.md

This file provides context for Claude Code and other AI coding assistants working in this repo.

## Project overview

`ext-tool` is a Python CLI (`ext`) for managing VS Code / Cursor extensions via a TOML registry.
It is published to PyPI and intended for installation via `uv tool install ext-tool` or `pipx install ext-tool`.

## Tech stack

| Layer | Choice |
|---|---|
| Python | 3.12+ |
| Package manager | uv |
| Build backend | hatchling |
| CLI framework | typer + rich |
| HTTP | httpx (async) |
| Config / models | pydantic-settings + pydantic v2 |
| TOML write | tomli-w (read via stdlib tomllib) |
| Linting / formatting | ruff |
| Type checking | mypy (strict) |
| Testing | pytest + pytest-asyncio + respx |

## Repo layout

```
src/ext_tool/
  __init__.py       package version
  cli.py            typer app + subcommand registration
  config.py         AppConfig (pydantic-settings), XDG config dir helpers
  models.py         Extension pydantic model, ExtensionRegistry
  marketplace.py    async Open VSX check, MS VSIX download helpers
  scanner.py        local extensions.json + package.json reader
  installer.py      install_open_vsx(), install_microsoft()
  exporter.py       export to TOML/JSON/CSV
  importer.py       import from export file
  logging.py        rich logging setup, debug log file handler
  commands/
    generate.py     ext generate
    install.py      ext install
    update.py       ext update
    export.py       ext export
    import_.py      ext import
    completions.py  ext completions
tests/
  conftest.py
  test_scanner.py
  test_marketplace.py
  test_models.py
  test_commands.py
```

## Key conventions

- All async I/O uses `asyncio.run()` at the CLI boundary — commands call `asyncio.run(async_main())`.
- `AppConfig` is a singleton loaded once per invocation; subcommands receive it via typer callback context.
- The registry file is always `~/.config/ext-tool/extensions.toml`; the user can override with `--extensions-file`.
- `--debug` / `EXT_DEBUG=1` writes a log to `./ext.debug-{6hexchars}.log`.
- Extension IDs are always stored and compared lowercase.
- Never write to cwd without user consent (all state goes to `~/.config/ext-tool/`).

## Common tasks

```bash
uv run ext generate          # regenerate registry
uv run ext install           # install from registry
uv run pytest                # run tests
uv run ruff check src tests  # lint
uv run mypy src              # type check
```
