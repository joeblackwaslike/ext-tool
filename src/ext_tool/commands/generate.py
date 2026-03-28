"""ext generate — scan installed extensions and write extensions.toml."""

import asyncio
import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from ext_tool.config import AppConfig
from ext_tool.marketplace import classify_extensions
from ext_tool.models import ExtensionRegistry, Marketplace
from ext_tool.scanner import resolve_extensions_dir, scan_local_extensions

logger = logging.getLogger(__name__)
console = Console()
app = typer.Typer(help="Scan installed extensions and write [bold]extensions.toml[/].")


@app.callback(invoke_without_command=True)
def generate(
    ctx: typer.Context,
    *,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print what would be written without saving."),
    ] = False,
) -> None:
    """Scan the local extensions directory and write the registry.

    Classifies each extension via Open VSX, writing to
    [dim]~/.config/ext-tool/extensions.toml[/].
    """
    cfg: AppConfig = ctx.obj["config"]

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]ext generate[/]  —  building extension registry",
            border_style="cyan",
        )
    )
    console.print()

    ext_dir = _resolve_dir(cfg)
    console.print(f"[dim]Scanning:[/] {ext_dir}")

    raw = _scan_dir(ext_dir)
    console.print(f"[dim]Found[/] [bold]{len(raw)}[/] installed extensions\n")

    registry = _classify(raw, cfg.concurrency)

    _print_table(registry)

    if dry_run:
        console.print(
            Panel(
                registry.to_toml(),
                title="[dim]dry-run — extensions.toml[/]",
                border_style="dim",
            )
        )
        console.print("[dim]Dry run — nothing written.[/]")
    else:
        registry.save(cfg.extensions_file)
        console.print(f"[bold green]✓[/] Registry written → [bold]{cfg.extensions_file}[/]")
    console.print()


def _resolve_dir(cfg: AppConfig) -> Path:
    """Resolve the extensions directory from config, exiting on failure."""
    try:
        return resolve_extensions_dir(cfg.helper, cfg.extensions_dir)
    except FileNotFoundError as exc:
        console.print(f"[bold red]Error:[/] {exc}")
        raise typer.Exit(1) from exc


def _scan_dir(ext_dir: Path) -> list[dict[str, str]]:
    """Scan the extensions directory, exiting on failure."""
    try:
        return scan_local_extensions(ext_dir)
    except FileNotFoundError as exc:
        console.print(f"[bold red]Error:[/] {exc}")
        raise typer.Exit(1) from exc


def _classify(raw: list[dict[str, str]], concurrency: int) -> ExtensionRegistry:
    """Run the async Open VSX classification with a progress bar."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Checking Open VSX...", total=len(raw))
        registry = asyncio.run(classify_extensions(raw, concurrency=concurrency))
        progress.update(task, completed=len(raw))
    return registry


def _print_table(registry: ExtensionRegistry) -> None:
    """Print the extension summary table and marketplace counts."""
    open_vsx_count = sum(
        1 for ext in registry.extensions if ext.marketplace == Marketplace.OPEN_VSX
    )
    ms_count = len(registry.extensions) - open_vsx_count

    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
    table.add_column("ID", style="white")
    table.add_column("Name", style="dim white")
    table.add_column("Marketplace", justify="right")

    for ext in registry.extensions:
        market_str = (
            "[green]open-vsx[/]"
            if ext.marketplace == Marketplace.OPEN_VSX
            else "[yellow]microsoft[/]"
        )
        table.add_row(ext.id, ext.name, market_str)

    console.print(table)
    console.print()
    console.print(
        f"  [green]open-vsx[/]  {open_vsx_count}    "
        f"[yellow]microsoft[/]  {ms_count}    "
        f"[bold]total[/]  {len(registry.extensions)}"
    )
    console.print()
