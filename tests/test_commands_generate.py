"""CLI integration tests — ext generate."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ext_tool.cli import app
from ext_tool.models import Extension, ExtensionRegistry, Marketplace

runner = CliRunner()


def test_generate_dry_run(fake_extensions_dir: Path, tmp_path: Path) -> None:
    """--dry-run should print the TOML but not write the file."""
    out_file = tmp_path / "extensions.toml"

    fake_registry = ExtensionRegistry(
        extensions=[
            Extension(
                id="charliermarsh.ruff",
                name="Ruff",
                publisher="charliermarsh",
                marketplace=Marketplace.OPEN_VSX,
                version="1.0.0",
            )
        ]
    )

    with (
        patch(
            "ext_tool.commands.generate.resolve_extensions_dir",
            return_value=fake_extensions_dir,
        ),
        patch(
            "ext_tool.commands.generate.scan_local_extensions",
            return_value=[],
        ),
        patch(
            "ext_tool.commands.generate.classify_extensions",
            return_value=fake_registry,
        ),
    ):
        result = runner.invoke(
            app,
            ["--extensions-file", str(out_file), "generate", "--dry-run"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0, result.output
    assert not out_file.exists(), "dry-run should not write the file"
