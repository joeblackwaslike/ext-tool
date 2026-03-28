"""ext install — install extensions from the registry."""

import logging
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ext_tool.config import AppConfig
from ext_tool.marketplace import install_extension
from ext_tool.models import Extension, ExtensionRegistry, Marketplace

logger = logging.getLogger(__name__)
console = Console()
app = typer.Typer(help="Install extensions from [bold]extensions.toml[/].")

_MARKET_CHOICES: tuple[str, ...] = ("all", "open-vsx", "microsoft")
_MARKET_CHOICES_CSV = ", ".join(_MARKET_CHOICES)

_FailList = list[tuple[Extension, str]]


def _market_label(ext: Extension) -> str:
    """Return a Rich-formatted marketplace label for an extension."""
    if ext.marketplace == Marketplace.OPEN_VSX:
        return "[green]open-vsx[/]"
    return "[yellow]microsoft[/]"


@app.callback(invoke_without_command=True)
def install(
    ctx: typer.Context,
    marketplace: Annotated[
        str,
        typer.Option(
            "--marketplace",
            "-m",
            help="Which marketplace entries to install: [dim]all | open-vsx | microsoft[/]",
        ),
    ] = "all",
    *,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print what would be installed without running."),
    ] = False,
) -> None:
    """Install all (or filtered) extensions from the registry.

    Routes each extension to the correct marketplace automatically.
    """
    _validate_marketplace(marketplace)
    cfg: AppConfig = ctx.obj["config"]
    _print_install_header(marketplace, cfg.helper)
    registry = _load_registry(cfg)
    extensions = _filter_extensions(registry, marketplace)
    if not extensions:
        console.print("[dim]No extensions match the current filter.[/]")
        raise typer.Exit
    console.print(f"[dim]Installing[/] [bold]{len(extensions)}[/] extensions…\n")
    table, installed, failed = _run_install_loop(extensions, cfg, dry_run=dry_run)
    console.print(table)
    console.print()
    _print_summary(dry_run=dry_run, extensions=extensions, installed=installed, failed=failed)
    console.print()


def _validate_marketplace(marketplace: str) -> None:
    """Exit with an error if the marketplace value is not valid."""
    if marketplace not in _MARKET_CHOICES:
        console.print(f"[bold red]Error:[/] --marketplace must be one of: {_MARKET_CHOICES_CSV}")
        raise typer.Exit(1)


def _print_install_header(marketplace: str, helper: str) -> None:
    """Print the install command header panel."""
    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]ext install[/]  —  marketplace=[bold]{marketplace}[/]  "
            f"helper=[bold]{helper}[/]",
            border_style="cyan",
        )
    )
    console.print()


def _load_registry(cfg: AppConfig) -> ExtensionRegistry:
    """Load the registry, exiting with an error if it does not exist."""
    if not cfg.extensions_file.exists():
        console.print(
            f"[bold red]Error:[/] Registry not found at [bold]{cfg.extensions_file}[/].\n"
            "Run [bold cyan]ext generate[/] first."
        )
        raise typer.Exit(1)
    return ExtensionRegistry.load(cfg.extensions_file)


def _run_install_loop(
    extensions: list[Extension],
    cfg: AppConfig,
    *,
    dry_run: bool,
) -> tuple[Table, int, _FailList]:
    """Execute the install loop and return the result table, count, and failures."""
    table = _make_install_table()
    state: tuple[int, _FailList] = (0, [])
    for ext in extensions:
        state = _process_extension(ext, cfg, table, state, dry_run=dry_run)
    installed, failed = state
    return table, installed, failed


def _make_install_table() -> Table:
    """Create and return the install progress table."""
    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
    table.add_column("Status", width=8)
    table.add_column("ID")
    table.add_column("Marketplace", justify="right")
    return table


def _process_extension(
    ext: Extension,
    cfg: AppConfig,
    table: Table,
    state: tuple[int, _FailList],
    *,
    dry_run: bool,
) -> tuple[int, _FailList]:
    """Process one extension: dry-run skip, install success, or failure."""
    installed, failed = state
    if dry_run:
        table.add_row("[dim]skip[/]", ext.id, _market_label(ext))
        return installed, failed
    try:
        install_extension(ext, cfg.helper)
    except Exception as exc:
        logger.debug("Failed to install %s: %s", ext.id, exc, exc_info=True)
        table.add_row("[red]✗[/]", ext.id, _market_label(ext))
        return installed, [*failed, (ext, str(exc))]
    else:
        table.add_row("[green]✓[/]", ext.id, _market_label(ext))
        return installed + 1, failed


def _filter_extensions(registry: ExtensionRegistry, marketplace: str) -> list[Extension]:
    """Return extensions filtered by the given marketplace selector."""
    match marketplace:
        case "open-vsx":
            return registry.filter_marketplace(Marketplace.OPEN_VSX)
        case "microsoft":
            return registry.filter_marketplace(Marketplace.MICROSOFT)
        case _:
            return list(registry.extensions)


def _print_summary(
    *,
    dry_run: bool,
    extensions: list[Extension],
    installed: int,
    failed: list[tuple[Extension, str]],
) -> None:
    """Print post-install summary to the console."""
    if dry_run:
        console.print(f"[dim]Dry run — would install {len(extensions)} extensions.[/]")
        return
    if failed:
        console.print(
            f"[bold green]✓[/] Installed [bold]{installed}[/]  "
            f"[bold red]✗[/] Failed [bold]{len(failed)}[/]"
        )
        console.print()
        for ext, reason in failed:
            console.print(f"  [red]✗[/] [bold]{ext.id}[/]  [dim]{reason}[/]")
        raise typer.Exit(1)
    console.print(f"[bold green]✓[/] All [bold]{installed}[/] extensions installed successfully.")
