import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import User, RequestDemo, SocialProvider
from app.api.schemas.login import SocialLoginBase
from app.api.schemas.users import UserCreate, UserUpdate, RequestDemoBase


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={
            "hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
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
        user = User(email=user_in.email, full_name=user_in.full_name)
        session.add(user)
        session.commit()
        session.refresh(user)
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
