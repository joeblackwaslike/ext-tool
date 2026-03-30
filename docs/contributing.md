# Contributing

## Development setup

**Requirements:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/joeblackwaslike/ext-tool.git
cd ext-tool
uv sync
```

Install pre-commit hooks:

```bash
uv run pre-commit install
```

Verify the setup works:

```bash
uv run ext --help
```

---

## Running tests

```bash
uv run pytest
```

With coverage:

```bash
uv run pytest --cov=ext_tool --cov-report=term-missing
```

HTTP calls are mocked via [respx](https://lundberg.github.io/respx/), so no network
access is required.

---

## Linting and type checking

Run all checks at once (same as CI):

```bash
make check
```

Individually:

```bash
uv run ruff check src tests   # fast linter
uv run ruff format src tests  # formatter
uv run mypy src               # type checker (strict mode)
```

Pre-commit runs ruff, mypy, and flake8 (wemake-python-styleguide) on every commit.

---

## Project layout

```
src/ext_tool/
├── __init__.py          Package version
├── cli.py               Typer app + global callback
├── config.py            AppConfig (pydantic-settings)
├── models.py            Extension, ExtensionRegistry, ExportFormat
├── marketplace.py       Open VSX API + VSIX install helpers
├── scanner.py           Local extensions.json reader
├── cache.py             Disk-backed TTL cache
├── logging.py           Rich logging + debug file handler
└── commands/
    ├── generate.py      ext generate
    ├── install.py       ext install
    ├── update.py        ext update
    ├── export.py        ext export
    ├── import_cmd.py    ext import
    └── completions.py   ext completions

tests/
├── conftest.py
├── test_commands*.py
├── test_marketplace.py
├── test_models.py
└── test_scanner.py
```

---

## Code style

| Concern | Tool | Config |
| --- | --- | --- |
| Formatting | ruff-format | `pyproject.toml` |
| Linting | ruff | `pyproject.toml` |
| Style enforcement | wemake-python-styleguide | `setup.cfg` |
| Type checking | mypy (strict) | `pyproject.toml` |
| Docstrings | Google style | `pyproject.toml` |

Key conventions:

- Line length: **100 characters**
- All async I/O uses `asyncio.run()` at the CLI boundary only
- `AppConfig` is loaded once per invocation and passed through Typer's context object
- Extension IDs are always stored and compared **lowercase**
- State goes to `~/.config/ext-tool/` — never write to `cwd` without user consent

---

## Making a release

1. Merge all changes to `main`
2. On GitHub: **Releases → Draft a new release → Create a new tag** (e.g. `1.0.0`)
3. Click **Publish release**

The `release-main` workflow automatically:

- Bumps the version in `pyproject.toml` to match the tag
- Builds the source distribution and wheel
- Publishes to PyPI via Twine
- Deploys updated documentation to GitHub Pages
