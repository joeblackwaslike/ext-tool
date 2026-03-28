"""ext update — regenerate registry then install in one step."""

import logging
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

logger = logging.getLogger(__name__)
console = Console()
app = typer.Typer(help="Re-generate the registry then install all extensions.")


@app.callback(invoke_without_command=True)
def update(
    ctx: typer.Context,
    marketplace: Annotated[
        str,
        typer.Option(
            "--marketplace",
            "-m",
            help="Which marketplace entries to install after generating: "
            "[dim]all | open-vsx | microsoft[/]",
        ),
    ] = "all",
    *,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Pass --dry-run to both generate and install."),
    ] = False,
) -> None:
    """Shortcut for running [bold cyan]ext generate[/] followed by [bold cyan]ext install[/]."""
    from ext_tool.commands.generate import generate as _generate
    from ext_tool.commands.install import install as _install

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]ext update[/]  —  generate → install",
            border_style="cyan",
        )
    )

    console.print()
    console.print(Rule("[dim cyan]Step 1 / 2  —  generate[/]", style="dim"))
    ctx.invoke(_generate, ctx=ctx, dry_run=dry_run)

    console.print(Rule("[dim cyan]Step 2 / 2  —  install[/]", style="dim"))
    ctx.invoke(_install, ctx=ctx, marketplace=marketplace, dry_run=dry_run)

    console.print(Panel.fit("[bold green]✓  Update complete.[/]", border_style="green"))
    console.print()
