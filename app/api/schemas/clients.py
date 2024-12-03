import uuid
from pydantic import BaseModel, EmailStr, conint
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List


class ClientBase(SQLModel):
    email: EmailStr = Field(max_length=255, unique=True)
    company_name: Optional[str] = Field(max_length=255)
    industry: Optional[str] = Field(default=None)
    company_size: Optional[str] = Field(default=None)
    headquarters_location: Optional[str] = Field(default=None, max_length=255)
    primary_contact_person: Optional[str] = Field(default=None, max_length=255)
    contact_phone_number: Optional[str] = Field(default=None, max_length=15, unique=True)
    primary_hiring_goals: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    preferred_job_locations: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    roles_of_interest: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    job_types: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    dashboard_metrics: Optional[str] = Field(default=None)
    role_specific_customization: Optional[bool] = Field(default=False)
    salary_benchmarking_preference: Optional[str] = Field(default=None)
    candidate_viewing_preferences: Optional[str] = Field(default=None)
    offer_optimization: Optional[str] = Field(default=None)
    enable_real_time_market_alerts: bool = False
    enable_custom_reporting: bool = False
    preferred_report_frequency: Optional[str] = Field(default=None)
    automated_updates: Optional[str] = Field(default=None)
    candidate_feedback_analysis: Optional[str] = Field(default=None)
    invite_team_member: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    referral_source: Optional[str] = Field(default=None)
    referral_code: Optional[str] = Field(default=None)
    terms_accepted: bool = Field(default=False)


class ClientLogin(SQLModel):
    email: EmailStr
    password: str


class ClientCreate(ClientBase):
    password: str = Field(min_length=8, max_length=40)


class ClientUpdate(ClientBase):
    pass


class ClientPrivate(SQLModel):
    id: uuid.UUID
    email: Optional[EmailStr] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    headquarters_location: Optional[str] = None


class ClientPublic(ClientBase):
    id: uuid.UUID


class ClientsPublic(SQLModel):
    data: List[ClientPublic]
    count: str
