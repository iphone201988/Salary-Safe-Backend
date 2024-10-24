import uuid
from enum import Enum
from pydantic import BaseModel, EmailStr
from sqlmodel import Field, Relationship, SQLModel
from app.models import *


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    role: str | None = Field(default=None, max_length=255)
    report_prefrence: bool = True
    notification_prefrence: bool = True


class UserCreate(UserBase):
    password: str = Field(default=None, min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(
        default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    role: str | None = Field(default=None, max_length=255)
    report_prefrence: bool = True
    notification_prefrence: bool = True


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class ResetPasswordResponse(SQLModel):
    link: str | None = None


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


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


class RequestDemoBase(SQLModel):
    full_name: str = Field(max_length=255)
    company_name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255, unique=True)
    phone_number: str = Field(max_length=15)
    message: str = Field(default=None, max_length=255)
