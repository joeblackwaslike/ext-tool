"""Domain models and the ExtensionRegistry (owns serialisation)."""

import csv
import io
import json
import tomllib
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Self, cast

import tomli_w
from pydantic import BaseModel, Field, field_validator

_JSON_MODE = "json"
_UTF8 = "utf-8"


class Marketplace(StrEnum):
    """Which marketplace hosts this extension."""

    OPEN_VSX = "open-vsx"
    MICROSOFT = "microsoft"


class ExportFormat(StrEnum):
    """Supported export formats."""

    TOML = "toml"
    JSON = "json"
    CSV = "csv"


class Extension(BaseModel):
    """A single VS Code / Cursor extension entry."""

    id: str = Field(description="Canonical publisher.name identifier (lowercase).")
    name: str = Field(description="Human-readable display name.")
    description: str = Field(default="", description="Short extension description.")
    publisher: str = Field(description="Publisher ID (lowercase).")
    publisher_display_name: str = Field(default="", description="Publisher display name.")
    version: str = Field(default="", description="Installed version string.")
    marketplace: Marketplace = Field(description="Source marketplace for installation.")

    @field_validator("id", "publisher", mode="before")
    @classmethod
    def lowercase(cls, raw_id: str) -> str:
        """Ensure id and publisher are always stored lowercase."""
        return raw_id.lower()

    @property
    def ext_name(self) -> str:
        """The name portion of publisher.name."""
        return self.id.split(".", 1)[-1]


class ExtensionRegistry(BaseModel):
    """The full extension registry — owns its own serialisation."""

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )
    extensions: list[Extension] = Field(default_factory=list)

    # ── Lookup helpers ─────────────────────────────────────────────────────

    def by_id(self, ext_id: str) -> Extension | None:
        """Return the extension with this id, or None."""
        normalized = ext_id.lower()
        return next((ext for ext in self.extensions if ext.id == normalized), None)

    def filter_marketplace(self, marketplace: Marketplace) -> list[Extension]:
        """Return only extensions matching the given marketplace."""
        return [ext for ext in self.extensions if ext.marketplace == marketplace]

    # ── TOML round-trip ────────────────────────────────────────────────────

    def to_toml(self) -> str:
        """Serialise registry to TOML string."""
        ts = self.generated_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        open_vsx = sum(1 for ext in self.extensions if ext.marketplace == Marketplace.OPEN_VSX)
        microsoft = len(self.extensions) - open_vsx
        open_vsx_label = "open-vsx"

        header = (
            "# VS Code / Cursor extension registry\n"
            f"# Generated: {ts}\n"
            f"# Total: {len(self.extensions)}"
            f"  ({open_vsx_label}: {open_vsx}, microsoft: {microsoft})\n"
            "#\n"
            "# marketplace values:\n"
            f'#   "{open_vsx_label}"  — installed via: $helper --install-extension <id>\n'
            '#   "microsoft" — installed via: VSIX download from gallery.vsassets.io\n'
            "\n"
        )
        payload = {"extension": [ext.model_dump(mode=_JSON_MODE) for ext in self.extensions]}
        return header + cast(str, tomli_w.dumps(payload))

    def save(self, path: Path) -> None:
        """Write registry to *path* as TOML."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_toml(), encoding=_UTF8)

    @classmethod
    def load(cls, path: Path) -> Self:
        """Load registry from a TOML file."""
        with path.open("rb") as registry_fh:
            registry_data = tomllib.load(registry_fh)
        extensions = [Extension(**entry) for entry in registry_data.get("extension", [])]
        return cls(extensions=extensions)

    # ── Export ─────────────────────────────────────────────────────────────

    def export(self, path: Path, fmt: ExportFormat) -> None:
        """Export registry to *path* in the requested format."""
        path.parent.mkdir(parents=True, exist_ok=True)
        match fmt:
            case ExportFormat.TOML:
                path.write_text(self.to_toml(), encoding=_UTF8)
            case ExportFormat.JSON:
                rows = [ext.model_dump(mode=_JSON_MODE) for ext in self.extensions]
                path.write_text(
                    json.dumps({"extensions": rows}, indent=2),
                    encoding=_UTF8,
                )
            case ExportFormat.CSV:
                _export_csv(self.extensions, path)

    # ── Merge ──────────────────────────────────────────────────────────────

    def merge(self, other: "ExtensionRegistry") -> "ExtensionRegistry":
        """Return a new registry merging *other* into self (other wins on conflict)."""
        index = {ext.id: ext for ext in self.extensions}
        for ext in other.extensions:
            index[ext.id] = ext
        return ExtensionRegistry(
            generated_at=datetime.now(UTC),
            extensions=sorted(index.values(), key=lambda entry: (entry.marketplace, entry.id)),
        )


def _export_csv(extensions: list[Extension], path: Path) -> None:
    """Write *extensions* to *path* in CSV format."""
    if not extensions:
        path.write_text("", encoding=_UTF8)
        return
    buf = io.StringIO()
    fields = list(Extension.model_fields.keys())
    writer = csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    for ext in extensions:
        writer.writerow(ext.model_dump(mode=_JSON_MODE))
    path.write_text(buf.getvalue(), encoding=_UTF8)


def load_from_export(
    path: Path,
    fmt: ExportFormat | None = None,
) -> ExtensionRegistry:
    """Load a registry from a previously exported file.

    If *fmt* is None the format is inferred from the file suffix.
    """
    if fmt is None:
        fmt = _infer_format(path)

    match fmt:
        case ExportFormat.TOML:
            return ExtensionRegistry.load(path)
        case ExportFormat.JSON:
            registry_data = json.loads(path.read_text(encoding=_UTF8))
            extensions = [Extension(**entry) for entry in registry_data.get("extensions", [])]
            return ExtensionRegistry(extensions=extensions)
        case ExportFormat.CSV:
            return _load_csv_registry(path)


def _load_csv_registry(path: Path) -> ExtensionRegistry:
    """Load an ExtensionRegistry from a CSV file."""
    with path.open(encoding=_UTF8, newline="") as csv_fh:
        reader = csv.DictReader(csv_fh)
        csv_extensions = [Extension(**row) for row in reader]
    return ExtensionRegistry(extensions=csv_extensions)


def _infer_format(path: Path) -> ExportFormat:
    """Infer ExportFormat from file suffix."""
    suffix = path.suffix.lower().lstrip(".")
    try:
        return ExportFormat(suffix)
    except ValueError:
        msg = (
            f"Cannot infer export format from suffix '.{suffix}'. "
            "Use --format to specify explicitly."
        )
        raise ValueError(msg) from None
