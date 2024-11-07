import uuid
from typing import Any
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, UploadFile
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
    candidate_in: CandidateCreate,
    session: SessionDep,
    resume_upload: Optional[UploadFile] = None,
    cover_letter_upload: Optional[UploadFile] = None
) -> Any:
    """
    Register a new candidate.
    """
    # Check if the email is already registered
    existing_user = (
        crud.get_client_by_email(session=session, email=candidate_in.email) or
        crud.get_candidate_by_email(session=session, email=candidate_in.email)
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Save resume and cover letter if uploaded
    if resume_upload:
        candidate_in.resume_upload = await save_file(resume_upload, "resumes")
    if cover_letter_upload:
        candidate_in.cover_letter_upload = await save_file(cover_letter_upload, "cover_letters")

    # Register the candidate
    candidate = crud.create_candidate(session=session, candidate_in=candidate_in)
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
