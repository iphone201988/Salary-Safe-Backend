import uuid
from typing import Any
from datetime import timedelta

from fastapi import (
    APIRouter, Depends, HTTPException,
    File, UploadFile, Form
)
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


@router.post("/register", response_model=Token)
async def register_candidate(
    session: SessionDep,
    candidate_in: CandidateCreate
) -> Token:
    """
    Register a new candidate.
    """
    # Check if the email is already registered
    existing_user_email = (
        crud.get_client_by_email(session=session, email=candidate_in.email) or
        crud.get_candidate_by_email(session=session, email=candidate_in.email)
    )
    if existing_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if the phone number is already registered
    if candidate_in.phone_number:
        existing_phone_number = (
            crud.get_client_by_phone_number(session=session, phone_number=candidate_in.phone_number) or
            crud.get_candidate_by_phone_number(session=session, phone_number=candidate_in.phone_number)
        )
        if existing_phone_number:
            raise HTTPException(status_code=400, detail="Phone number already registered")

    candidate = crud.create_candidate(session=session, candidate_in=candidate_in)

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return Token(
        access_token=security.create_access_token(
            candidate.id, expires_delta=access_token_expires
        )
    )


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
async def update_current_candidate(
    session: SessionDep,
    current_user: CurrentUser,
    full_name: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    current_job_title: Optional[str] = Form(None),
    linkedin_profile_url: Optional[str] = Form(None),
    job_titles_of_interest: Optional[str] = Form(None),
    total_years_of_experience: Optional[int] = Form(None),
    education_level: Optional[str] = Form(None),
    key_skills: Optional[List[str]] = Form([]),
    general_salary_range: Optional[str] = Form(None),
    preferred_salary_type: Optional[str] = Form(None),
    open_to_performance_based_compensation: Optional[bool] = Form(None),
    willing_to_negociate: Optional[bool] = Form(None),
    minimum_acceptable_salary: Optional[int] = Form(None),
    preferred_benefits: Optional[List[str]] = Form([]),
    view_salary_expectations: Optional[str] = Form(None),
    hide_profile_from_current_employer: Optional[bool] = Form(None),
    industries_of_interest: Optional[List[str]] = Form([]),
    job_type_preferences: Optional[List[str]] = Form([]),
    actively_looking_for_new_job: Optional[bool] = Form(None),
    career_goals: Optional[str] = Form(None),
    professional_development_areas: Optional[List[str]] = Form([]),
    role_specific_salary_adjustments: Optional[str] = Form(None),
    interested_in_salary_benchmarks: Optional[bool] = Form(None),
    invite_employer: Optional[List[str]] = Form([]),
    notification_preferences: Optional[List[str]] = Form([]),
    job_alerts_frequency: Optional[str] = Form(None),
    referral_source: Optional[str] = Form(None),
    referral_code: Optional[str] = Form(None),
    terms_accepted: Optional[bool] = Form(None),
    avatar: Optional[UploadFile] = Form(None),
    resume_upload: Optional[UploadFile] = Form(None),
    cover_letter_upload: Optional[UploadFile] = Form(None),
) -> Any:
    """
    Update the currently logged-in candidate's profile.
    """
    candidate = crud.get_candidate_by_email(
        session=session, email=current_user.email
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    avatar = await save_file(avatar, "avatar") if avatar else None
    resume_url = await save_file(resume_upload, "resumes") if resume_upload else None
    cover_letter_url = (
        await save_file(cover_letter_upload, "cover_letters") if cover_letter_upload else None
    )

    candidate_data = {
        "full_name": full_name,
        "email": current_user.email,
        "phone_number": phone_number,
        "location": location,
        "current_job_title": current_job_title,
        "linkedin_profile_url": linkedin_profile_url,
        "job_titles_of_interest": job_titles_of_interest,
        "total_years_of_experience": total_years_of_experience,
        "education_level": education_level,
        "key_skills": key_skills or None,
        "general_salary_range": general_salary_range,
        "preferred_salary_type": preferred_salary_type,
        "open_to_performance_based_compensation": open_to_performance_based_compensation,
        "willing_to_negociate": willing_to_negociate,
        "minimum_acceptable_salary": minimum_acceptable_salary,
        "preferred_benefits": preferred_benefits or None,
        "view_salary_expectations": view_salary_expectations,
        "hide_profile_from_current_employer": hide_profile_from_current_employer,
        "industries_of_interest": industries_of_interest or None,
        "job_type_preferences": job_type_preferences or None,
        "actively_looking_for_new_job": actively_looking_for_new_job,
        "career_goals": career_goals,
        "professional_development_areas": professional_development_areas or None,
        "role_specific_salary_adjustments": role_specific_salary_adjustments,
        "interested_in_salary_benchmarks": interested_in_salary_benchmarks,
        "avatar": avatar,
        "resume_upload": resume_url,
        "cover_letter_upload": cover_letter_url,
        "invite_employer": invite_employer or None,
        "notification_preferences": notification_preferences or None,
        "job_alerts_frequency": job_alerts_frequency,
        "referral_source": referral_source,
        "referral_code": referral_code,
        "terms_accepted": terms_accepted,
    }

    filtered_data = {k: v for k, v in candidate_data.items() if v is not None}
    candidate_in = CandidateUpdate(**filtered_data)

    updated_candidate = crud.update_candidate(
        session=session, db_candidate=candidate, candidate_in=candidate_in
    )

    return updated_candidate


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
