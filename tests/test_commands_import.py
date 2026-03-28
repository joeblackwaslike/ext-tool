"""CLI integration tests — ext import."""

from pathlib import Path

from typer.testing import CliRunner

from ext_tool.cli import app
from ext_tool.models import ExportFormat, Extension, ExtensionRegistry, Marketplace

runner = CliRunner()


def _make_registry(tmp_path: Path) -> Path:
    """Write a minimal registry file and return its path."""
    reg = ExtensionRegistry(
        extensions=[
            Extension(
                id="charliermarsh.ruff",
                name="Ruff",
                publisher="charliermarsh",
                marketplace=Marketplace.OPEN_VSX,
                version="1.0.0",
            ),
            Extension(
                id="ms-python.python",
                name="Python",
                publisher="ms-python",
                marketplace=Marketplace.MICROSOFT,
                version="2.0.0",
            ),
        ]
    )
    reg_path = tmp_path / "extensions.toml"
    reg.save(reg_path)
    return reg_path


def test_import_json_merge(tmp_path: Path) -> None:
    reg_path = _make_registry(tmp_path)

    new_ext = Extension(
        id="tamasfe.even-better-toml",
        name="Even Better TOML",
        publisher="tamasfe",
        marketplace=Marketplace.OPEN_VSX,
        version="0.21.2",
    )
    import_src = tmp_path / "new.json"
    ExtensionRegistry(extensions=[new_ext]).export(import_src, ExportFormat.JSON)

    result = runner.invoke(
        app,
        [
            "--extensions-file",
            str(reg_path),
            "import",
            str(import_src),
            "--merge",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.output

    loaded = ExtensionRegistry.load(reg_path)
    assert loaded.by_id("tamasfe.even-better-toml") is not None
    assert loaded.by_id("charliermarsh.ruff") is not None  # original preserved


def test_import_replace(tmp_path: Path) -> None:
    reg_path = _make_registry(tmp_path)

    new_ext = Extension(
        id="tamasfe.even-better-toml",
        name="Even Better TOML",
        publisher="tamasfe",
        marketplace=Marketplace.OPEN_VSX,
        version="0.21.2",
    )
    import_src = tmp_path / "new.json"
    ExtensionRegistry(extensions=[new_ext]).export(import_src, ExportFormat.JSON)

    # --replace prompts for confirmation; send "y\n" as stdin
    result = runner.invoke(
        app,
        [
            "--extensions-file",
            str(reg_path),
            "import",
            str(import_src),
            "--replace",
        ],
        input="y\n",
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.output

    loaded = ExtensionRegistry.load(reg_path)
    assert loaded.by_id("tamasfe.even-better-toml") is not None
    assert loaded.by_id("charliermarsh.ruff") is None  # replaced, not merged
