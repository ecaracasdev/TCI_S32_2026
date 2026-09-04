"""Rich rendering for configuration models with secret redaction."""

from __future__ import annotations

import ipaddress
from numbers import Number
from typing import Any
from urllib.parse import urlparse

from pydantic import SecretStr
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .models import ConfigurationSection
from .schema import field_extra


def _computed_names(model: ConfigurationSection) -> set[str]:
    names = set(type(model).model_computed_fields)
    for model_type in type(model).__mro__:
        if model_type is ConfigurationSection:
            break
        names.update(
            name
            for name, value in model_type.__dict__.items()
            if not name.startswith("_") and isinstance(value, property)
        )
    return names


def _is_url_or_ip(value: str) -> bool:
    if value.lower() == "localhost":
        return True
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        parsed = urlparse(value)
        return bool(parsed.scheme and parsed.netloc)


def _display(value: Any) -> Text:
    if isinstance(value, SecretStr) or hasattr(value, "get_secret_value"):
        return Text("[redacted]", style="bold")
    if isinstance(value, ConfigurationSection):
        return Text(f"<{value.__class__.__name__}>")
    if isinstance(value, bool) or isinstance(value, Number):
        return Text(str(value), style="violet")
    if isinstance(value, str):
        style = "green" if _is_url_or_ip(value) else "gold1"
        return Text(value, style=style)
    if isinstance(value, (list, tuple, set)):
        result = Text("[")
        for index, item in enumerate(value):
            if index:
                result.append(", ")
            result.append_text(_display(item))
        result.append("]")
        return result
    if isinstance(value, dict):
        result = Text("{")
        for index, (key, item) in enumerate(value.items()):
            if index:
                result.append(", ")
            result.append(f"{key}=", style="cyan")
            result.append_text(_display(item))
        result.append("}")
        return result
    return Text(str(value))


def _rows(
    model: ConfigurationSection,
    include_computed: bool,
    prefix: str = "",
) -> list[tuple[str, Text]]:
    rows: list[tuple[str, Text]] = []
    for name, field in type(model).model_fields.items():
        value = getattr(model, name, None)
        if value is None:
            continue
        path = f"{prefix}.{name}" if prefix else name
        if isinstance(value, ConfigurationSection):
            rows.extend(_rows(value, include_computed, path))
            continue
        elif field_extra(field).get("secret"):
            rows.append((path, Text("[redacted]", style="bold")))
        else:
            rows.append((path, _display(value)))
    if include_computed:
        for name in _computed_names(model):
            value = getattr(model, name)
            path = f"{prefix}.{name}" if prefix else name
            rows.append((path, _display(value)))
    return rows


def build_graph(model: ConfigurationSection, *, include_computed: bool = False) -> Table:
    """Build a Rich table for a configuration model."""
    table = Table(title=model.__class__.__name__)
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    for name, value in _rows(model, include_computed):
        table.add_row(name, value)
    return table


def print_model_graph(
    model: ConfigurationSection,
    *,
    include_computed: bool = False,
    console: Console | None = None,
) -> None:
    """Print a Rich table for a configuration model.

    Args:
        model: Configuration section to render.
        include_computed: Include computed properties in the output.
        console: Optional Rich console destination.
    """
    (console or Console()).print(build_graph(model, include_computed=include_computed))
