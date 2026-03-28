"""CLI integration tests — ext export."""

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


def test_export_toml(tmp_path: Path) -> None:
    reg_path = _make_registry(tmp_path)
    out = tmp_path / "out.toml"
    result = runner.invoke(
        app,
        ["--extensions-file", str(reg_path), "export", str(out)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.output
    assert out.exists()
    assert "charliermarsh.ruff" in out.read_text()


def test_export_json(tmp_path: Path) -> None:
    reg_path = _make_registry(tmp_path)
    out = tmp_path / "out.json"
    result = runner.invoke(
        app,
        ["--extensions-file", str(reg_path), "export", str(out), "--format", "json"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_export_csv(tmp_path: Path) -> None:
    reg_path = _make_registry(tmp_path)
    out = tmp_path / "out.csv"
    result = runner.invoke(
        app,
        ["--extensions-file", str(reg_path), "export", str(out)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_export_unknown_format_errors(tmp_path: Path) -> None:
    reg_path = _make_registry(tmp_path)
    out = tmp_path / "out.xyz"
    result = runner.invoke(
        app,
        ["--extensions-file", str(reg_path), "export", str(out)],
    )
    assert result.exit_code != 0
