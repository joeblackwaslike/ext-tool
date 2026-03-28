"""Logging setup — rich console handler + optional debug file log."""

import logging
import uuid
from pathlib import Path

from rich.logging import RichHandler

logger = logging.getLogger("ext_tool")


class _DebugLogState:
    """Holds the optional debug log path for the current invocation."""

    path: Path | None = None


debug_log_state = _DebugLogState()


def setup_logging(*, debug: bool = False) -> Path | None:
    """Configure logging for the current invocation.

    Args:
        debug: When True, also writes DEBUG-level output to a file in cwd.

    Returns:
        Path to the debug log file if one was created, else None.
    """
    root = logging.getLogger("ext_tool")
    root.setLevel(logging.DEBUG if debug else logging.WARNING)
    root.handlers.clear()

    console_handler = RichHandler(
        level=logging.DEBUG if debug else logging.INFO,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    root.addHandler(console_handler)

    if debug:
        suffix = uuid.uuid4().hex[:6]
        debug_log_state.path = Path(f"ext.debug-{suffix}.log")
        file_handler = logging.FileHandler(debug_log_state.path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        root.addHandler(file_handler)
        root.debug("Debug logging enabled → %s", debug_log_state.path)
        return debug_log_state.path

    return None


def get_debug_log_path() -> Path | None:
    """Return the debug log path for the current invocation, if any."""
    return debug_log_state.path
