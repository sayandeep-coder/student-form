"""Schemas package exporting Pydantic schemas."""

from app.schemas.student import (
    StudentBase,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
)

__all__ = [
    "StudentBase",
    "StudentCreate",
    "StudentResponse",
    "StudentUpdate",
]
