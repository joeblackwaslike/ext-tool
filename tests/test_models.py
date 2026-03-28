"""Tests for ext_tool.models — Extension, ExtensionRegistry serialisation."""

import json
from pathlib import Path

import pytest

from ext_tool.models import (
    ExportFormat,
    Extension,
    ExtensionRegistry,
    Marketplace,
    _infer_format,
    load_from_export,
)


def test_extension_id_is_lowercased() -> None:
    ext = Extension(
        id="MS-Python.Python",
        name="Python",
        publisher="MS-Python",
        marketplace=Marketplace.MICROSOFT,
    )
    assert ext.id == "ms-python.python"
    assert ext.publisher == "ms-python"


def test_extension_ext_name_property() -> None:
    ext = Extension(
        id="ms-python.python",
        name="Python",
        publisher="ms-python",
        marketplace=Marketplace.MICROSOFT,
    )
    assert ext.ext_name == "python"


# ── TOML round-trip ────────────────────────────────────────────────────────────


def test_registry_toml_roundtrip(sample_registry: ExtensionRegistry, tmp_path: Path) -> None:
    path = tmp_path / "extensions.toml"
    sample_registry.save(path)
    loaded = ExtensionRegistry.load(path)
    assert len(loaded.extensions) == len(sample_registry.extensions)
    assert {ext.id for ext in loaded.extensions} == {ext.id for ext in sample_registry.extensions}


def test_registry_toml_contains_header_comment(
    sample_registry: ExtensionRegistry, tmp_path: Path
) -> None:
    path = tmp_path / "extensions.toml"
    sample_registry.save(path)
    toml_text = path.read_text()
    assert "# VS Code / Cursor extension registry" in toml_text
    assert "open-vsx" in toml_text


# ── JSON export / import ───────────────────────────────────────────────────────


def test_export_json(sample_registry: ExtensionRegistry, tmp_path: Path) -> None:
    path = tmp_path / "out.json"
    sample_registry.export(path, ExportFormat.JSON)
    registry_data = json.loads(path.read_text())
    assert len(registry_data["extensions"]) == 2


def test_from_export_json(sample_registry: ExtensionRegistry, tmp_path: Path) -> None:
    path = tmp_path / "out.json"
    sample_registry.export(path, ExportFormat.JSON)
    loaded = load_from_export(path)
    assert {ext.id for ext in loaded.extensions} == {ext.id for ext in sample_registry.extensions}


# ── CSV export / import ────────────────────────────────────────────────────────


def test_export_csv(sample_registry: ExtensionRegistry, tmp_path: Path) -> None:
    path = tmp_path / "out.csv"
    sample_registry.export(path, ExportFormat.CSV)
    lines = path.read_text().splitlines()
    assert len(lines) == 3  # header + 2 data rows


def test_from_export_csv(sample_registry: ExtensionRegistry, tmp_path: Path) -> None:
    path = tmp_path / "out.csv"
    sample_registry.export(path, ExportFormat.CSV)
    loaded = load_from_export(path)
    assert {ext.id for ext in loaded.extensions} == {ext.id for ext in sample_registry.extensions}


def test_export_csv_empty_registry(tmp_path: Path) -> None:
    empty = ExtensionRegistry(extensions=[])
    path = tmp_path / "out.csv"
    empty.export(path, ExportFormat.CSV)
    assert path.read_text() == ""


# ── Merge ──────────────────────────────────────────────────────────────────────


def test_merge_incoming_wins_on_conflict(sample_registry: ExtensionRegistry) -> None:
    updated = Extension(
        id="charliermarsh.ruff",
        name="Ruff Updated",
        publisher="charliermarsh",
        marketplace=Marketplace.OPEN_VSX,
        version="9999.0.0",
    )
    incoming = ExtensionRegistry(extensions=[updated])
    merged = sample_registry.merge(incoming)
    ruff = merged.by_id("charliermarsh.ruff")
    assert ruff is not None
    assert ruff.version == "9999.0.0"
    assert len(merged.extensions) == 2  # ms-python.python preserved


def test_merge_adds_new_extension(sample_registry: ExtensionRegistry) -> None:
    new_ext = Extension(
        id="tamasfe.even-better-toml",
        name="Even Better TOML",
        publisher="tamasfe",
        marketplace=Marketplace.OPEN_VSX,
        version="0.21.2",
    )
    incoming = ExtensionRegistry(extensions=[new_ext])
    merged = sample_registry.merge(incoming)
    assert len(merged.extensions) == 3
    assert merged.by_id("tamasfe.even-better-toml") is not None


# ── by_id ──────────────────────────────────────────────────────────────────────


def test_by_id_case_insensitive(sample_registry: ExtensionRegistry) -> None:
    assert sample_registry.by_id("CHARLIERMARSH.RUFF") is not None


def test_by_id_missing_returns_none(sample_registry: ExtensionRegistry) -> None:
    assert sample_registry.by_id("does-not.exist") is None


# ── filter_marketplace ─────────────────────────────────────────────────────────


def test_filter_marketplace_open_vsx(sample_registry: ExtensionRegistry) -> None:
    filtered = sample_registry.filter_marketplace(Marketplace.OPEN_VSX)
    assert all(ext.marketplace == Marketplace.OPEN_VSX for ext in filtered)
    assert len(filtered) == 1


def test_filter_marketplace_microsoft(sample_registry: ExtensionRegistry) -> None:
    filtered = sample_registry.filter_marketplace(Marketplace.MICROSOFT)
    assert all(ext.marketplace == Marketplace.MICROSOFT for ext in filtered)
    assert len(filtered) == 1


# ── Format inference ───────────────────────────────────────────────────────────


def test_infer_format_toml() -> None:
    assert _infer_format(Path("extensions.toml")) == ExportFormat.TOML


def test_infer_format_json() -> None:
    assert _infer_format(Path("extensions.json")) == ExportFormat.JSON


def test_infer_format_csv() -> None:
    assert _infer_format(Path("extensions.csv")) == ExportFormat.CSV


def test_infer_format_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Cannot infer"):
        _infer_format(Path("extensions.xyz"))
