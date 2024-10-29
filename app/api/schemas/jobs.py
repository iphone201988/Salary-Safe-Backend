import uuid
from pydantic import BaseModel, EmailStr, condecimal
from sqlmodel import SQLModel, Field
from typing import Optional, List
from enum import Enum


class JobStatusEnum(str, Enum):
    active = "active"
    closed = "closed"


class JobBase(SQLModel):
    title: str
    description: str
    location: Optional[str] = Field(default=None)
    salary_min: Optional[condecimal(ge=0)] = Field(default=None)
    salary_max: Optional[condecimal(ge=0)] = Field(default=None)
    requirements: Optional[str] = Field(default=None)
    status: JobStatusEnum = Field(default="active")


class JobCreate(JobBase):
    client_id: uuid.UUID


class JobUpdate(JobBase):
    pass


class JobPublic(JobBase):
    id: uuid.UUID


class JobsPublic(SQLModel):
    data: List[JobPublic]
    count: int


class ApplicationStatusEnum(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class JobApplicationBase(SQLModel):
    status: ApplicationStatusEnum | None = Field(default=None)
    salary_expectation: Optional[condecimal(ge=0)] = Field(default=None)


class JobApplicationCreate(JobApplicationBase):
    job_id: uuid.UUID
    candidate_id: uuid.UUID


class JobApplicationUpdate(JobApplicationBase):
    pass


class JobApplicationPublic(JobApplicationBase):
    id: uuid.UUID
    job_id: uuid.UUID
    candidate_id: uuid.UUID


class JobApplicationsPublic(SQLModel):
    data: List[JobApplicationPublic]
    count: int