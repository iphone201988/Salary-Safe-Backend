import uuid
from typing import Any
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
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
def update_current_client(
    session: SessionDep, client_in: ClientUpdate, current_user: CurrentUser
) -> Any:
    """
    Update the currently logged-in client's profile.
    """
    client = crud.get_client_by_email(session=session, email=current_user.email)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    client = crud.update_client(
        session=session, db_client=client, client_in=client_in
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
