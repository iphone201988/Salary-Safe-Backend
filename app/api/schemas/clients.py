import uuid
from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field
from typing import Optional, List


class ClientBase(SQLModel):
    company_name: Optional[str] | None = Field(default=None, max_length=255)
    industry: Optional[str] = Field(default=None)
    size: Optional[int] = Field(default=None)


class ClientCreate(ClientBase):
    user_id: uuid.UUID


class ClientUpdate(ClientBase):
    pass


class ClientPublic(ClientBase):
    id: uuid.UUID


class ClientsPublic(SQLModel):
    data: List[ClientPublic]
    count: str