"""ext export — export the registry to TOML, JSON, or CSV."""

import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from ext_tool.config import AppConfig
from ext_tool.models import ExportFormat, ExtensionRegistry, _infer_format

logger = logging.getLogger(__name__)
console = Console()

_FORMAT_CHOICES: tuple[str, ...] = tuple(fmt.value for fmt in ExportFormat)
_FORMAT_CHOICES_STR = " | ".join(_FORMAT_CHOICES)
_FORMAT_CHOICES_CSV = ", ".join(_FORMAT_CHOICES)


def export_cmd(
    ctx: typer.Context,
    output: Annotated[
        Path,
        typer.Argument(help="Destination file path."),
    ],
    fmt: Annotated[
        str | None,
        typer.Option(
            "--format",
            "-f",
            help=f"Export format: [dim]{_FORMAT_CHOICES_STR}[/]  "
            "(inferred from file suffix if omitted)",
            show_default=False,
        ),
    ] = None,
) -> None:
    """Export the extension registry to a file.

    The format is inferred from the file suffix when [bold]--format[/] is omitted:
    [dim].toml → toml   .json → json   .csv → csv[/]
    """
    cfg: AppConfig = ctx.obj["config"]
    export_fmt = _resolve_export_format(fmt, output)
    _check_registry_exists(cfg)
    registry = ExtensionRegistry.load(cfg.extensions_file)

    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]ext export[/]  —  {len(registry.extensions)} extensions "
            f"→ [bold]{output}[/] ([dim]{export_fmt}[/])",
            border_style="cyan",
        )
    )
    console.print()

    try:
        registry.export(output, export_fmt)
    except Exception as exc:
        logger.debug("Export failed", exc_info=True)
        console.print(f"[bold red]Error:[/] {exc}")
        raise typer.Exit(1) from exc

    console.print(
        f"[bold green]✓[/] Exported [bold]{len(registry.extensions)}[/] extensions "
        f"→ [bold]{output}[/]"
    )
    console.print()


def _resolve_export_format(fmt: str | None, output: Path) -> ExportFormat:
    """Resolve the export format from the --format flag or file suffix."""
    if fmt is None:
        try:
            return _infer_format(output)
        except ValueError as exc:
            console.print(f"[bold red]Error:[/] {exc}")
            raise typer.Exit(1) from exc
    if fmt not in _FORMAT_CHOICES:
        console.print(f"[bold red]Error:[/] --format must be one of: {_FORMAT_CHOICES_CSV}")
        raise typer.Exit(1)
    return ExportFormat(fmt)


def _check_registry_exists(cfg: AppConfig) -> None:
    """Exit with an error message if the registry file does not exist."""
    if cfg.extensions_file.exists():
        return
    console.print(
        f"[bold red]Error:[/] Registry not found at [bold]{cfg.extensions_file}[/].\n"
        "Run [bold cyan]ext generate[/] first."
    )
    raise typer.Exit(1)
