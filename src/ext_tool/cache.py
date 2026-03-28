"""Simple disk-backed TTL cache for HTTP responses."""

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_TTL: float = 300.0  # 5 minutes


class DiskCache:
    """A write-back TTL cache backed by a JSON file on disk.

    Entries are held in memory and flushed to disk in a single write via
    :meth:`flush`.  This avoids redundant I/O when many keys are written in
    one batch (e.g. one entry per extension in a ``asyncio.gather`` call).

    Cache file format::

        { "<key>": { "v": <value>, "ts": <unix-timestamp-float> } }
    """

    _path: Path
    _ttl: float
    _store: dict[str, tuple[Any, float]]

    def __init__(self, path: Path, ttl: float = DEFAULT_TTL) -> None:
        """Initialise the cache, loading any valid (non-stale) entries from disk."""
        self._path = path
        self._ttl = ttl
        self._store = {}
        self._load()

    # ── public ────────────────────────────────────────────────────────────────

    def get(self, key: str) -> Any | None:
        """Return the cached value for *key*, or ``None`` if absent/stale."""
        entry = self._store.get(key)
        if entry is None:
            return None
        cached_val, ts = entry
        if time.time() - ts > self._ttl:
            self._store.pop(key, None)
            return None
        return cached_val

    def set(self, key: str, cached_val: Any) -> None:
        """Store *cached_val* in memory under *key* (no disk I/O)."""
        self._store[key] = (cached_val, time.time())

    def flush(self) -> None:
        """Write the current in-memory state to disk.

        Errors are logged and swallowed — a cache write failure must never
        prevent the surrounding command from completing.
        """
        try:
            self._write_cache()
        except Exception:
            logger.debug("Cache flush failed", exc_info=True)

    def _write_cache(self) -> None:
        """Serialize and write the in-memory store to disk."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            cache_key: {"v": cached_val, "ts": ts}
            for cache_key, (cached_val, ts) in self._store.items()
        }
        self._path.write_text(json.dumps(payload))
        logger.debug("Cache flushed to %s (%d entries)", self._path, len(payload))

    # ── private ───────────────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load cache from disk and drop stale entries."""
        if not self._path.exists():
            return
        try:
            raw: dict[str, dict[str, Any]] = json.loads(self._path.read_text())
        except Exception:
            logger.debug("Cache load failed, starting empty", exc_info=True)
            self._store = {}
        else:
            now = time.time()
            for cache_key, entry in raw.items():
                ts = float(entry["ts"])
                if now - ts <= self._ttl:
                    self._store[cache_key] = (entry["v"], ts)
