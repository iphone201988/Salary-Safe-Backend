import uuid
from pydantic import BaseModel, EmailStr, conint
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List


class ClientBase(SQLModel):
    email: EmailStr = Field(max_length=255)
    company_name: Optional[str] = Field(max_length=255)
    industry: Optional[str] = Field(default=None)
    company_size: Optional[str] = Field(default=None)
    headquarters_location: Optional[str] = Field(default=None, max_length=255)
    primary_contact_person: Optional[str] = Field(default=None, max_length=255)
    contact_phone_number: Optional[str] = Field(default=None, max_length=15)
    primary_hiring_goals: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    preferred_job_locations: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    roles_of_interest: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    job_types: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    dashboard_metrics: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    role_specific_customization: Optional[bool] = Field(default=False)
    enable_competitive_salary_benchmarking: bool = False
    receive_salary_adjustment_suggestions: bool = False
    candidate_viewing_preferences: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    enable_offer_optimization: bool = False
    enable_budget_analysis: bool = False
    enable_real_time_market_alerts: bool = False
    enable_custom_reporting: bool = False
    preferred_report_frequency: Optional[str] = Field(default=None)
    enable_automated_updates: bool = False
    enable_candidate_feedback_analysis: bool = False
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


class ClientPublic(ClientBase):
    id: uuid.UUID


class ClientsPublic(SQLModel):
    data: List[ClientPublic]
    count: str
