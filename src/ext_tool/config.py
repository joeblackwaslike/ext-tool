"""Application configuration and XDG config directory management."""

import tomllib
from pathlib import Path
from typing import Annotated, Self

import tomli_w
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME = "ext-tool"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.toml"
EXTENSIONS_FILE = CONFIG_DIR / "extensions.toml"

_MAX_CONCURRENCY = 50


def ensure_config_dir() -> Path:
    """Create ~/.config/ext-tool/ if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


class AppConfig(BaseSettings):
    """User-facing configuration for ext-tool.

    Loaded from (in order of precedence):
      1. CLI flags (injected by typer callback)
      2. Environment variables prefixed with EXT_
      3. ~/.config/ext-tool/config.toml
      4. Defaults below
    """

    model_config = SettingsConfigDict(
        env_prefix="EXT_",
        env_file=".env",
        extra="ignore",
    )

    helper: Annotated[
        str,
        Field(default="cursor", description="VS Code-compatible CLI binary to use."),
    ] = "cursor"

    extensions_file: Annotated[
        Path,
        Field(default=EXTENSIONS_FILE, description="Path to extensions.toml registry."),
    ] = EXTENSIONS_FILE

    extensions_dir: Annotated[
        Path | None,
        Field(default=None, description="Override VS Code extensions directory."),
    ] = None

    concurrency: Annotated[
        int,
        Field(
            default=10, ge=1, le=_MAX_CONCURRENCY, description="Max concurrent Open VSX requests."
        ),
    ] = 10

    debug: Annotated[
        bool,
        Field(default=False, description="Enable debug logging."),
    ] = False

    @classmethod
    def load(cls) -> Self:
        """Load config from file + environment."""
        if CONFIG_FILE.exists():
            with CONFIG_FILE.open("rb") as config_fh:
                file_data = tomllib.load(config_fh)
        else:
            file_data = {}
        return cls(**file_data)

    def save(self) -> None:
        """Persist current config to ~/.config/ext-tool/config.toml."""
        ensure_config_dir()
        serialized = self.model_dump(mode="json", exclude={"debug"})
        cleaned = {
            field_name: str(field_val) if isinstance(field_val, Path) else field_val
            for field_name, field_val in serialized.items()
            if field_val is not None
        }
        CONFIG_FILE.write_bytes(tomli_w.dumps(cleaned).encode())
