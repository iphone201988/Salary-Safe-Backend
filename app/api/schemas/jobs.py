import uuid
import datetime
from pydantic import BaseModel, EmailStr, condecimal
from sqlmodel import SQLModel, Field
from typing import Optional, List
from enum import Enum
from app.api.schemas.candidates import CandidatePublic
from app.api.schemas.clients import ClientPublic


class JobTypeEnum(str, Enum):
    fulltime = "fulltime"
    parttime = "parttime"
    internship = "internship"
    contract = "contract"
    temproray = "temporary"
    volunteer = "volunteer"
    other = "other"


class JobWorkplaceTypeEnum(str, Enum):
    onsite = "onsite"
    remote = "remote"
    hybrid = "hybrid"


class JobStatusEnum(str, Enum):
    active = "active"
    closed = "closed"


class ApplicationStatusEnum(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class JobBase(SQLModel):
    title: str
    description: str
    location: Optional[str] = Field(default=None)
    salary_min: Optional[condecimal(ge=0)] = Field(default=None)
    salary_max: Optional[condecimal(ge=0)] = Field(default=None)
    requirements: Optional[str] = Field(default=None)
    status: JobStatusEnum = Field(default="active")
    job_type: JobTypeEnum = Field(default="fulltime")
    workplace_type: JobWorkplaceTypeEnum = Field(default="onsite")


class JobCreate(JobBase):
    client_id: uuid.UUID = Field(default=None)
    pass


class JobUpdate(JobBase):
    pass


class JobSearch(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    status: Optional[JobStatusEnum] = None
    job_type: Optional[JobTypeEnum] = None
    workplace_type: Optional[JobWorkplaceTypeEnum] = None
    skip: int = 0
    limit: int = 100


class JobPublic(JobBase):
    application_status: Optional[ApplicationStatusEnum] = None
    client_details: Optional[ClientPublic] = None
    created_at: datetime.datetime
    id: uuid.UUID


class JobsPublic(SQLModel):
    data: List[JobPublic]
    count: int


class JobInsightsRequest(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    min_salary: Optional[condecimal(ge=0)] = None
    max_salary: Optional[condecimal(ge=0)] = None
    requirements: Optional[str] = None
    status: Optional[JobStatusEnum] = None
    job_type: Optional[JobTypeEnum] = None
    workplace_type: Optional[JobWorkplaceTypeEnum] = None


class TopCompany(BaseModel):
    company_name: str
    job_count: int


class JobTypeDistribution(BaseModel):
    job_type: str
    count: int


class SalaryRangeDistribution(BaseModel):
    range: str
    count: int


class MarketInsightsResponse(BaseModel):
    average_salary: Optional[float]
    total_jobs: int
    top_companies: List[TopCompany]
    job_type_distribution: List[JobTypeDistribution]
    salary_distribution: List[SalaryRangeDistribution]


class JobApplicationBase(SQLModel):
    status: ApplicationStatusEnum = Field(default="pending")
    salary_expectation: condecimal(ge=0) = Field(default=None)


class JobApplicationCreate(JobApplicationBase):
    job_id: uuid.UUID
    candidate_id: uuid.UUID = Field(default=None)


class JobApplicationUpdate(JobApplicationBase):
    pass


class JobApplicationStatusUpdate(BaseModel):
    status: ApplicationStatusEnum


class JobApplicationPublic(JobApplicationBase):
    job_details: Optional[JobPublic] = None
    candidate_details: Optional[CandidatePublic] = None
    created_at: datetime.datetime
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    id: uuid.UUID


class JobApplicationsPublic(SQLModel):
    data: List[JobApplicationPublic]
    count: int


class CreateSkill(SQLModel):
    name: str
    weight: float = 1.0
    market_premium: float = 0.0
