from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import Client
from app.api.schemas.clients import ClientCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

# Initialize the database with a superuser Client account
def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # If migrations are not used, you can uncomment the following lines
    # to create tables manually:
    # from sqlmodel import SQLModel
    # SQLModel.metadata.create_all(engine)

    # Check if the first superuser Client already exists
    superuser_client = session.exec(
        select(Client).where(Client.email == settings.FIRST_SUPERUSER)
    ).first()
    if not superuser_client:
        # Create a new superuser Client
        client_in = ClientCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            full_name="Superuser",
            company_name="SalarySafe"
        )
        superuser_client = crud.create_client(session=session, client_create=client_in)
