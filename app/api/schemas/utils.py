from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from enum import Enum


class LoginBase(SQLModel):
    username: EmailStr
    password: str


class SocialProviderEnum(str, Enum):
    google = "google.com"
    linkedin = "linkedin.com"


class SocialLoginBase(SQLModel):
    email: EmailStr
    full_name: Optional[str]
    provider: SocialProviderEnum
    provider_id: str


class RequestDemoBase(SQLModel):
    full_name: str = Field(max_length=255)
    company_name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255, unique=True)
    phone_number: str = Field(max_length=15)
    message: str = Field(default=None, max_length=255)


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class SocialLoginToken(SQLModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool = False


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class ResetPasswordResponse(SQLModel):
    link: str | None = None