"""ext completions — emit shell completion scripts."""

from __future__ import annotations

import logging
import sys
import types
from enum import StrEnum
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

logger = logging.getLogger(__name__)
console = Console()


class Shell(StrEnum):
    """Supported shell targets for completion generation."""

    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"


_BASH_INSTALL_HINT = '# Add to ~/.bashrc:\neval "$(ext completions bash)"'
_ZSH_INSTALL_HINT = '# Add to ~/.zshrc:\neval "$(ext completions zsh)"'
_FISH_INSTALL_HINT = "# Add to ~/.config/fish/config.fish:\next completions fish | source"

_INSTALL_HINT: types.MappingProxyType[Shell, str] = types.MappingProxyType({
    Shell.BASH: _BASH_INSTALL_HINT,
    Shell.ZSH: _ZSH_INSTALL_HINT,
    Shell.FISH: _FISH_INSTALL_HINT,
})

_BASH_COMPLETION = """\
# ext-tool bash completions
_ext_complete() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local cmds="generate install update export import completions --help --version --debug"
    COMPREPLY=($(compgen -W "$cmds" -- "$cur"))
}
complete -F _ext_complete ext
"""

_ZSH_COMPLETION = """\
# ext-tool zsh completions
#compdef ext

_ext() {
  local -a commands
  commands=(
    'generate:Scan extensions and write registry'
    'install:Install extensions from registry'
    'update:Generate then install'
    'export:Export registry to file'
    'import:Import a registry file'
    'completions:Emit shell completions'
  )
  _describe 'ext commands' commands
}

compdef _ext ext
"""

_FISH_COMPLETION = """\
# ext-tool fish completions
complete -c ext -f
complete -c ext -n '__fish_use_subcommand' -a generate    -d 'Scan extensions and write registry'
complete -c ext -n '__fish_use_subcommand' -a install     -d 'Install extensions from registry'
complete -c ext -n '__fish_use_subcommand' -a update      -d 'Generate then install'
complete -c ext -n '__fish_use_subcommand' -a export      -d 'Export registry to file'
complete -c ext -n '__fish_use_subcommand' -a import      -d 'Import a registry file'
complete -c ext -n '__fish_use_subcommand' -a completions -d 'Emit shell completions'
"""

_COMPLETION_SCRIPT: types.MappingProxyType[Shell, str] = types.MappingProxyType({
    Shell.BASH: _BASH_COMPLETION,
    Shell.ZSH: _ZSH_COMPLETION,
    Shell.FISH: _FISH_COMPLETION,
})


def completions_cmd(
    ctx: typer.Context,
    shell: Annotated[
        Shell,
        typer.Argument(help="Shell: [dim]bash | zsh | fish[/]"),
    ],
    *,
    show_install: Annotated[
        bool,
        typer.Option("--show-install", help="Print install instructions instead of the script."),
    ] = False,
) -> None:
    r"""Print a completion script for the given shell.

    Pipe directly to your shell config or source it inline:

    \b
      eval "$(ext completions zsh)"
    """
    if show_install:
        console.print()
        console.print(
            Panel(
                _INSTALL_HINT[shell],
                title=f"[dim]{shell} install instructions[/]",
                border_style="dim",
            )
        )
        console.print()
        return

    # Plain write — output must be sourceable, no Rich escape codes
    sys.stdout.write(_COMPLETION_SCRIPT[shell])
