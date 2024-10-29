import uuid
from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field
from typing import Optional, List


class CandidateBase(SQLModel):
    experience: Optional[str] = Field(default=None)
    qualifications: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    salary_expectation: Optional[float] = Field(default=None)


class CandidateUpdate(CandidateBase):
    pass


class CandidateCreate(CandidateBase):
    user_id: uuid.UUID


class CandidatePublic(CandidateBase):
    id: uuid.UUID


class CandidatesPublic(SQLModel):
    data: List[CandidatePublic]
    count: int
