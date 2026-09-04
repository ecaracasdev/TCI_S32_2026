"""Compatibility helpers backed by the vendored ``autoconfig`` package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from config import Config
from logs import get_logger

config: Config | None = None
__loaded = False


def _config_path(config_file: str | Path) -> Path:
    path = Path(config_file)
    if path.exists():
        return path
    if isinstance(config_file, str):
        if config_file in {"default", "config"}:
            return Path("config.toml")
        if path.suffix:
            return path
        return Path(f"config.{config_file}.toml")
    return path


def _with_runtime_metadata(loaded: Config, path: Path) -> Config:
    return loaded.model_copy(
        update={
            "NAME": path.stem,
            "CONFIG_FILE": path.resolve(),
        }
    )


def load_config(config_file: str | Path = "config.toml", reload: bool = False) -> Config:
    """Load and validate a configuration through ``Config.maker``."""
    global config, __loaded

    path = _config_path(config_file)
    if __loaded and not reload and config is not None:
        return config

    try:
        loaded = Config.maker.load(path=path)
        config = _with_runtime_metadata(loaded, path)
        __loaded = True
        return config
    except Exception:
        get_logger().critical("Cannot load configuration file: %s", path)
        raise


def get_config(path: str | None = None) -> Config:
    """Return the process configuration, loading the default when needed."""
    if path is not None:
        return load_config(path)
    if not __loaded or config is None:
        return load_config()
    return config


def update_config(cfg: dict[str, Any]) -> Config:
    """Apply runtime overrides while preserving nested Pydantic validation."""
    global config
    current = get_config()
    updated: dict[str, Any] = {}

    for key, value in cfg.items():
        if isinstance(value, dict) and hasattr(current, key):
            nested = getattr(current, key)
            if isinstance(nested, BaseModel):
                updated[key] = nested.model_copy(update=value)
                continue
        updated[key] = value

    config = current.model_copy(update=updated)
    return config
