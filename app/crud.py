import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    RequestDemo, SocialProvider,
    Candidate, Client, Job, JobApplication
)
from app.api.schemas.utils import RequestDemoBase, SocialLoginBase
from app.api.schemas.candidates import CandidateBase, CandidateCreate, CandidateUpdate
from app.api.schemas.clients import ClientBase, ClientCreate, ClientUpdate
from app.api.schemas.jobs import (
    JobBase, JobUpdate, JobCreate, JobApplicationBase,
    JobApplicationCreate, JobApplicationUpdate
)


def create_request_demo(session: Session, request_create: RequestDemoBase) -> RequestDemo:
    # Create a new request demo record
    db_request = RequestDemo(
        full_name=request_create.full_name,
        company_name=request_create.company_name,
        email=request_create.email,
        phone_number=request_create.phone_number,
        message=request_create.message,
    )

    # Add to session and commit
    session.add(db_request)
    session.commit()
    session.refresh(db_request)

    return db_request


def get_request_demo_user(session: Session, email: str) -> RequestDemo | None:
    # Query the database for the demo request by email
    statement = select(RequestDemo).where(RequestDemo.email == email)
    request_user = session.exec(statement).first()
    return request_user


##################################################
#                                                #
#                  Candidate                     # 
#                                                #
##################################################

def create_candidate(*, session: Session, candidate_in: CandidateCreate) -> Candidate:
    db_candidate = Candidate.model_validate(candidate_in)
    if candidate_in.password:
        db_candidate = Candidate.model_validate(
            candidate_in, update={
                "hashed_password": get_password_hash(candidate_in.password)}
        )
    session.add(db_candidate)
    session.commit()
    session.refresh(db_candidate)
    return db_candidate


# Candidate Social auth
def create_or_update_candidate(*, session: Session, user_in: SocialLoginBase):
    is_new_user = False
    # Check if user with this provider exists
    existing_provider = session.query(SocialProvider).filter(
        SocialProvider.provider == user_in.provider,
        SocialProvider.provider_id == user_in.provider_id
    ).first()

    if existing_provider:
        # User already exists, log them in
        user = existing_provider.user
        return user, is_new_user

    # Check if a candidate with the provided email exists
    candidate = session.query(Candidate).filter(Candidate.email == user_in.email).first()

    if not candidate:
        # Create a new candidate if no candidate with this email exists
        user_data = CandidateCreate(
            email=user_in.email,
            full_name=user_in.full_name,
            password=None
        )
        user = create_user(session=session, user_create=user_data)
        is_new_user = True

    # Associate the new provider with the user if not already linked
    if not session.query(SocialProvider).filter(
        SocialProvider.user_id == user.id,
        SocialProvider.provider == user_in.provider
    ).first():
        new_provider = SocialProvider(
            user_id=user.id, provider=user_in.provider, provider_id=user_in.provider_id
        )
        session.add(new_provider)
        session.commit()

    return user, is_new_user


def authenticate_candidate(*, session: Session, email: str, password: str) -> Candidate | None:
    candidate = session.query(Candidate).filter(Candidate.email == email).first()
    if candidate and verify_password(password, candidate.hashed_password):
        return candidate
    return None


def update_candidate(*, session: Session, db_candidate: Candidate, candidate_in: CandidateUpdate) -> Candidate:
    candidate_data = candidate_in.model_dump(exclude_unset=True)
    db_candidate.sqlmodel_update(candidate_data)
    session.add(db_candidate)
    session.commit()
    session.refresh(db_candidate)
    return db_candidate


def get_candidate_by_email(*, session: Session, email: str) -> Candidate | None:
    statement = select(Candidate).where(Candidate.email == email)
    session_user = session.exec(statement).first()
    return session_user

##################################################
#                                                #
#                    Client                      # 
#                                                #
##################################################

def create_client(*, session: Session, client_in: ClientCreate) -> Client:
    db_client = Client.model_validate(client_in)
    db_client = Client.model_validate(
        client_in, update={
            "hashed_password": get_password_hash(client_in.password)}
    )
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    return db_client


def authenticate_client(*, session: Session, email: str, password: str) -> Client | None:
    client = session.query(Client).filter(Client.email == email).first()
    if client and verify_password(password, client.hashed_password):
        return client
    return None


def update_client(*, session: Session, db_client: Client, client_in: ClientUpdate) -> Client:
    client_data = client_in.model_dump(exclude_unset=True)
    db_client.sqlmodel_update(client_data)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    return db_client


def get_client_by_email(*, session: Session, email: str) -> Client | None:
    statement = select(Client).where(Client.email == email)
    session_user = session.exec(statement).first()
    return session_user


##################################################
#                                                #
#                    Jobs                        # 
#                                                #
##################################################


def create_job(*, session: Session, job_in: JobCreate) -> Job:
    db_job = Job.model_validate(job_in)
    session.add(db_job)
    session.commit()
    session.refresh(db_job)
    return db_job


def update_job(*, session: Session, db_job: Job, job_in: JobUpdate) -> Job:
    job_data = job_in.model_dump(exclude_unset=True)
    db_job.sqlmodel_update(job_data)
    session.add(db_job)
    session.commit()
    session.refresh(db_job)
    return db_job


def create_job_application(*, session: Session, application_in: JobApplicationCreate) -> JobApplication:
    db_application = JobApplication.model_validate(application_in)
    session.add(db_application)
    session.commit()
    session.refresh(db_application)
    return db_application


def update_job_application(*, session: Session, db_application: JobApplication, application_in: JobApplicationUpdate) -> JobApplication:
    application_data = application_in.model_dump(exclude_unset=True)
    db_application.sqlmodel_update(application_data)
    session.add(db_application)
    session.commit()
    session.refresh(db_application)
    return db_application
