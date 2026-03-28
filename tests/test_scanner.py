"""Tests for ext_tool.scanner."""

import json
from pathlib import Path

import pytest

from ext_tool.scanner import resolve_extensions_dir, scan_local_extensions


def test_scan_returns_both_extensions(fake_extensions_dir: Path) -> None:
    found = scan_local_extensions(fake_extensions_dir)
    ids = {entry["id"] for entry in found}
    assert ids == {"charliermarsh.ruff", "ms-python.python"}


def test_scan_reads_display_name_from_package_json(fake_extensions_dir: Path) -> None:
    found = scan_local_extensions(fake_extensions_dir)
    index = {entry["id"]: entry for entry in found}
    assert index["charliermarsh.ruff"]["display_name"] == "Ruff"
    assert index["ms-python.python"]["display_name"] == "Python"


def test_scan_reads_description_from_package_json(fake_extensions_dir: Path) -> None:
    found = scan_local_extensions(fake_extensions_dir)
    index = {entry["id"]: entry for entry in found}
    assert index["charliermarsh.ruff"]["description"] == "Fast Python linter."


def test_scan_deduplicates_same_id(fake_extensions_dir: Path) -> None:
    """If extensions.json has two entries for the same id, keep only the newest."""
    index_file = fake_extensions_dir / "extensions.json"
    existing = json.loads(index_file.read_text())
    dup = dict(existing[0])
    dup["metadata"] = {**dup.get("metadata", {}), "installedTimestamp": 0}
    index_file.write_text(json.dumps([*existing, dup]))

    found = scan_local_extensions(fake_extensions_dir)
    ids = [entry["id"] for entry in found]
    assert ids.count("charliermarsh.ruff") == 1


def test_scan_raises_when_extensions_json_missing(tmp_path: Path) -> None:
    ext_dir = tmp_path / "extensions"
    ext_dir.mkdir()
    with pytest.raises(FileNotFoundError, match="extensions.json"):
        scan_local_extensions(ext_dir)


def test_resolve_extensions_dir_raises_on_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        resolve_extensions_dir("code", override=tmp_path / "nonexistent")


def test_resolve_extensions_dir_uses_override(fake_extensions_dir: Path) -> None:
    resolved = resolve_extensions_dir("code", override=fake_extensions_dir)
    assert resolved == fake_extensions_dir
