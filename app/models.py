import uuid
from pydantic import EmailStr
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from app.api.schemas.users import *


class User(UserBase, table=True):
    __tablename__ = "user"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: Optional[str] = Field(default=None)
    social_providers: List["SocialProvider"] = Relationship(
        back_populates="user")


class SocialProvider(SQLModel, table=True):
    __tablename__ = "social_provider"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, foreign_key="user.id")
    provider: str = Field(default=None)
    provider_id: str = Field(default=None)
    user: User = Relationship(back_populates="social_providers")


class RequestDemo(RequestDemoBase, table=True):
    __tablename__ = "request_demo"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
