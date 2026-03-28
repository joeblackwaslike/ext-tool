"""CLI integration tests — ext install."""

from pathlib import Path

from typer.testing import CliRunner

from ext_tool.cli import app
from ext_tool.models import Extension, ExtensionRegistry, Marketplace

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


def test_install_missing_registry(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["--extensions-file", str(tmp_path / "missing.toml"), "install"],
    )
    assert result.exit_code != 0
    assert "generate" in result.output.lower() or "not found" in result.output.lower()


def test_install_dry_run(tmp_path: Path) -> None:
    reg_path = _make_registry(tmp_path)
    result = runner.invoke(
        app,
        ["--extensions-file", str(reg_path), "install", "--dry-run"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.output
    assert "dry run" in result.output.lower()


def test_install_invalid_marketplace_flag(tmp_path: Path) -> None:
    reg_path = _make_registry(tmp_path)
    result = runner.invoke(
        app,
        ["--extensions-file", str(reg_path), "install", "--marketplace", "invalid"],
    )
    assert result.exit_code != 0
