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
from app.models import Candidate
from app.api.schemas.candidates import (
    CandidateCreate, CandidateUpdate, CandidatePublic,
    CandidatesPublic
)
from app.api.schemas.utils import Message

router = APIRouter()


@router.get("/me", response_model=CandidatePublic)
def get_current_candidate(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get the currently logged-in candidate's profile.
    """
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Access denied")

    candidate = session.exec(select(Candidate).where(
        Candidate.user_id == current_user.id)).first()
    if not candidate:
        raise HTTPException(
            status_code=404, detail="Candidate profile not found")

    return candidate


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=CandidatePublic,
)
def create_candidate(session: SessionDep, candidate_in: CandidateCreate) -> Any:
    """
    Create a new candidate.
    """
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=403, detail="Only candidates can create profiles")

    candidate = crud.create_candidate(
        session=session, candidate_in=candidate_in)
    return candidate


@router.get("/", response_model=CandidatesPublic)
def read_candidates(
    session: SessionDep, current_user: CurrentUser,
    skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve all candidates.
    """
    statement = select(Candidate).offset(skip).limit(limit)
    candidates = session.exec(statement).all()

    count = session.exec(select(func.count()).select_from(Candidate)).one()
    return CandidatesPublic(data=candidates, count=count)


@router.get("/{candidate_id}", response_model=CandidatePublic)
def read_candidate_by_id(
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
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=403, detail="Only candidates can update this profile")

    candidate = session.exec(select(Candidate).where(
        Candidate.user_id == current_user.id)).first()
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
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=403, detail="Only candidates can delete this profile")

    candidate = session.exec(select(Candidate).where(
        Candidate.user_id == current_user.id)).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    session.delete(candidate)
    session.commit()
    return Message(message="Candidate deleted successfully")
