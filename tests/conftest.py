"""Shared fixtures for ext-tool tests."""

import json
from pathlib import Path

import pytest

from ext_tool.config import AppConfig
from ext_tool.models import Extension, ExtensionRegistry, Marketplace

_KEY_ID = "id"
_KEY_VERSION = "version"
_KEY_DESCRIPTION = "description"


@pytest.fixture(autouse=True)
def isolate_http_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Redirect the Open VSX disk cache to a per-test temp dir.

    Without this, a real ``ext generate`` run would leave cache entries that
    override mocked responses in subsequent test runs.
    """
    from ext_tool import marketplace as marketplace_mod

    monkeypatch.setattr(marketplace_mod, "_OPEN_VSX_CACHE_FILE", tmp_path / "open-vsx.json")


@pytest.fixture
def fake_extensions_dir(tmp_path: Path) -> Path:
    """Create a minimal fake VS Code extensions directory."""
    ext_dir = tmp_path / "extensions"
    ext_dir.mkdir()

    entries = [
        {
            _KEY_ID: "charliermarsh.ruff",
            "display_name": "Ruff",
            _KEY_DESCRIPTION: "Fast Python linter.",
            "publisher": "charliermarsh",
            "publisher_display_name": "Astral Software",
            _KEY_VERSION: "2026.1.0",
        },
        {
            _KEY_ID: "ms-python.python",
            "display_name": "Python",
            _KEY_DESCRIPTION: "Python language support.",
            "publisher": "ms-python",
            "publisher_display_name": "Microsoft",
            _KEY_VERSION: "2026.5.0",
        },
    ]

    index = []
    for entry in entries:
        rel = f"{entry[_KEY_ID]}-{entry[_KEY_VERSION]}"
        pkg_dir = ext_dir / rel
        pkg_dir.mkdir()
        (pkg_dir / "package.json").write_text(
            json.dumps({
                "displayName": entry["display_name"],
                _KEY_DESCRIPTION: entry[_KEY_DESCRIPTION],
            })
        )
        index.append({
            "identifier": {_KEY_ID: entry[_KEY_ID]},
            _KEY_VERSION: entry[_KEY_VERSION],
            "relativeLocation": rel,
            "metadata": {
                "publisherDisplayName": entry["publisher_display_name"],
                "installedTimestamp": 1000,
            },
        })

    (ext_dir / "extensions.json").write_text(json.dumps(index))
    return ext_dir


@pytest.fixture
def sample_registry() -> ExtensionRegistry:
    """A small in-memory registry for serialisation tests."""
    return ExtensionRegistry(
        extensions=[
            Extension(
                id="charliermarsh.ruff",
                name="Ruff",
                description="Fast Python linter.",
                publisher="charliermarsh",
                publisher_display_name="Astral Software",
                version="2026.1.0",
                marketplace=Marketplace.OPEN_VSX,
            ),
            Extension(
                id="ms-python.python",
                name="Python",
                description="Python language support.",
                publisher="ms-python",
                publisher_display_name="Microsoft",
                version="2026.5.0",
                marketplace=Marketplace.MICROSOFT,
            ),
        ]
    )


@pytest.fixture
def app_config(tmp_path: Path) -> AppConfig:
    """AppConfig pointing at a temporary extensions file."""
    return AppConfig(
        helper="code-insiders",
        extensions_file=tmp_path / "extensions.toml",
        concurrency=2,
    )
