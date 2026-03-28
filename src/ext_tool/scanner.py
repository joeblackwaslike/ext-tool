"""Scan a local VS Code / Cursor extensions directory.

Strategy
--------
1. Read ``extensions.json`` for the deduplicated canonical ID list — VS Code's
   own source of truth, handles multiple versions on disk cleanly.
2. For *every* extension (open-vsx and microsoft alike) read
   ``<relativeLocation>/package.json`` for ``displayName`` and ``description``.
   This avoids any extra API calls for metadata — the data is already local.
3. The Open VSX check (in marketplace.py) is performed separately and only to
   determine the ``marketplace`` routing field.
"""

import json
import logging
import types
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_EXTENSIONS_DIR = "extensions"
_EXTENSIONS_INDEX = "extensions.json"
_DESCRIPTION_KEY = "description"

_RawEntry = dict[str, Any]

# Known default locations keyed by CLI helper name
_DEFAULT_DIRS: types.MappingProxyType[str, Path] = types.MappingProxyType({
    "code-insiders": Path.home() / ".vscode-insiders" / _EXTENSIONS_DIR,
    "cursor": Path.home() / ".cursor" / _EXTENSIONS_DIR,
    "code": Path.home() / ".vscode" / _EXTENSIONS_DIR,
})


def resolve_extensions_dir(helper: str, override: Path | None = None) -> Path:
    """Return the extensions directory to scan.

    Args:
        helper:   The VS Code-compatible CLI binary name (e.g. ``"cursor"``).
        override: If provided, use this path directly.

    Raises:
        FileNotFoundError: When the resolved directory does not exist.
    """
    if override is None:
        path = _DEFAULT_DIRS.get(helper, Path.home() / ".vscode" / _EXTENSIONS_DIR)
    else:
        path = override

    if not path.exists():
        msg = f"Extensions directory not found: {path}"
        raise FileNotFoundError(msg)

    logger.debug("Extensions directory: %s", path)
    return path


def _read_package_meta(extensions_dir: Path, relative_location: str) -> dict[str, str]:
    """Read displayName and description from an extension's package.json.

    Returns an empty dict on any error so callers can always safely ``.get()``.
    """
    pkg = extensions_dir / relative_location / "package.json"
    if not pkg.exists():
        logger.debug("package.json not found: %s", pkg)
        return {}
    try:
        raw_text = pkg.read_text(encoding="utf-8")
    except Exception:
        logger.debug("Failed to parse package.json: %s", pkg, exc_info=True)
        return {}
    else:
        parsed = json.loads(raw_text)
        return {
            "display_name": parsed.get("displayName", ""),
            _DESCRIPTION_KEY: parsed.get(_DESCRIPTION_KEY, ""),
        }


def _deduplicate_entries(raw: list[_RawEntry]) -> list[_RawEntry]:
    """Return one entry per extension id, keeping the highest installedTimestamp."""
    seen: dict[str, _RawEntry] = {}
    for entry in raw:
        ext_id = str(entry["identifier"]["id"]).lower()
        ts = entry.get("metadata", {}).get("installedTimestamp", 0)
        if ext_id not in seen or ts > seen[ext_id]["_ts"]:
            seen[ext_id] = {**entry, "_ts": ts}
    return list(seen.values())


def _entry_to_dict(extensions_dir: Path, entry: dict[str, Any]) -> dict[str, str]:
    """Convert a raw extensions.json entry to a plain string dict."""
    ext_id = str(entry["identifier"]["id"]).lower()
    publisher = ext_id.split(".", 1)[0]
    pkg = _read_package_meta(extensions_dir, str(entry.get("relativeLocation", "")))
    meta = entry.get("metadata") or {}
    publisher_display = str(meta.get("publisherDisplayName", "") or publisher)
    logger.debug("Scanned: %s  (v%s)", ext_id, entry.get("version", ""))
    return {
        "id": ext_id,
        "version": str(entry.get("version", "")),
        "relative_location": str(entry.get("relativeLocation", "")),
        "publisher": publisher,
        "publisher_display_name": publisher_display,
        "display_name": pkg.get("display_name") or ext_id.split(".", 1)[-1],
        _DESCRIPTION_KEY: pkg.get(_DESCRIPTION_KEY, ""),
    }


def scan_local_extensions(extensions_dir: Path) -> list[dict[str, str]]:
    """Return a list of raw extension dicts from the local filesystem.

    Each dict contains:
        id, version, relative_location, publisher, publisher_display_name,
        display_name, description

    The ``marketplace`` field is intentionally absent — it is assigned by
    :func:`ext_tool.marketplace.classify_extensions` after async Open VSX checks.

    Args:
        extensions_dir: Path to the VS Code extensions directory.

    Raises:
        FileNotFoundError: When ``extensions.json`` is missing.
    """
    index_file = extensions_dir / _EXTENSIONS_INDEX
    if not index_file.exists():
        msg = f"extensions.json not found in {extensions_dir}"
        raise FileNotFoundError(msg)

    raw: list[dict[str, Any]] = json.loads(index_file.read_text(encoding="utf-8"))
    logger.debug("extensions.json contains %d entries", len(raw))
    deduped = _deduplicate_entries(raw)
    logger.debug("Total unique extensions: %d", len(deduped))
    return [_entry_to_dict(extensions_dir, entry) for entry in deduped]
