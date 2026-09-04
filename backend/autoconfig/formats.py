"""Serialization and parsing for supported configuration formats."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import tomlkit
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


SUPPORTED_FORMATS = {"toml", "yaml", "yml", "json"}


def normalize_format(value: str) -> str:
    """Normalize a format name or extension to ``toml``, ``yaml`` or ``json``.

    Args:
        value: Format name or filename extension, with or without a dot.

    Returns:
        The canonical format name.

    Raises:
        ValueError: If the format is not supported.
    """
    value = value.lower().lstrip(".")
    if value == "yml":
        return "yaml"
    if value not in {"toml", "yaml", "json"}:
        raise ValueError(f"Unsupported configuration format: {value}")
    return value


def format_from_path(path: Path) -> str:
    """Return the canonical format name inferred from a path extension."""
    return normalize_format(path.suffix)


def _toml_value(value: Any) -> str:
    return tomlkit.item(value).as_string()


def _toml_section_box(comments: dict[str, str], path: str, width: int) -> list[str]:
    title = path.rsplit(".", 1)[-1].replace("_", " ").title()
    comment = comments.get(path, "")
    details = [line for line in comment.splitlines() if line.strip().lower() != title.lower()]
    content_width = max(width, len(title) + 4)
    title_padding = content_width - len(title) - 2
    left = title_padding // 2
    right = title_padding - left
    top = "#" * left + f" {title} " + "#" * right
    if not details:
        return [top]
    return [top, *[f"# {line}" for line in details], "#" * content_width]


def _render_toml(
    data: dict[str, Any],
    comments: dict[str, str],
    prefix: str = "",
    *,
    include_comments: bool = True,
) -> list[str]:
    lines: list[str] = []
    primitives = [
        (key, value)
        for key, value in data.items()
        if not isinstance(value, dict)
        and not (isinstance(value, list) and value and all(isinstance(item, dict) for item in value))
    ]
    sections = [(key, value) for key, value in data.items() if isinstance(value, dict)]
    table_arrays = [
        (key, value)
        for key, value in data.items()
        if isinstance(value, list) and value and all(isinstance(item, dict) for item in value)
    ]

    for key, value in primitives:
        path = f"{prefix}.{key}" if prefix else key
        if include_comments and path in comments:
            lines.extend(f"# {line}" for line in comments[path].splitlines())
        lines.append(f"{key} = {_toml_value(value)}")

    for key, value in sections:
        path = f"{prefix}.{key}" if prefix else key
        if lines:
            lines.append("")
        section_content = [
            f"[{path}]",
            *_render_toml(value, comments, path, include_comments=include_comments),
        ]
        if include_comments:
            title = key.replace("_", " ").title()
            comment = comments.get(path, "")
            detail_width = max((len(f"# {line}") for line in comment.splitlines()), default=0)
            width = max(34, len(title) + 4, detail_width, *(len(line) for line in section_content))
            lines.extend(_toml_section_box(comments, path, width))
            lines.extend(section_content)
            lines.append("#" * width)
        else:
            lines.extend(section_content)

    for key, values in table_arrays:
        path = f"{prefix}.{key}" if prefix else key
        if lines:
            lines.append("")
        for index, value in enumerate(values):
            if index:
                lines.append("")
            section_content = [
                f"[[{path}]]",
                *_render_toml(value, comments, path, include_comments=include_comments),
            ]
            if include_comments:
                title = key.replace("_", " ").title()
                comment = comments.get(path, "")
                detail_width = max((len(f"# {line}") for line in comment.splitlines()), default=0)
                width = max(34, len(title) + 4, detail_width, *(len(line) for line in section_content))
                lines.extend(_toml_section_box(comments, path, width))
            lines.extend(section_content)
            if include_comments:
                lines.append("#" * width)
    return lines


def _yaml_map(
    data: dict[str, Any],
    comments: dict[str, str],
    prefix: str = "",
    *,
    include_comments: bool = True,
) -> CommentedMap:
    result = CommentedMap()
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        value = _yaml_value(value, comments, path, include_comments=include_comments)
        result[key] = value
        if include_comments and path in comments:
            comment = comments[path]
            if isinstance(value, dict):
                title = key.replace("_", " ").title()
                comment = "\n".join(
                    [
                        "############################",
                        title,
                        *comment.splitlines(),
                        "############################",
                    ]
                )
            result.yaml_set_comment_before_after_key(key, before=comment)
    return result


def _yaml_value(
    value: Any,
    comments: dict[str, str],
    path: str,
    *,
    include_comments: bool,
) -> Any:
    if isinstance(value, dict):
        return _yaml_map(value, comments, path, include_comments=include_comments)
    if isinstance(value, list):
        result = CommentedSeq()
        for item in value:
            result.append(_yaml_value(item, comments, path, include_comments=include_comments))
        return result
    return value


def serialize(data: dict[str, Any], format_name: str, comments: dict[str, str] | None) -> str:
    """Serialize configuration data to a supported text format.

    Args:
        data: Plain configuration mapping to serialize.
        format_name: Target format name or extension.
        comments: Optional field comments. ``None`` disables comments and
            metadata.

    Returns:
        A UTF-8 compatible configuration document ending with a newline.
    """
    format_name = normalize_format(format_name)
    include_comments = comments is not None
    comments = comments or {}
    if format_name == "toml":
        return "\n".join(
            _render_toml(data, comments, include_comments=include_comments)
        ) + "\n"
    if format_name == "json":
        document = ({"_comments": comments, **data} if include_comments else data)
        return json.dumps(document, indent=2, ensure_ascii=False) + "\n"

    yaml = YAML()
    yaml.default_flow_style = False
    from io import StringIO

    stream = StringIO()
    yaml.dump(_yaml_map(data, comments, include_comments=include_comments), stream)
    return stream.getvalue()


def parse(path: Path, format_name: str | None = None) -> dict[str, Any]:
    """Parse a configuration file into a plain dictionary.

    Args:
        path: Configuration file to read.
        format_name: Optional format override. By default it is inferred from
            ``path``.

    Returns:
        Parsed configuration data without JSON comment metadata.
    """
    format_name = normalize_format(format_name or format_from_path(path))
    text = path.read_text(encoding="utf-8")
    if format_name == "toml":
        return dict(tomllib.loads(text))
    if format_name == "json":
        data = json.loads(text)
        data.pop("_comments", None)
        return data
    yaml = YAML(typ="safe")
    return yaml.load(text) or {}
