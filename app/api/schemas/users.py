import uuid
from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel


class RoleEnum(str, Enum):
    candidate = "candidate"
    client = "client"


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_verified: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    role: RoleEnum | None = Field(default=None)
    report_prefrence: bool = True
    notification_prefrence: bool = True


class UserCreate(UserBase):
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)
    role: Optional[RoleEnum] = Field(default=None)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
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


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class RequestDemoBase(SQLModel):
    full_name: str = Field(max_length=255)
    company_name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255, unique=True)
    phone_number: str = Field(max_length=15)
    message: str = Field(default=None, max_length=255)
