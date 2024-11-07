import uuid
from pydantic import BaseModel, EmailStr, conint
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List


class CandidateBase(SQLModel):
    full_name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255, unique=True)
    phone_number: Optional[str] = Field(default=None, max_length=15, unique=True)
    location: Optional[str] = Field(default=None, max_length=255)
    current_job_title: Optional[str] = Field(default=None, max_length=255)
    linkedin_profile_url: Optional[str] = Field(default=None, max_length=255)
    job_titles_of_interest: Optional[str] = Field(default=None)
    total_years_of_experience: Optional[int] = Field(default=None)
    education_level: Optional[str] = Field(default=None)
    key_skills: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    general_salary_range: Optional[str] = Field(default=None, max_length=255)
    preferred_salary_type: Optional[str] = Field(default=None)
    open_to_performance_based_compensation: bool = False
    willing_to_negociate: bool = False
    minimum_acceptable_salary: Optional[conint(ge=0)] = Field(default=None)
    preferred_benefits: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    view_salary_expectations: Optional[str] = Field(default=None)
    hide_profile_from_current_employer: bool = False
    industries_of_interest: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    job_type_preferences: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    actively_looking_for_new_job: bool = False
    career_goals: Optional[str] = Field(default=None)
    professional_development_areas: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    role_specific_salary_adjustments: Optional[str] = Field(default=None)
    interested_in_salary_benchmarks: bool = False
    resume_upload: Optional[str] = Field(default=None)
    cover_letter_upload: Optional[str] = Field(default=None)
    invite_employer: bool = False
    employer_name: Optional[str] = Field(default=None, max_length=255)
    contact_person_name: Optional[str] = Field(default=None, max_length=255)
    contact_email: Optional[EmailStr] = Field(default=None, max_length=255)
    message_to_employer: Optional[str] = Field(default=None, max_length=255)
    job_alerts_frequency: Optional[str] = Field(default=None)
    referral_source: Optional[str] = Field(default=None)
    referral_code: Optional[str] = Field(default=None)
    terms_accepted: bool = Field(default=False)


class CandidateLogin(SQLModel):
    email: EmailStr
    password: str


class CandidateUpdate(CandidateBase):
    pass


class CandidateCreate(CandidateBase):
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)


class CandidatePublic(CandidateBase):
    id: uuid.UUID


class CandidatesPublic(SQLModel):
    data: List[CandidatePublic]
    count: int
