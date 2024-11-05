from collections.abc import Generator
from typing import Annotated, Union

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import Client, Candidate
from app.api.schemas.utils import TokenPayload


# OAuth2 setup
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/candidates/login"
)


# Database dependency
def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


# Get current user function
def get_current_user(session: SessionDep, token: TokenDep) -> Union[Client, Candidate]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = session.get(Candidate, token_data.sub) or session.get(Client, token_data.sub)    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


CurrentUser = Annotated[Union[Client, Candidate], Depends(get_current_user)]


# Superuser verification (if applicable for clients)
def get_current_active_superuser(current_user: CurrentUser) -> Client:
    if isinstance(current_user, Client) and not getattr(current_user, 'is_superuser', False):
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
