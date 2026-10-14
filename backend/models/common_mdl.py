from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class ResponseDto(BaseModel):
    """Base for response DTOs backed by domain objects."""

    model_config = ConfigDict(from_attributes=True)


class RequestDto(BaseModel):
    """Base for request DTOs that validate client input."""


class PaginaResponseDto(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(gt=0)


class ErrorResponseDto(BaseModel):
    codigo: str
    mensaje: str


class OperacionResponseDto(BaseModel):
    resultado: str
    mensaje: str
