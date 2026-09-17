"""Configuration generation, loading, merging and validation."""

from __future__ import annotations

import warnings
import json
import os
from pathlib import Path
from typing import Any, Generic, Mapping, Type, TypeVar, get_args

from pydantic import ValidationError

from .formats import format_from_path, normalize_format, parse, serialize
from .models import ConfigurationDefinition
from .schema import (
    build_comments,
    build_template,
    field_extra,
    is_list_type,
    is_section_type,
    unwrap_type,
)

T = TypeVar("T", bound=ConfigurationDefinition)


class ConfigFileExistsError(FileExistsError):
    """Raised when generation would overwrite a file without permission."""

    def __init__(self, path: Path) -> None:
        super().__init__(
            f"Configuration file already exists: {path}. "
            "Use recreate=True to replace it."
        )


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def _missing_optional_fields(model_type: Type[ConfigurationDefinition], data: dict[str, Any], prefix: str = "") -> list[str]:
    missing: list[str] = []
    for name, field in model_type.model_fields.items():
        path = f"{prefix}.{name}" if prefix else name
        extra = field_extra(field)
        if name not in data:
            if extra.get("optional"):
                missing.append(path)
            continue
        value = data[name]
        section_type = unwrap_type(field.annotation)
        if is_section_type(section_type) and isinstance(value, dict):
            missing.extend(_missing_optional_fields(section_type, value, path))
        elif is_list_type(field.annotation) and isinstance(value, list):
            args = get_args(field.annotation)
            item_type = unwrap_type(args[0]) if args else Any
            if is_section_type(item_type):
                for index, item in enumerate(value):
                    if isinstance(item, dict):
                        missing.extend(_missing_optional_fields(item_type, item, f"{path}.{index}"))
    return missing


def _missing_strict_fields(model_type: Type[ConfigurationDefinition], data: dict[str, Any], prefix: str = "") -> list[str]:
    """Return non-optional fields that are not explicit in an environment file."""

    missing: list[str] = []
    for name, field in model_type.model_fields.items():
        path = f"{prefix}.{name}" if prefix else name
        extra = field_extra(field)
        section_type = unwrap_type(field.annotation)
        if name not in data:
            if extra.get("optional"):
                continue
            missing.append(path)
            continue
        value = data[name]
        if is_section_type(section_type) and isinstance(value, dict):
            missing.extend(_missing_strict_fields(section_type, value, path))
        elif is_list_type(field.annotation) and isinstance(value, list):
            args = get_args(field.annotation)
            item_type = unwrap_type(args[0]) if args else Any
            if is_section_type(item_type):
                for index, item in enumerate(value):
                    if isinstance(item, dict):
                        missing.extend(_missing_strict_fields(item_type, item, f"{path}.{index}"))
    return missing


def _decode_environment_value(value: str) -> Any:
    stripped = value.strip()
    if stripped.startswith(("[", "{")):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return value
    return value


def _set_environment_value(target: dict[str, Any], parts: list[str], value: Any) -> None:
    current: Any = target
    for index, part in enumerate(parts):
        last = index == len(parts) - 1
        next_is_index = not last and parts[index + 1].isdigit()
        if isinstance(current, list):
            if not part.isdigit():
                return
            item_index = int(part)
            while len(current) <= item_index:
                current.append(None)
            if last:
                current[item_index] = value
            else:
                if current[item_index] is None:
                    current[item_index] = [] if next_is_index else {}
                current = current[item_index]
        else:
            key = part.lower()
            if last:
                current[key] = value
            else:
                if key not in current or current[key] is None:
                    current[key] = [] if next_is_index else {}
                current = current[key]


def _environment_data(
    definition: Type[ConfigurationDefinition],
    environ: Mapping[str, str],
) -> dict[str, Any]:
    prefix = definition.env_prefix
    delimiter = definition.env_nested_delimiter
    result: dict[str, Any] = {}
    for name, value in environ.items():
        if not name.startswith(prefix):
            continue
        field_path = name[len(prefix):]
        if not field_path:
            continue
        parts = field_path.split(delimiter)
        _set_environment_value(result, parts, _decode_environment_value(value))
    return result


class ConfigMaker(Generic[T]):
    """Generate, load and validate one concrete configuration definition.

    The loading precedence is environment-specific file, base file, process
    environment variables, and finally Pydantic defaults.
    """

    def __init__(self, definition: Type[T], directory: str | Path = ".", config_name: str | None = None) -> None:
        """Create a maker for ``definition``.

        Args:
            definition: Configuration model to generate and validate.
            directory: Directory containing configuration files.
            config_name: Base filename without extension. Defaults to the
                definition's ``config_name`` or ``config``.
        """
        self.definition = definition
        self.directory = Path(directory)
        self.config_name = config_name or definition.config_name or "config"
        self._last_format = "toml"

    def path_for(self, *, environment: str | None = None, format_name: str | None = None) -> Path:
        """Return the expected path for a base or environment file."""
        format_name = normalize_format(format_name or self._last_format)
        filename = f"{self.config_name}.{format_name}"
        if environment:
            filename = f"{self.config_name}.{environment}.{format_name}"
        return self.directory / filename

    def generate(
        self,
        *,
        environment: str | None = None,
        path: str | Path | None = None,
        format_name: str | None = None,
        recreate: bool = False,
        force: bool | None = None,
        uncommented: bool = False,
    ) -> Path:
        """Generate a configuration template on disk.

        Args:
            environment: Optional environment suffix such as ``development``.
            path: Explicit output path. If omitted, derive it from the maker.
            format_name: Output format. Defaults to the most recently used
                format, initially TOML.
            recreate: Allow replacing an existing file.
            force: Backward-compatible alias for ``recreate``.
            uncommented: Omit comments and JSON comment metadata.

        Returns:
            The path of the generated file.

        Raises:
            ConfigFileExistsError: If the destination exists and replacement
                was not requested.
        """
        if force is not None:
            recreate = force
        if format_name:
            self._last_format = normalize_format(format_name)
        output = Path(path) if path else self.path_for(environment=environment, format_name=format_name)
        if path:
            self._last_format = format_from_path(output)
        format_name = self._last_format
        if output.exists() and not recreate:
            raise ConfigFileExistsError(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            serialize(
                build_template(self.definition),
                format_name,
                None if uncommented else build_comments(self.definition),
            ),
            encoding="utf-8",
        )
        return output

    def load(
        self,
        *,
        environment: str | None = None,
        path: str | Path | None = None,
        format_name: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> T:
        """Load, merge and validate a configuration.

        Args:
            environment: Optional environment name used to locate an override
                file such as ``config.development.toml``.
            path: Explicit base configuration path.
            format_name: Format override when loading the derived base path.
            env: Optional process-environment mapping, useful for tests. When
                omitted, ``os.environ`` is read.

        Returns:
            A validated instance of the configured definition type.

        Raises:
            FileNotFoundError: If a strict environment file is missing.
            ValueError: If a strict environment omits required fields.
            pydantic.ValidationError: If merged values are invalid.
        """
        base_path = Path(path) if path else self.path_for(format_name=format_name)
        if path:
            format_name = format_from_path(base_path)
        else:
            format_name = normalize_format(format_name or self._last_format)
        base = parse(base_path, format_name) if base_path.exists() else {}

        environment_data: dict[str, Any] = {}
        if environment:
            env_path = self.path_for(environment=environment, format_name=format_name)
            if env_path.exists():
                environment_data = parse(env_path, format_name)
            elif self.definition.strict:
                raise FileNotFoundError(f"Strict environment file does not exist: {env_path}")
            else:
                warnings.warn(f"Environment file does not exist: {env_path}", UserWarning, stacklevel=2)

        environment_values = _environment_data(
            self.definition,
            os.environ if env is None else env,
        )
        if environment and self.definition.strict:
            data = _merge(environment_values, environment_data)
        else:
            data = _merge(_merge(environment_values, base), environment_data)
        if environment and self.definition.strict:
            missing = _missing_strict_fields(self.definition, data)
            if missing:
                raise ValueError(
                    "Strict environment is missing required fields: " + ", ".join(missing)
                )
        if environment and not self.definition.strict:
            for field_name in _missing_optional_fields(self.definition, data):
                warnings.warn(f"Optional configuration field is missing: {field_name}", UserWarning, stacklevel=2)

        try:
            return self.definition.model_validate(data)
        except ValidationError:
            raise
