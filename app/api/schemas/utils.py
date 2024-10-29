from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class SocialLoginToken(SQLModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool = False


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None
