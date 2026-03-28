"""CLI integration tests — ext completions."""

from typer.testing import CliRunner

from ext_tool.cli import app

runner = CliRunner()


def test_completions_zsh() -> None:
    result = runner.invoke(app, ["completions", "zsh"], catch_exceptions=False)
    assert result.exit_code == 0, result.output
    assert "compdef _ext ext" in result.output


def test_completions_bash() -> None:
    result = runner.invoke(app, ["completions", "bash"], catch_exceptions=False)
    assert result.exit_code == 0, result.output
    assert "_ext_complete" in result.output


def test_completions_fish() -> None:
    result = runner.invoke(app, ["completions", "fish"], catch_exceptions=False)
    assert result.exit_code == 0, result.output
    assert "complete -c ext" in result.output


def test_completions_show_install_zsh() -> None:
    result = runner.invoke(app, ["completions", "zsh", "--show-install"], catch_exceptions=False)
    assert result.exit_code == 0, result.output
    assert "zshrc" in result.output.lower() or "eval" in result.output
