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
from app.models import Client, Job, JobApplication
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
) -> JobsPublic:
    """
    Retrieve all jobs.
    """
    jobs, count = crud.get_jobs(session=session, skip=skip, limit=limit)
    return JobsPublic(data=jobs, count=count)


@router.get("/{job_id}", response_model=JobPublic)
def read_job_by_id(
    job_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific job by id.
    """
    job = crud.get_job_by_id(session=session, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobPublic(**job.dict(), client_details=job.client)


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

    job = crud.get_job_by_id(session=session, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.client_id != client.id:
        raise HTTPException(
        status_code=403, detail="You are not authorized to update this job"
    )

    job = crud.update_job(session=session, db_client=job, job_in=job_in)
    return job


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

    job = crud.get_job_by_id(session=session, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.client_id != client.id:
        raise HTTPException(
            status_code=403, detail="You are not authorized to delete this job"
        )

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
    jobs = [
        JobPublic(
            **job.dict(),
            client_details=job.client,
            application_status=crud.get_job_applications_status(
                session=session, candidate_id=current_user.id, job_id=job.id
            )
        ) for job in jobs
    ]
    return JobsPublic(data=jobs, count=count)


@router.get("/me/matches", response_model=JobsPublic)
def get_matching_jobs(
    session: SessionDep, current_user: CurrentUser,
    skip: int = 0, limit: int = 100
) -> Any:
    """
    Get job matches for current/logged in candidate
    """
    candidate = crud.get_candidate_by_email(session=session, email=current_user.email)
    if not candidate:
        raise HTTPException(
            status_code=403, detail="Only candidates can view their job matches")

    jobs, count = crud.get_matching_jobs_for_candidate(
        session=session, candidate=candidate, skip=skip, limit=limit
    )
    jobs = [
        JobPublic(
            **job.dict(),
            client_details=job.client,
            application_status=crud.get_job_applications_status(
                session=session, candidate_id=current_user.id, job_id=job.id
            )
        ) for job in jobs
    ]
    return JobsPublic(data=jobs, count=count)


@router.post("/filters/insights", response_model=MarketInsightsResponse)
def get_market_insights(
    session: SessionDep, current_user: CurrentUser, filters: JobInsightsRequest
) -> MarketInsightsResponse:
    """
    Get market insights based on job filters.
    """
    return crud.get_market_insights(session=session, filters=filters)


##################################################################
#                                                                #
#                       Job Applications                         #
#                                                                #
##################################################################
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

    job = crud.get_job_by_id(session=session, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    application_in.candidate_id = candidate.id
    application_in.job_id = job.id
    application_in.status = ApplicationStatusEnum.pending
    application = crud.create_job_application(
        session=session, application_in=application_in
    )
    return application


@router.get("/applications/all", response_model=JobApplicationsPublic)
def read_job_applications(
    session: SessionDep, current_user: CurrentUser,
    skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve all job applications.
    """
    applications, count = crud.get_job_applications(
        session=session, skip=skip, limit=limit
    )
    applications = [
        JobApplicationPublic(
            **app.dict(),
            job_details=JobPublic(
                **app.job.dict(),
                client_details=app.job.client
            )
        )
        for app in applications
    ]

    return JobApplicationsPublic(data=applications, count=count)


@router.get("/applications/me", response_model=JobApplicationsPublic)
def get_my_job_applications(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get all applications submitted by the current/logged-in candidate.
    """
    candidate = crud.get_candidate_by_email(session=session, email=current_user.email)
    if not candidate:
        raise HTTPException(
            status_code=403, detail="Only candidates can view their applications"
        )

    applications, count = crud.get_job_applications_by_candidate_id(
        session=session, candidate_id=candidate.id, skip=skip, limit=limit
    )

    applications = [
        JobApplicationPublic(
            **app.dict(),
            candidate_details=app.candidate,
            job_details=JobPublic(
                **app.job.dict(),
                client_details=app.job.client
            )
        )
        for app in applications
    ]

    return JobApplicationsPublic(data=applications, count=count)


@router.get("/{job_id}/applications", response_model=JobApplicationsPublic)
def get_job_applications_by_job_id(
    session: SessionDep, current_user: CurrentUser, job_id: uuid.UUID,
    skip: int = 0, limit: int = 100
) -> Any:
    """
    Get the applications for a specific job. (Only for clients)
    """
    client = crud.get_client_by_email(session=session, email=current_user.email)
    if not client:
        raise HTTPException(
            status_code=403, detail="Only for clients"
        )

    job = crud.get_job_by_id(session=session, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.client_id != client.id:
        raise HTTPException(
            status_code=403, detail="You are not authorized to view this job applications"
        )

    applications, count = crud.get_job_applications_by_job_id(
        session=session, job_id=job_id, skip=skip, limit=limit
    )

    applications = [
        JobApplicationPublic(
            **app.dict(),
            candidate_details=app.candidate,
            job_details=JobPublic(
                **app.job.dict(),
                client_details=app.job.client,
            )
        )
        for app in applications
    ]

    return JobApplicationsPublic(data=applications, count=count)


@router.get("/applications/{job_id}/status")
def get_job_application_status(
    session: SessionDep, current_user: CurrentUser, job_id: uuid.UUID
) -> Any:
    """
    Fetch the application status of the current user for a specific job.
    """
    candidate = crud.get_candidate_by_email(session=session, email=current_user.email)
    if not candidate:
        raise HTTPException(
            status_code=403, detail="Only for candidates"
        )

    job = crud.get_job_by_id(session=session, job_id=job_id)
    if not application:
        raise HTTPException(status_code=404, detail="Job not found")

    application_status = crud.get_job_applications_status(
        session=session, candidate_id=candidate.id, job_id=job_id
    )

    return application_status


@router.patch("/applications/{application_id}/status", response_model=JobApplicationPublic)
def update_job_application_status(
    session: SessionDep,
    current_user: CurrentUser,
    application_id: uuid.UUID,
    application_status: JobApplicationStatusUpdate
) -> Any:
    """
    Update the status of a job application. (Only for clients)
    """
    client = crud.get_client_by_email(session=session, email=current_user.email)
    if not client:
        raise HTTPException(status_code=403, detail="Only for clients")

    application = crud.get_job_application_by_id(session=session, application_id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")

    if application.job.client_id != client.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this application")

    application = crud.update_job_application_status(
        session=session, application=application,
        application_status=application_status.status
    )

    return JobApplicationPublic(
        **application.dict(),
        candidate_details=application.candidate,
        job_details=JobPublic(
            **application.job.dict(),
            client_details=application.job.client
        )
    )
