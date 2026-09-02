"""Helpers that turn a Pydantic configuration definition into a template."""

from __future__ import annotations

from enum import Enum
import inspect
from types import UnionType
from typing import Any, Type, Union, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import PydanticUndefined

from .models import ConfigurationSection


def field_extra(field: Any) -> dict[str, Any]:
    """Return autoconfig metadata stored on a Pydantic field."""
    extra = field.json_schema_extra
    return extra if isinstance(extra, dict) else {}


def unwrap_type(annotation: Any) -> Any:
    """Remove a single ``None`` member from an optional union annotation."""
    origin = get_origin(annotation)
    if origin in (Union, UnionType):
        non_none = [item for item in get_args(annotation) if item is not type(None)]
        if len(non_none) == 1:
            return unwrap_type(non_none[0])
    return annotation


def is_section_type(annotation: Any) -> bool:
    """Return whether an annotation resolves to a configuration section."""
    annotation = unwrap_type(annotation)
    return isinstance(annotation, type) and issubclass(annotation, ConfigurationSection)


def is_list_type(annotation: Any) -> bool:
    """Return whether an annotation resolves to ``list[T]``."""
    return get_origin(unwrap_type(annotation)) is list


def list_item_type(annotation: Any) -> Any:
    """Return the item annotation from a list type, or ``Any`` if unknown."""
    args = get_args(unwrap_type(annotation))
    return args[0] if args else Any


def section_type_for_annotation(annotation: Any) -> Type[ConfigurationSection] | None:
    """Find a section type directly or inside ``list[Section]``."""
    annotation = unwrap_type(annotation)
    if is_section_type(annotation):
        return annotation
    if is_list_type(annotation):
        item_type = unwrap_type(list_item_type(annotation))
        if is_section_type(item_type):
            return item_type
    return None


def _placeholder(annotation: Any) -> Any:
    annotation = unwrap_type(annotation)
    origin = get_origin(annotation)

    if is_list_type(annotation):
        return [_placeholder(list_item_type(annotation)), _placeholder(list_item_type(annotation))]
    if annotation is bool:
        return False
    if annotation is int:
        return 0
    if annotation is float:
        return 0.0
    if annotation is str:
        return "CHANGE_ME"
    if origin in (set, tuple):
        return []
    if origin is dict:
        return {}
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return next(iter(annotation)).value
    if is_section_type(annotation):
        return build_template(annotation)
    return "CHANGE_ME"


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "get_secret_value"):
        return value.get_secret_value()
    if isinstance(value, BaseModel):
        return {
            key: _plain(item)
            for key, item in value.model_dump(mode="python").items()
            if item is not None
        }
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items() if item is not None}
    if isinstance(value, (list, tuple, set)):
        return [_plain(item) for item in value]
    return value


def build_template(model_type: Type[ConfigurationSection]) -> dict[str, Any]:
    """Build a serializable template without evaluating computed fields.

    Required lists receive two representative items so users can edit the
    generated configuration immediately.
    """

    result: dict[str, Any] = {}
    for name, field in model_type.model_fields.items():
        extra = field_extra(field)
        annotation = unwrap_type(field.annotation)

        if field.is_required():
            value = _placeholder(annotation)
        elif field.default is not PydanticUndefined:
            value = field.default
        elif field.default_factory is not None:
            value = field.default_factory()
        else:
            value = None

        if is_list_type(annotation) and value == [] and field.is_required():
            value = _placeholder(annotation)
        if value is None:
            if extra.get("optional"):
                continue
            continue
        if extra.get("secret") and value == "":
            continue
        if is_section_type(annotation) or is_list_type(annotation):
            if isinstance(value, ConfigurationSection):
                value = _plain(value)
            elif is_section_type(annotation) and not isinstance(value, dict):
                value = build_template(annotation)
            else:
                value = _plain(value)
        result[name] = _plain(value)
    return result


def build_comments(model_type: Type[ConfigurationSection], prefix: str = "") -> dict[str, str]:
    """Collect field and section descriptions keyed by dotted field path."""
    comments: dict[str, str] = {}
    for name, field in model_type.model_fields.items():
        path = f"{prefix}.{name}" if prefix else name
        extra = field_extra(field)
        description = field.description
        section_type = section_type_for_annotation(field.annotation)
        if section_type is not None:
            title = name.replace("_", " ").title()
            raw_docstring = getattr(section_type, "__doc__", None)
            section_comment = (inspect.cleandoc(raw_docstring) if raw_docstring else None) or description or ""
            if extra.get("optional"):
                section_comment = f"{section_comment} Optional section".strip()
            if section_comment:
                comments[path] = section_comment
            comments.update(build_comments(section_type, path))
        elif description:
            comments[path] = description
    return comments
