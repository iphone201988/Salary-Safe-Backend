import uuid
from typing import Any
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form
from sqlmodel import func, select

from app import crud
from app.utils import save_file
from app.core import security
from app.core.config import settings
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import Candidate
from app.api.schemas.candidates import *
from app.api.schemas.utils import (
    Message, Token, SocialLoginBase
)

router = APIRouter()


@router.post("/register", response_model=CandidatePublic)
async def register_candidate(
    session: SessionDep,
    full_name: str = Form(...),
    email: EmailStr = Form(...),
    password: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    current_job_title: Optional[str] = Form(None),
    linkedin_profile_url: Optional[str] = Form(None),
    job_titles_of_interest: Optional[str] = Form(None),
    total_years_of_experience: Optional[int] = Form(None),
    education_level: Optional[str] = Form(None),
    key_skills: Optional[List[str]] = Form(None),
    general_salary_range: Optional[str] = Form(None),
    preferred_salary_type: Optional[str] = Form(None),
    open_to_performance_based_compensation: bool = Form(False),
    willing_to_negociate: bool = Form(False),
    minimum_acceptable_salary: Optional[int] = Form(None),
    preferred_benefits: Optional[List[str]] = Form(None),
    view_salary_expectations: Optional[str] = Form(None),
    hide_profile_from_current_employer: bool = Form(False),
    industries_of_interest: Optional[List[str]] = Form(None),
    job_type_preferences: Optional[List[str]] = Form(None),
    actively_looking_for_new_job: bool = Form(False),
    career_goals: Optional[str] = Form(None),
    professional_development_areas: Optional[List[str]] = Form(None),
    role_specific_salary_adjustments: Optional[str] = Form(None),
    interested_in_salary_benchmarks: bool = Form(False),
    invite_employer: bool = Form(False),
    employer_name: Optional[str] = Form(None),
    contact_person_name: Optional[str] = Form(None),
    contact_email: Optional[EmailStr] = Form(None),
    message_to_employer: Optional[str] = Form(None),
    job_alerts_frequency: Optional[str] = Form(None),
    referral_source: Optional[str] = Form(None),
    referral_code: Optional[str] = Form(None),
    terms_accepted: bool = Form(...),
    resume_upload: Optional[UploadFile] = None,
    cover_letter_upload: Optional[UploadFile] = None,
) -> Any:
    """
    Register a new candidate.
    """
    # Check if the email is already registered
    existing_user = (
        crud.get_client_by_email(session=session, email=email) or
        crud.get_candidate_by_email(session=session, email=email)
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    resume_url, cover_letter_url = None, None
    if resume_upload:
        resume_url = await save_file(resume_upload, "resumes")
    if cover_letter_upload:
        cover_letter_url = await save_file(cover_letter_upload, "cover_letters")

    # Create candidate input data dictionary
    candidate_data = {
        "full_name": full_name,
        "email": email,
        "password": password,
        "phone_number": phone_number,
        "location": location,
        "current_job_title": current_job_title,
        "linkedin_profile_url": linkedin_profile_url,
        "job_titles_of_interest": job_titles_of_interest,
        "total_years_of_experience": total_years_of_experience,
        "education_level": education_level,
        "key_skills": key_skills,
        "general_salary_range": general_salary_range,
        "preferred_salary_type": preferred_salary_type,
        "open_to_performance_based_compensation": open_to_performance_based_compensation,
        "willing_to_negociate": willing_to_negociate,
        "minimum_acceptable_salary": minimum_acceptable_salary,
        "preferred_benefits": preferred_benefits,
        "view_salary_expectations": view_salary_expectations,
        "hide_profile_from_current_employer": hide_profile_from_current_employer,
        "industries_of_interest": industries_of_interest,
        "job_type_preferences": job_type_preferences,
        "actively_looking_for_new_job": actively_looking_for_new_job,
        "career_goals": career_goals,
        "professional_development_areas": professional_development_areas,
        "role_specific_salary_adjustments": role_specific_salary_adjustments,
        "interested_in_salary_benchmarks": interested_in_salary_benchmarks,
        "resume_upload": resume_url,
        "cover_letter_upload": cover_letter_url,
        "invite_employer": invite_employer,
        "employer_name": employer_name,
        "contact_person_name": contact_person_name,
        "contact_email": contact_email,
        "message_to_employer": message_to_employer,
        "job_alerts_frequency": job_alerts_frequency,
        "referral_source": referral_source,
        "referral_code": referral_code,
        "terms_accepted": terms_accepted,
    }
    candidate = crud.create_candidate(session=session, candidate_in=candidate_data)
    return candidate


@router.post("/login", response_model=Token)
def login_candidate(candidate_in: CandidateLogin, session: SessionDep) -> Any:
    """
    Log in a candidate and return a token.
    """
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    candidate = crud.authenticate_candidate(
        session=session, email=candidate_in.email, password=candidate_in.password
    )
    if not candidate:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    elif not candidate.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return Token(
        access_token=security.create_access_token(
            candidate.id, expires_delta=access_token_expires
        )
    )


@router.post("/social-login")
def login_social_candidate(session: SessionDep, login_request: SocialLoginBase) -> Token:
    """
    Handle social login and return an access token.
    """
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Use create_or_update_user to either create or authenticate the user
    user, is_new_user = crud.create_or_update_user(
        session=session, user_in=login_request
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="User not found, Please contact support")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    if is_new_user:
        return SocialLoginToken(
            access_token=security.create_access_token(
                str(candidate.id), expires_delta=access_token_expires
            ),
            is_new_user=is_new_user
        )
    else:
        return Token(
            access_token=security.create_access_token(
                str(candidate.id), expires_delta=access_token_expires
            )
        )


@router.get("/me", response_model=CandidatePublic)
def get_current_candidate(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get the currently logged-in candidate's profile.
    """
    candidate = crud.get_candidate_by_email(session=session, email=current_user.email)
    if not candidate:
        raise HTTPException(
            status_code=404, detail="Candidate profile not found")

    return candidate


@router.get("/{candidate_id}", response_model=CandidatePublic)
def get_candidate_by_id(
    candidate_id: uuid.UUID, session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Get a specific candidate by id.
    """
    candidate = session.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.patch("/me", response_model=CandidatePublic)
def update_current_candidate(
    session: SessionDep, candidate_in: CandidateUpdate, current_user: CurrentUser
) -> Any:
    """
    Update the currently logged-in candidate's profile.
    """
    candidate = crud.get_candidate_by_email(session=session, email=current_user.email)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate = crud.update_candidate(
        session=session, db_candidate=candidate, candidate_in=candidate_in)
    return candidate


@router.delete("/me", response_model=Message)
def delete_current_candidate(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Delete the currently logged-in candidate's profile.
    """
    candidate = crud.get_candidate_by_email(session=session, email=current_user.email)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    session.delete(candidate)
    session.commit()
    return Message(message="Candidate deleted successfully")
