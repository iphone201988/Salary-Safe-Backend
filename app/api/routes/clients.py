import uuid
from typing import Any
from datetime import timedelta

from fastapi import (
    APIRouter, Depends, HTTPException,
    File, UploadFile, Form
)
from sqlmodel import func, select

from app import crud
from app.core import security
from app.core.config import settings
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import Client
from app.api.schemas.clients import *
from app.api.schemas.utils import Message, Token

router = APIRouter()


@router.post("/register", response_model=ClientPublic)
def register_client(client_in: ClientCreate, session: SessionDep) -> Any:
    """
    Register a new client.
    """

    # Check if the email is already registered
    existing_user_email = (
        crud.get_client_by_email(session=session, email=client_in.email) or
        crud.get_candidate_by_email(session=session, email=client_in.email)
    )
    if existing_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if the phone number is already registered
    if client_in.contact_phone_number:
        existing_phone_number = (
            crud.get_client_by_phone_number(session=session, phone_number=client_in.contact_phone_number) or
            crud.get_candidate_by_phone_number(session=session, phone_number=client_in.contact_phone_number)
        )
        if existing_phone_number:
            raise HTTPException(status_code=400, detail="Phone number already registered")


    client = crud.create_client(session=session, client_in=client_in)
    return client


@router.post("/login", response_model=Token)
def login_client(client_in: ClientLogin, session: SessionDep) -> Any:
    """
    Log in a client and return a token.
    """
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    client = crud.authenticate_client(
        session=session, email=client_in.email, password=client_in.password
    )
    if not client:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    elif not client.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return Token(
        access_token=security.create_access_token(
            client.id, expires_delta=access_token_expires
        )
    )


@router.get("/me", response_model=ClientPublic)
def get_current_client(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get the currently logged-in client's profile.
    """
    client = crud.get_client_by_email(session=session, email=current_user.email)
    if not client:
        raise HTTPException(status_code=404, detail="Client profile not found")

    return client


@router.get("/{client_id}", response_model=ClientPublic)
def get_client_by_id(
    client_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific client by id.
    """
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.patch("/me", response_model=ClientPublic)
async def update_current_client(
    session: SessionDep,
    current_user: CurrentUser,
    company_name: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    industry: Optional[str] = Form(None),
    company_size: Optional[str] = Form(None),
    headquarters_location: Optional[str] = Form(None),
    primary_contact_person: Optional[str] = Form(None),
    contact_phone_number: Optional[str] = Form(None),
    primary_hiring_goals: Optional[List[str]] = Form(None),
    preferred_job_locations: Optional[List[str]] = Form(None), 
    roles_of_interest: Optional[List[str]] = Form(None),
    job_types: Optional[List[str]] = Form(None),
    dashboard_metrics: Optional[str] = Form(None),
    role_specific_customization: Optional[bool] = Form(None),
    salary_benchmarking_preference: Optional[str] = Form(None),
    candidate_viewing_preferences: Optional[str] = Form(None),
    offer_optimization: Optional[str] = Form(None),
    enable_real_time_market_alerts: Optional[bool] = Form(None),
    enable_custom_reporting: Optional[bool] = Form(None),
    preferred_report_frequency: Optional[str] = Form(None),
    automated_updates: Optional[str] = Form(None),
    candidate_feedback_analysis: Optional[str] = Form(None),
    invite_team_member: Optional[List[dict]] = Form(None),
    referral_source: Optional[str] = Form(None),
    referral_code: Optional[str] = Form(None),
    terms_accepted: Optional[bool] = Form(None)
) -> ClientPublic:
    """
    Update the currently logged-in client's profile.
    """
    client = crud.get_client_by_email(session=session, email=current_user.email)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    avatar = await save_file(avatar, "avatar") if avatar else None

    client_data = {
        "company_name": company_name,
        "email": current_user.email,
        "avatar": avatar,
        "industry": industry,
        "company_size": company_size,
        "headquarters_location": headquarters_location,
        "primary_contact_person": primary_contact_person,
        "contact_phone_number": contact_phone_number,
        "primary_hiring_goals": primary_hiring_goals,
        "preferred_job_locations": preferred_job_locations,
        "roles_of_interest": roles_of_interest,
        "job_types": job_types,
        "dashboard_metrics": dashboard_metrics,
        "role_specific_customization": role_specific_customization,
        "salary_benchmarking_preference": salary_benchmarking_preference,
        "candidate_viewing_preferences": candidate_viewing_preferences,
        "offer_optimization": offer_optimization,
        "enable_real_time_market_alerts": enable_real_time_market_alerts,
        "enable_custom_reporting": enable_custom_reporting,
        "preferred_report_frequency": preferred_report_frequency,
        "automated_updates": automated_updates,
        "candidate_feedback_analysis": candidate_feedback_analysis,
        "invite_team_member": invite_team_member,
        "referral_source": referral_source,
        "referral_code": referral_code,
        "terms_accepted": terms_accepted,
    }

    # Remove keys with None value to avoid overwriting existing values with null
    client_data = {k: v for k, v in client_data.items() if v is not None}
    client_data = ClientUpdate(**client_data)

    client = crud.update_client(
        session=session, db_client=client, client_in=client_data
    )
    return client


@router.delete("/me", response_model=Message)
def delete_current_client(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Delete the currently logged-in client's profile.
    """
    client = crud.get_client_by_email(session=session, email=current_user.email)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    session.delete(client)
    session.commit()
    return Message(message="Client deleted successfully")
