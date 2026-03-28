"""ext import — import an exported registry file."""

import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from ext_tool.config import AppConfig
from ext_tool.models import ExportFormat, ExtensionRegistry, load_from_export

logger = logging.getLogger(__name__)
console = Console()

_FORMAT_CHOICES: tuple[str, ...] = tuple(fmt.value for fmt in ExportFormat)
_FORMAT_CHOICES_DISPLAY = " | ".join(_FORMAT_CHOICES)


def import_cmd(
    ctx: typer.Context,
    source: Annotated[
        Path,
        typer.Argument(help="Path to the file to import."),
    ],
    fmt: Annotated[
        str | None,
        typer.Option(
            "--format",
            "-f",
            help=f"Import format: [dim]{_FORMAT_CHOICES_DISPLAY}[/]  "
            "(inferred from suffix if omitted)",
            show_default=False,
        ),
    ] = None,
    *,
    merge: Annotated[
        bool,
        typer.Option(
            "--merge/--replace",
            help="Merge with existing registry (imported wins on conflict) or fully replace it.",
        ),
    ] = True,
) -> None:
    """Import an exported registry file.

    By default entries are [bold]merged[/] — the imported file wins on conflict.
    Pass [bold]--replace[/] to overwrite the registry entirely.
    """
    cfg: AppConfig = ctx.obj["config"]

    _validate_source_and_format(source, fmt)

    import_fmt: ExportFormat | None = None if fmt is None else ExportFormat(fmt)

    console.print()
    action_label = "[cyan]merge[/]" if merge else "[yellow]replace[/]"
    console.print(
        Panel.fit(
            f"[bold cyan]ext import[/]  —  {source}  ({action_label})",
            border_style="cyan",
        )
    )
    console.print()

    incoming = _load_incoming(source, import_fmt)

    console.print(
        f"[dim]Loaded[/] [bold]{len(incoming.extensions)}[/] extensions from import file."
    )

    if not merge and cfg.extensions_file.exists():
        confirmed = typer.confirm(
            f"  Replace existing registry at {cfg.extensions_file}?",
            default=False,
        )
        if not confirmed:
            console.print("[dim]Aborted.[/]")
            raise typer.Exit

    final = _apply_merge(cfg, incoming, merge=merge)

    final.save(cfg.extensions_file)
    console.print(f"[bold green]✓[/] Registry saved → [bold]{cfg.extensions_file}[/]")
    console.print()


def _validate_source_and_format(source: Path, fmt: str | None) -> None:
    """Validate source file exists and format is recognised; exit on failure."""
    if not source.exists():
        console.print(f"[bold red]Error:[/] File not found: [bold]{source}[/]")
        raise typer.Exit(1)
    format_list = ", ".join(_FORMAT_CHOICES)
    if fmt is not None and fmt not in _FORMAT_CHOICES:
        console.print(f"[bold red]Error:[/] --format must be one of: {format_list}")
        raise typer.Exit(1)


def _load_incoming(source: Path, import_fmt: ExportFormat | None) -> ExtensionRegistry:
    """Load an ExtensionRegistry from an export file; exit on parse failure."""
    try:
        return load_from_export(source, import_fmt)
    except Exception as exc:
        logger.debug("Import parse failed", exc_info=True)
        console.print(f"[bold red]Error:[/] Could not parse import file: {exc}")
        raise typer.Exit(1) from exc


def _apply_merge(
    cfg: AppConfig,
    incoming: ExtensionRegistry,
    *,
    merge: bool,
) -> ExtensionRegistry:
    """Merge incoming registry into existing if merge=True, else return incoming."""
    if merge and cfg.extensions_file.exists():
        existing = ExtensionRegistry.load(cfg.extensions_file)
        merged = existing.merge(incoming)
        console.print(
            f"[dim]Merged:[/] {len(existing.extensions)} existing + "
            f"{len(incoming.extensions)} imported → "
            f"[bold]{len(merged.extensions)}[/] total"
        )
        return merged
    return incoming
