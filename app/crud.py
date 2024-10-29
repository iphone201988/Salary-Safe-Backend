import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    User, RequestDemo, SocialProvider,
    Candidate, Client, Job, JobApplication
)
from app.api.schemas.login import SocialLoginBase
from app.api.schemas.users import UserCreate, UserUpdate, RequestDemoBase, RoleEnum
from app.api.schemas.candidates import CandidateBase, CandidateCreate, CandidateUpdate
from app.api.schemas.clients import ClientBase, ClientCreate, ClientUpdate
from app.api.schemas.jobs import (
    JobBase, JobUpdate, JobCreate, JobApplicationBase,
    JobApplicationCreate, JobApplicationUpdate
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(user_create)
    if user_create.password:
        db_obj = User.model_validate(
            user_create, update={
                "hashed_password": get_password_hash(user_create.password)}
        )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    # Create Candidate or Client based on user role
    if user_create.role:
        if user_create.role == RoleEnum.candidate:
            candidate = Candidate(user_id=db_obj.id)
            session.add(candidate)
        elif user_create.role == RoleEnum.client:
            client = Client(user_id=db_obj.id)
            session.add(client)

    session.commit()
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}

    # Update hashed password if provided
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password

    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)

    # Update Candidate or Client based on user role
    if db_user.role:
        if db_user.role == RoleEnum.candidate:
            candidate = session.get(Candidate, db_user.id)
            if candidate:
                candidate_data = CandidateBase.model_validate(user_in)
                candidate.sqlmodel_update(candidate_data)
                session.add(candidate)

        elif db_user.role == RoleEnum.client:
            client = session.get(Client, db_user.id)
            if client:
                client_data = ClientBase.model_validate(user_in)
                client.sqlmodel_update(client_data)
                session.add(client)

    session.commit()
    session.refresh(db_user)
    return db_user


def create_or_update_user(*, session: Session, user_in: SocialLoginBase):
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

    # Check if a user with the provided email exists
    user = session.query(User).filter(User.email == user_in.email).first()

    if not user:
        # Create a new user if no user with this email exists
        user_data = UserCreate(
            email=user_in.email,
            full_name=user_in.full_name,
            role=user_in.role,
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


def create_candidate(*, session: Session, candidate_in: CandidateCreate) -> Candidate:
    db_candidate = Candidate.model_validate(candidate_in)
    session.add(db_candidate)
    session.commit()
    session.refresh(db_candidate)
    return db_candidate


def update_candidate(*, session: Session, db_candidate: Candidate, candidate_in: CandidateUpdate) -> Candidate:
    candidate_data = candidate_in.model_dump(exclude_unset=True)
    db_candidate.sqlmodel_update(candidate_data)
    session.add(db_candidate)
    session.commit()
    session.refresh(db_candidate)
    return db_candidate


def create_client(*, session: Session, client_in: ClientCreate) -> Client:
    db_client = Client.model_validate(client_in)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    return db_client


def update_client(*, session: Session, db_client: Client, client_in: ClientUpdate) -> Client:
    client_data = client_in.model_dump(exclude_unset=True)
    db_client.sqlmodel_update(client_data)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    return db_client


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


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def get_request_demo_user(session: Session, email: str) -> RequestDemo | None:
    # Query the database for the demo request by email
    statement = select(RequestDemo).where(RequestDemo.email == email)
    request_user = session.exec(statement).first()
    return request_user
