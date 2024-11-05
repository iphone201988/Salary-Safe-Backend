import uuid
from pydantic import EmailStr
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, Column, DateTime
from app.api.schemas.utils import RequestDemoBase
from app.api.schemas.candidates import CandidateBase
from app.api.schemas.clients import ClientBase
from app.api.schemas.jobs import JobBase, JobApplicationBase
from datetime import datetime


class RequestDemo(RequestDemoBase, table=True):
    __tablename__ = "request_demo"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.utcnow))


class Client(ClientBase, table=True):
    __tablename__ = "client_profile"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: Optional[str] = Field(default=None)
    is_super_user: bool = False
    is_active: bool = True
    mfa_enabled: bool = False
    jobs: List["Job"] = Relationship(back_populates="client", cascade_delete=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))


class Candidate(CandidateBase, table=True):
    __tablename__ = "candidate_profile"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: Optional[str] = Field(default=None)
    is_active: bool = True
    mfa_enabled: bool = True
    job_applications: List["JobApplication"] = Relationship(back_populates="candidate", cascade_delete=True)
    social_providers: List["SocialProvider"] = Relationship(back_populates="candidate", cascade_delete=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))


class SocialProvider(SQLModel, table=True):
    __tablename__ = "social_provider"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    candidate: Candidate = Relationship(back_populates="social_providers")
    candidate_id: uuid.UUID = Field(default_factory=uuid.uuid4, foreign_key="candidate_profile.id")
    provider: str = Field(default=None)
    provider_id: str = Field(default=None)


class Job(JobBase, table=True):
    __tablename__ = "job"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    client_id: uuid.UUID = Field(foreign_key="client_profile.id")
    client: Client = Relationship(back_populates="jobs")
    job_applications: List["JobApplication"] = Relationship(back_populates="job", cascade_delete=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))


class JobApplication(JobApplicationBase, table=True):
    __tablename__ = "job_application"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_id: uuid.UUID = Field(foreign_key="job.id")
    job: Job = Relationship(back_populates="job_applications")
    candidate_id: uuid.UUID = Field(foreign_key="candidate_profile.id")
    candidate: Candidate = Relationship(back_populates="job_applications")
    created_at: datetime = Field(default_factory=datetime.utcnow)
