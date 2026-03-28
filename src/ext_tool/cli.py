"""Main Typer application — global flags, subcommand registration."""

from importlib.metadata import version as _pkg_version
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from ext_tool.config import AppConfig, ensure_config_dir
from ext_tool.logging import setup_logging

console = Console()

app = typer.Typer(
    name="ext",
    help="[bold cyan]ext[/] — VS Code / Cursor extension manager.",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)

# Sub-apps: commands that are group roots or have no positional arguments
from ext_tool.commands import generate, install, update  # noqa: E402

app.add_typer(generate.app, name="generate")
app.add_typer(install.app, name="install")
app.add_typer(update.app, name="update")

# Direct registration: commands with positional args must NOT use add_typer,
# which would make Typer treat those args as nested subcommand names.
from ext_tool.commands.completions import completions_cmd  # noqa: E402
from ext_tool.commands.export import export_cmd  # noqa: E402
from ext_tool.commands.import_cmd import import_cmd  # noqa: E402

app.command("export")(export_cmd)
app.command("import")(import_cmd)
app.command("completions")(completions_cmd)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    *,
    version: Annotated[
        bool,
        typer.Option("--version", "-v", help="Show version and exit.", is_eager=True),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Enable debug logging.", envvar="EXT_DEBUG"),
    ] = False,
    helper: Annotated[
        str | None,
        typer.Option(
            "--helper",
            help="VS Code-compatible CLI to use  [dim](default: cursor)[/]",
            show_default=False,
        ),
    ] = None,
    extensions_file: Annotated[
        Path | None,
        typer.Option(
            "--extensions-file",
            help="Path to extensions.toml  [dim](default: ~/.config/ext-tool/extensions.toml)[/]",
            show_default=False,
        ),
    ] = None,
) -> None:
    r"""[bold cyan]ext[/] — manage VS Code / Cursor extensions from a TOML registry.

    \b
    Configuration is stored in [dim]~/.config/ext-tool/[/]

    Run [bold]ext COMMAND --help[/] for command-specific options.
    """
    if version:
        console.print(f"[bold cyan]ext-tool[/] [green]{_pkg_version('ext-tool')}[/]")
        raise typer.Exit

    log_path = setup_logging(debug=debug)

    ensure_config_dir()
    cfg = AppConfig.load()
    if helper is not None:
        cfg.helper = helper
    if extensions_file is not None:
        cfg.extensions_file = extensions_file
    cfg.debug = debug

    ctx.ensure_object(dict)
    ctx.obj["config"] = cfg

    if debug and log_path:
        console.print(f"[dim]Debug log → [bold]{log_path}[/bold][/dim]")
