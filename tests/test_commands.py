"""CLI integration tests — top-level CLI flags."""

from typer.testing import CliRunner

from ext_tool.cli import app

runner = CliRunner()


def test_version_flag() -> None:
    outcome = runner.invoke(app, ["--version"])
    assert outcome.exit_code == 0
    assert "ext-tool" in outcome.output
