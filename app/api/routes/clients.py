import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import Client
from app.api.schemas.clients import (
    ClientCreate, ClientUpdate, ClientPublic,
    ClientsPublic
)
from app.api.schemas.utils import Message

router = APIRouter()


@router.get("/me", response_model=ClientPublic)
def get_current_client(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get the currently logged-in client's profile.
    """
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Access denied")
    
    client = session.exec(select(Client).where(Client.user_id == current_user.id)).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client profile not found")

    return client


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ClientPublic,
)
def create_client(session: SessionDep, client_in: ClientCreate) -> Any:
    """
    Create a new client.
    """
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can create profiles")
    
    client = crud.create_client(session=session, client_in=client_in)
    return client


@router.get("/", response_model=ClientsPublic)
def read_clients(
    session: SessionDep, current_user: CurrentUser,
    skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve all clients.
    """
    statement = select(Client).offset(skip).limit(limit)
    clients = session.exec(statement).all()

    count = session.exec(select(func.count()).select_from(Client)).one()
    return ClientsPublic(data=clients, count=count)


@router.get("/{client_id}", response_model=ClientPublic)
def read_client_by_id(
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
    if current_user.role != "client":
        raise HTTPException(
            status_code=403, detail="Only clients can update this profile"
        )
    
    client = session.exec(
        select(Client).where(Client.user_id == current_user.id)).first()
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
    if current_user.role != "client":
        raise HTTPException(
            status_code=403, detail="Only clients can delete this profile"
        )
    
    client = session.exec(
        select(Client).where(Client.user_id == current_user.id)).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    session.delete(client)
    session.commit()
    return Message(message="Client deleted successfully")
