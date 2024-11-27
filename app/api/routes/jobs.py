import uuid
from typing import Optional, List, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import Job, JobApplication
from app.api.schemas.jobs import *
from app.api.schemas.utils import Message

router = APIRouter()


@router.post("/", response_model=JobPublic)
def create_job(
    session: SessionDep, job_in: JobCreate, current_user: CurrentUser
) -> Any:
    """
    Create a new job (only for clients).
    """
    client = crud.get_client_by_email(session=session, email=current_user.email)
    if not client:
        raise HTTPException(
            status_code=403, detail="Only clients can create jobs")

    job_in.client_id = client.id
    job = crud.create_job(session=session, job_in=job_in)
    return job


@router.get("/me", response_model=JobsPublic)
def get_current_client_jobs(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get jobs created by the current/logged in client.
    """
    client = crud.get_client_by_email(session=session, email=current_user.email)
    if not client:
        raise HTTPException(
            status_code=403, detail="Only clients can access their jobs"
        )

    jobs, count = crud.get_jobs_by_client(
        session=session, client_id=client.id, skip=skip, limit=limit)
    return JobsPublic(data=jobs, count=count)



@router.get("/", response_model=JobsPublic)
def read_jobs(
    session: SessionDep, current_user: CurrentUser,
    skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve all jobs.
    """
    statement = select(Job).offset(skip).limit(limit)
    jobs = session.exec(statement).all()

    count = session.exec(select(func.count()).select_from(Job)).one()
    return JobsPublic(data=jobs, count=count)


@router.get("/{job_id}", response_model=JobPublic)
def read_job_by_id(
    job_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific job by id.
    """
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/{job_id}", response_model=JobPublic)
def update_job(
    job_id: uuid.UUID, session: SessionDep, job_in: JobUpdate,
    current_user: CurrentUser
) -> Any:
    """
    Update a job (only for clients).
    """
    client = crud.get_client_by_email(session=session, email=current_user.email)
    if not client:
        raise HTTPException(
            status_code=403, detail="Only clients can update jobs")

    db_job = session.get(Job, job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")

    db_job = crud.update_job(session=session, db_job=db_job, job_in=job_in)
    return db_job


@router.delete("/{job_id}", response_model=Message)
def delete_job(
    job_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Delete a job (only for clients).
    """
    client = crud.get_client_by_email(session=session, email=current_user.email)
    if not client:
        raise HTTPException(
            status_code=403, detail="Only clients can delete jobs")

    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    session.delete(job)
    session.commit()
    return Message(message="Job deleted successfully")


@router.post("/filters/search", response_model=JobsPublic)
def search_jobs(
    session: SessionDep, current_user: CurrentUser, filters: JobSearch
) -> Any:
    """
    Search for jobs based on multiple filters.
    """
    jobs, count = crud.search_jobs(
        session=session,
        filters=filters,
    )
    return JobsPublic(data=jobs, count=count)


@router.post("/{job_id}/apply", response_model=JobApplicationPublic)
def apply_to_job(
    job_id: uuid.UUID, session: SessionDep,
    application_in: JobApplicationCreate, current_user: CurrentUser
) -> Any:
    """
    Apply to a job (only for candidates).
    """
    candidate = crud.get_candidate_by_email(session=session, email=current_user.email)
    if not candidate:
        raise HTTPException(
            status_code=403, detail="Only candidates can apply to jobs")

    application_in.candidate_id = candidate.id
    application = crud.create_job_application(
        session=session, application_in=application_in)
    return application


@router.get("/applications/me", response_model=JobApplicationsPublic)
def get_my_job_applications(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get all applications submitted by the current/logged in candidate.
    """
    candidate = crud.get_candidate_by_email(session=session, email=current_user.email)
    if not candidate:
        raise HTTPException(
            status_code=403, detail="Only candidates can view their applications"
        )

    applications, count = crud.get_applications_by_candidate(
        session=session, candidate_id=candidate.id, skip=skip, limit=limit)
    return JobApplicationsPublic(data=applications, count=count)


@router.get("/{job_id}/applications", response_model=JobApplicationsPublic)
def read_job_applications_for_job(
    job_id: uuid.UUID, session: SessionDep, current_user: CurrentUser,
    skip: int = 0, limit: int = 100
) -> Any:
    """
        Fetch applications for a specific job
    """
    statement = select(JobApplication).where(
        JobApplication.job_id == job_id).offset(skip).limit(limit)
    applications = session.exec(statement).all()
    count = session.exec(select(func.count()).select_from(
        JobApplication).where(JobApplication.job_id == job_id)).one()
    return JobApplicationsPublic(data=applications, count=count)


@router.get("/applications/all", response_model=JobApplicationsPublic)
def read_job_applications(
    session: SessionDep, current_user: CurrentUser,
    skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve all job applications.
    """
    statement = select(JobApplication).offset(skip).limit(limit)
    applications = session.exec(statement).all()

    count = session.exec(select(func.count()).select_from(JobApplication)).one()
    return JobApplicationsPublic(data=applications, count=count)
