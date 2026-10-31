"""Pydantic schemas and validation for Student entities."""

from datetime import date, datetime
import re
from typing import Optional
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


PHONE_REGEX = re.compile(r"^\+?[0-9\s\-().]{7,20}$")


class StudentBase(BaseModel):
    """Base schema defining shared student attributes and field validation."""

    full_name: str = Field(..., max_length=150, description="Full name of the student")
    date_of_birth: Optional[date] = Field(None, description="Date of birth (cannot be in the future)")
    gender: Optional[str] = Field(None, max_length=30, description="Gender of the student")
    phone_number: str = Field(..., max_length=20, description="Contact phone number")
    email: EmailStr = Field(..., max_length=255, description="Email address")
    current_address: str = Field(..., max_length=1000, description="Current residential address")

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if v is None:
            raise ValueError("Full name is required.")
        v = v.strip()
        if not v:
            raise ValueError("Full name cannot be blank or whitespace.")
        if len(v) > 150:
            raise ValueError("Full name cannot exceed 150 characters.")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if len(v) > 30:
            raise ValueError("Gender cannot exceed 30 characters.")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        if v is None:
            raise ValueError("Phone number is required.")
        v = v.strip()
        if not v:
            raise ValueError("Phone number cannot be blank.")
        if len(v) > 20:
            raise ValueError("Phone number cannot exceed 20 characters.")
        if not PHONE_REGEX.match(v):
            raise ValueError("Phone number format is invalid.")
        digits = re.sub(r"\D", "", v)
        if len(digits) < 7:
            raise ValueError("Phone number must contain at least 7 digits.")
        if len(digits) > 15:
            raise ValueError("Phone number cannot exceed 15 digits.")
        return v

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: EmailStr) -> str:
        if v is None:
            raise ValueError("Email is required.")
        return str(v).strip().lower()

    @field_validator("current_address")
    @classmethod
    def validate_current_address(cls, v: str) -> str:
        if v is None:
            raise ValueError("Current address is required.")
        v = v.strip()
        if not v:
            raise ValueError("Current address cannot be blank or whitespace.")
        if len(v) > 1000:
            raise ValueError("Current address cannot exceed 1000 characters.")
        return v


class StudentCreate(StudentBase):
    """Schema for creating a new student record."""

    pass


class StudentUpdate(BaseModel):
    """Schema for partially updating an existing student record."""

    full_name: Optional[str] = Field(None, max_length=150)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=30)
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = Field(None, max_length=255)
    current_address: Optional[str] = Field(None, max_length=1000)

    @field_validator("full_name")
    @classmethod
    def validate_update_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Full name cannot be blank or whitespace.")
        if len(v) > 150:
            raise ValueError("Full name cannot exceed 150 characters.")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_update_date_of_birth(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return v

    @field_validator("gender")
    @classmethod
    def validate_update_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if len(v) > 30:
            raise ValueError("Gender cannot exceed 30 characters.")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_update_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Phone number cannot be blank.")
        if len(v) > 20:
            raise ValueError("Phone number cannot exceed 20 characters.")
        if not PHONE_REGEX.match(v):
            raise ValueError("Phone number format is invalid.")
        digits = re.sub(r"\D", "", v)
        if len(digits) < 7:
            raise ValueError("Phone number must contain at least 7 digits.")
        if len(digits) > 15:
            raise ValueError("Phone number cannot exceed 15 digits.")
        return v

    @field_validator("email")
    @classmethod
    def normalize_update_email(cls, v: Optional[EmailStr]) -> Optional[str]:
        if v is None:
            return v
        return str(v).strip().lower()

    @field_validator("current_address")
    @classmethod
    def validate_update_current_address(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Current address cannot be blank or whitespace.")
        if len(v) > 1000:
            raise ValueError("Current address cannot exceed 1000 characters.")
        return v

    @model_validator(mode="after")
    def validate_non_nullable_fields_and_presence(self) -> "StudentUpdate":
        # Check non-nullable fields when explicitly supplied
        non_nullable = {"full_name", "phone_number", "email", "current_address"}
        for field in non_nullable:
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"Field '{field}' cannot be null.")
        return self


class StudentResponse(BaseModel):
    """Schema for serializing student responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone_number: str
    email: str
    current_address: str
    created_at: datetime
    updated_at: datetime
