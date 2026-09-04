"""Base models and field helpers for declarative configurations."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Optional

from pydantic import BaseModel, ConfigDict, Field, SecretStr
from pydantic import computed_field as computed

computed_field = computed

if TYPE_CHECKING:
    from .service import ConfigMaker
    from rich.console import Console


def _extra(*, optional: bool = False, secret: bool = False) -> dict[str, Any]:
    return {"optional": optional, "secret": secret}


def config_field(
    default: Any = ...,
    *,
    description: Optional[str] = None,
    optional: bool = False,
    secret: bool = False,
    **kwargs: Any,
) -> Any:
    """Declare a field that participates in configuration generation.

    Args:
        default: Default value. Omit it to make the field required in the
            generated template.
        description: Human-readable description written to generated files.
        optional: Mark the field as optional for environment validation and
            warnings.
        secret: Mark the field as sensitive for graph rendering.
        **kwargs: Additional keyword arguments forwarded to
            :class:`pydantic.Field`.

    Returns:
        A Pydantic field declaration with autoconfig metadata attached.
    """

    return Field(
        default=default,
        description=description,
        json_schema_extra=_extra(optional=optional, secret=secret),
        **kwargs,
    )


# Backward-compatible name. Sections and primitive values intentionally share
# exactly the same declaration API; the annotation carries the type.
section_field = config_field
field = config_field
computed = computed_field

class _MakerDescriptor:
    """Lazily bind a ConfigMaker to the definition that owns it."""

    def __init__(self) -> None:
        self._makers: dict[type[Any], Any] = {}

    def __get__(self, instance: Any, owner: type["ConfigurationDefinition"] | None = None) -> Any:
        if owner is None:
            return self
        from .service import ConfigMaker

        if owner not in self._makers:
            directory = getattr(owner, "config_directory", Path("."))
            self._makers[owner] = ConfigMaker(owner, directory=directory)
        return self._makers[owner]


class ConfigurationSection(BaseModel):
    """Base class for a named, validated configuration section.

    Subclass this type to create nested configuration sections. Extra keys are
    rejected and assignment validation is enabled by default.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    def print_graph(
        self,
        *,
        include_computed: bool = False,
        console: Console | None = None,
    ) -> None:
        """Render the section as a Rich table.

        Args:
            include_computed: Include computed properties in the output.
            console: Optional Rich console used for rendering.
        """
        from .graph import print_model_graph

        print_model_graph(
            self,
            include_computed=include_computed,
            console=console,
        )


class ConfigurationDefinition(ConfigurationSection):
    """Base class for a complete application configuration definition.

    Set class attributes such as ``config_name``, ``config_directory`` or
    ``env_prefix`` to customize file discovery and environment variables.
    The lazily bound :attr:`maker` service generates and loads the definition.
    """

    strict: ClassVar[bool] = False
    config_name: ClassVar[Optional[str]] = None
    config_directory: ClassVar[str | Path] = "."
    env_prefix: ClassVar[str] = "AUTOCONFIG_"
    env_nested_delimiter: ClassVar[str] = "__"
    if TYPE_CHECKING:
        maker: ClassVar["ConfigMaker[ConfigurationDefinition]"]
    else:
        maker: ClassVar[Any] = _MakerDescriptor()
