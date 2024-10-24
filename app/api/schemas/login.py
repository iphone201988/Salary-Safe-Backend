from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models import *


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
