from datetime import timedelta
from typing import Annotated, Any
from pydantic.networks import EmailStr

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Form

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash

from app.api.schemas.candidates import CandidatePublic
from app.api.schemas.clients import ClientPublic
from app.api.schemas.utils import (
    Message, Token, SocialLoginToken,
    NewPassword, ResetPasswordResponse
)
from app.utils import (
    generate_test_email,
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter()

@router.post("/login/test-token", response_model=Any)
def test_token(current_user: Any) -> Any:
    """
    Test access token for either Client or Candidate
    """
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> ResetPasswordResponse:
    """
    Password Recovery for Client or Candidate
    """
    user = crud.get_client_by_email(session=session, email=email) or crud.get_candidate_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    password_reset_link = f"{settings.FRONTEND_HOST}/reset-password?email={email}&token={password_reset_token}"

    # email_data = generate_reset_password_email(
    #     email_to=user.email, email=email, token=password_reset_token
    # )
    # send_email(
    #     email_to=user.email,
    #     subject=email_data.subject,
    #     html_content=email_data.html_content,
    # )
    return ResetPasswordResponse(link=password_reset_link)


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password for Client or Candidate
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.get_client_by_email(session=session, email=email) or crud.get_candidate_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery for Client or Candidate
    """
    user = crud.get_client_by_email(session=session, email=email) or crud.get_candidate_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    return True
