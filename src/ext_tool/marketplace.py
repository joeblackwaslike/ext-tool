"""Marketplace interactions — Open VSX classification, MS VSIX download, install."""

import asyncio
import logging
import re
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path
from typing import cast

import httpx

from ext_tool.cache import DiskCache
from ext_tool.config import CONFIG_DIR
from ext_tool.models import Extension, ExtensionRegistry, Marketplace

logger = logging.getLogger(__name__)

OPEN_VSX_API = "https://open-vsx.org/api/{publisher}/{name}"
MS_VSIX_URL = (
    "https://{publisher}.gallery.vsassets.io"
    "/_apis/public/gallery/publisher/{publisher}"
    "/extension/{name}/latest"
    "/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage"
)
_DOWNLOAD_RETRIES = 3
_RETRY_DELAY = 2.0
_HTTP_OK = 200

_OPEN_VSX_CACHE_FILE = CONFIG_DIR / "cache" / "open-vsx.json"
_OPEN_VSX_CACHE_TTL = 300.0  # 5 minutes


# ── Open VSX classification ────────────────────────────────────────────────────


async def _check_one(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    publisher: str,
    name: str,
    cache: DiskCache,
) -> bool:
    """Return True if the extension exists on Open VSX."""
    key = f"{publisher}.{name}"
    cached = cache.get(key)
    if cached is not None:
        logger.debug("Open VSX cache hit %s.%s → %s", publisher, name, cached)
        return cast(bool, cached)

    url = OPEN_VSX_API.format(publisher=publisher, name=name)
    async with sem:
        try:
            resp = await client.get(url, timeout=10)
        except httpx.RequestError:
            logger.debug("Open VSX request error for %s.%s", publisher, name, exc_info=True)
            return False
        else:
            found = bool(resp.status_code == _HTTP_OK)
            logger.debug("Open VSX check %s.%s → %s", publisher, name, found)
            cache.set(key, found)
            return found


def _build_extension(raw: dict[str, str], *, on_open_vsx: bool) -> Extension:
    """Convert a raw scanner dict and Open VSX flag to an Extension."""
    market = Marketplace.OPEN_VSX if on_open_vsx else Marketplace.MICROSOFT
    return Extension(
        id=raw["id"],
        name=raw["display_name"],
        description=raw.get("description", ""),
        publisher=raw["publisher"],
        publisher_display_name=raw.get("publisher_display_name", ""),
        version=raw.get("version", ""),
        marketplace=market,
    )


def _sort_key(ext: Extension) -> tuple[int, str]:
    """Sort key: open-vsx first, then alphabetical by id."""
    return (0 if ext.marketplace == Marketplace.OPEN_VSX else 1, ext.id)


def _ext_name_from_item(ext_item: dict[str, str]) -> str:
    """Extract the extension name portion from a raw extension dict."""
    return ext_item["id"].split(".", 1)[-1]


async def _gather_checks(
    raw_extensions: list[dict[str, str]],
    sem: asyncio.Semaphore,
    cache: DiskCache,
) -> tuple[bool, ...]:
    """Run Open VSX existence checks for all extensions and return results."""
    async with httpx.AsyncClient(
        headers={"User-Agent": "ext-tool/0.1.0"},
        follow_redirects=True,
    ) as client:
        tasks = [
            _check_one(client, sem, ext_entry["publisher"], _ext_name_from_item(ext_entry), cache)
            for ext_entry in raw_extensions
        ]
        check_results = await asyncio.gather(*tasks)
    return tuple(check_results)


async def classify_extensions(
    raw_extensions: list[dict[str, str]],
    *,
    concurrency: int = 10,
) -> ExtensionRegistry:
    """Check every extension against Open VSX and return a populated registry.

    Args:
        raw_extensions: Output from :func:`ext_tool.scanner.scan_local_extensions`.
        concurrency:    Max simultaneous Open VSX HTTP requests.

    Returns:
        :class:`~ext_tool.models.ExtensionRegistry` with marketplace field set.
    """
    sem = asyncio.Semaphore(concurrency)
    cache = DiskCache(_OPEN_VSX_CACHE_FILE, ttl=_OPEN_VSX_CACHE_TTL)
    check_results = await _gather_checks(raw_extensions, sem, cache)
    cache.flush()

    extensions = [
        _build_extension(raw, on_open_vsx=bool(flag))
        for raw, flag in zip(raw_extensions, check_results, strict=False)
    ]
    extensions.sort(key=_sort_key)
    return ExtensionRegistry(extensions=extensions)


# ── Installation ───────────────────────────────────────────────────────────────


def install_open_vsx(ext: Extension, helper: str) -> None:
    """Install an extension directly from the Open VSX / default marketplace."""
    logger.debug("Installing open-vsx extension: %s", ext.id)
    subprocess.run(
        [helper, "--install-extension", ext.id],
        check=True,
    )


def _read_vsix_manifest(raw_vsix: Path, publisher: str, name: str) -> str:
    """Read and return the raw VSIX manifest XML string."""
    try:
        with zipfile.ZipFile(raw_vsix) as zip_fh:
            manifest = zip_fh.read("extension.vsixmanifest").decode("utf-8")
    except Exception as exc:
        raw_vsix.unlink(missing_ok=True)
        msg = f"Could not read VSIX manifest for {publisher}.{name}"
        raise RuntimeError(msg) from exc
    return manifest


def _extract_vsix_version(manifest: str, raw_vsix: Path, publisher: str, name: str) -> str:
    """Extract and return the version string from a VSIX manifest."""
    match = re.search(r'<Identity[^>]+Version="([^"]+)"', manifest)
    if not match:
        raw_vsix.unlink(missing_ok=True)
        msg = f"Could not extract version from manifest for {publisher}.{name}"
        raise RuntimeError(msg)
    return match.group(1)


def _attempt_download(url: str, raw_vsix: Path) -> bool:
    """Attempt one VSIX download. Returns True on success, False on HTTP error."""
    try:
        with httpx.stream("GET", url, follow_redirects=True, timeout=60) as resp:
            resp.raise_for_status()
            with raw_vsix.open("wb") as vsix_fh:
                for chunk in resp.iter_bytes():
                    vsix_fh.write(chunk)
    except httpx.HTTPError:
        return False
    return True


def _stream_vsix(url: str, raw_vsix: Path, publisher: str, name: str) -> None:
    """Stream-download a VSIX file, retrying on failure."""
    for attempt in range(1, _DOWNLOAD_RETRIES + 1):
        logger.debug("Downloading VSIX (attempt %d): %s", attempt, url)
        if _attempt_download(url, raw_vsix):
            return
        logger.debug("Download attempt %d failed", attempt)
        if attempt < _DOWNLOAD_RETRIES:
            time.sleep(_RETRY_DELAY)
        else:
            msg = f"Failed to download {publisher}.{name} after {_DOWNLOAD_RETRIES} attempts"
            raise RuntimeError(msg)


def _download_vsix(publisher: str, name: str, dest: Path) -> Path:
    """Download the latest VSIX from the Microsoft marketplace.

    Retries up to ``_DOWNLOAD_RETRIES`` times on failure.

    Returns:
        Path to the downloaded (and version-renamed) VSIX file.

    Raises:
        RuntimeError: When all download attempts fail or version extraction fails.
    """
    url = MS_VSIX_URL.format(publisher=publisher, name=name)
    raw_vsix = dest / f"{name}.vsix"
    _stream_vsix(url, raw_vsix, publisher, name)
    manifest = _read_vsix_manifest(raw_vsix, publisher, name)
    version = _extract_vsix_version(manifest, raw_vsix, publisher, name)
    versioned = dest / f"{publisher}.{name}-{version}.vsix"
    raw_vsix.rename(versioned)
    logger.debug("VSIX saved: %s", versioned)
    return versioned


def install_microsoft(ext: Extension, helper: str) -> None:
    """Download a VSIX from the Microsoft marketplace and install it locally."""
    logger.debug("Installing microsoft extension: %s", ext.id)
    with tempfile.TemporaryDirectory(prefix="ext-tool-vsix-") as vsix_dir:
        vsix_path = _download_vsix(ext.publisher, ext.ext_name, Path(vsix_dir))
        subprocess.run(
            [helper, "--install-extension", str(vsix_path)],
            check=True,
        )


def install_extension(ext: Extension, helper: str) -> None:
    """Route an extension to the correct install function based on marketplace."""
    match ext.marketplace:
        case Marketplace.OPEN_VSX:
            install_open_vsx(ext, helper)
        case Marketplace.MICROSOFT:
            install_microsoft(ext, helper)
