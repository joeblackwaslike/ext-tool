"""Tests for ext_tool.marketplace — Open VSX classification (mocked)."""

import asyncio

import httpx
import respx

from ext_tool.marketplace import classify_extensions
from ext_tool.models import Marketplace

_HTTP_OK = 200
_HTTP_NOT_FOUND = 404

_FAKE_RAW: tuple[dict[str, str], ...] = (
    {
        "id": "charliermarsh.ruff",
        "publisher": "charliermarsh",
        "display_name": "Ruff",
        "description": "Fast linter.",
        "publisher_display_name": "Astral",
        "version": "1.0.0",
    },
    {
        "id": "ms-python.python",
        "publisher": "ms-python",
        "display_name": "Python",
        "description": "Python support.",
        "publisher_display_name": "Microsoft",
        "version": "2.0.0",
    },
)


@respx.mock
def test_classify_open_vsx_hit() -> None:
    """Extensions found on Open VSX get marketplace=open-vsx."""
    respx.get("https://open-vsx.org/api/charliermarsh/ruff").mock(
        return_value=httpx.Response(_HTTP_OK)
    )
    respx.get("https://open-vsx.org/api/ms-python/python").mock(
        return_value=httpx.Response(_HTTP_NOT_FOUND)
    )

    registry = asyncio.run(classify_extensions(list(_FAKE_RAW), concurrency=2))
    indexed = {ext.id: ext for ext in registry.extensions}

    assert indexed["charliermarsh.ruff"].marketplace == Marketplace.OPEN_VSX
    assert indexed["ms-python.python"].marketplace == Marketplace.MICROSOFT


@respx.mock
def test_classify_network_error_defaults_to_microsoft() -> None:
    """A network error during Open VSX check defaults to microsoft."""
    respx.get("https://open-vsx.org/api/charliermarsh/ruff").mock(
        side_effect=httpx.ConnectError("unreachable")
    )
    respx.get("https://open-vsx.org/api/ms-python/python").mock(
        side_effect=httpx.ConnectError("unreachable")
    )

    registry = asyncio.run(classify_extensions(list(_FAKE_RAW), concurrency=2))
    for ext in registry.extensions:
        assert ext.marketplace == Marketplace.MICROSOFT


@respx.mock
def test_classify_sorts_open_vsx_first() -> None:
    """open-vsx entries appear before microsoft entries in the registry."""
    respx.get("https://open-vsx.org/api/charliermarsh/ruff").mock(
        return_value=httpx.Response(_HTTP_OK)
    )
    respx.get("https://open-vsx.org/api/ms-python/python").mock(
        return_value=httpx.Response(_HTTP_NOT_FOUND)
    )

    registry = asyncio.run(classify_extensions(list(_FAKE_RAW), concurrency=2))
    marketplaces = [ext.marketplace for ext in registry.extensions]
    assert marketplaces[0] == Marketplace.OPEN_VSX


@respx.mock
def test_classify_all_open_vsx() -> None:
    """When all extensions are on Open VSX, all get marketplace=open-vsx."""
    for raw_ext in _FAKE_RAW:
        publisher, ext_name = raw_ext["id"].split(".")
        respx.get(f"https://open-vsx.org/api/{publisher}/{ext_name}").mock(
            return_value=httpx.Response(_HTTP_OK)
        )

    registry = asyncio.run(classify_extensions(list(_FAKE_RAW), concurrency=2))
    assert all(ext.marketplace == Marketplace.OPEN_VSX for ext in registry.extensions)


@respx.mock
def test_classify_preserves_metadata() -> None:
    """display_name and description are carried through from raw input."""
    respx.get("https://open-vsx.org/api/charliermarsh/ruff").mock(
        return_value=httpx.Response(_HTTP_OK)
    )
    respx.get("https://open-vsx.org/api/ms-python/python").mock(
        return_value=httpx.Response(_HTTP_NOT_FOUND)
    )

    registry = asyncio.run(classify_extensions(list(_FAKE_RAW), concurrency=2))
    indexed = {ext.id: ext for ext in registry.extensions}
    assert indexed["charliermarsh.ruff"].name == "Ruff"
    assert indexed["charliermarsh.ruff"].description == "Fast linter."
