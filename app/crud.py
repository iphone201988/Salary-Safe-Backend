import uuid
from typing import Any, Optional
from decimal import Decimal

from sqlmodel import Session, select, func

from app.core.security import get_password_hash, verify_password
from app.models import *
from app.api.schemas.utils import RequestDemoBase, SocialLoginBase
from app.api.schemas.candidates import CandidateBase, CandidateCreate, CandidateUpdate
from app.api.schemas.clients import ClientBase, ClientCreate, ClientUpdate
from app.api.schemas.jobs import *


def create_request_demo(
    session: Session, request_create: RequestDemoBase
) -> RequestDemo:
    db_request = RequestDemo(
        full_name=request_create.full_name,
        company_name=request_create.company_name,
        email=request_create.email,
        phone_number=request_create.phone_number,
        message=request_create.message,
    )
    session.add(db_request)
    session.commit()
    session.refresh(db_request)

    return db_request


def get_request_demo_user(
    session: Session, email: str
) -> RequestDemo | None:
    statement = select(RequestDemo).where(RequestDemo.email == email)
    request_user = session.exec(statement).first()

    return request_user


##################################################
#                                                #
#                  Candidate                     # 
#                                                #
##################################################

def create_candidate(
    *, session: Session, candidate_in: CandidateCreate
) -> Candidate:
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
def create_or_update_candidate(
    *, session: Session, user_in: SocialLoginBase
):
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
    candidate = session.query(
        Candidate).filter(Candidate.email == user_in.email).first()

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
            user_id=user.id, provider=user_in.provider,
            provider_id=user_in.provider_id
        )
        session.add(new_provider)
        session.commit()

    return user, is_new_user


def authenticate_candidate(
    *, session: Session,email: str, password: str
) -> Candidate | None:
    candidate = session.query(
        Candidate).filter(Candidate.email == email).first()
    if candidate and verify_password(password, candidate.hashed_password):
        return candidate

    return None


def update_candidate(
    *, session: Session, db_candidate: Candidate,
    candidate_in: CandidateUpdate
) -> Candidate:
    candidate_data = candidate_in.model_dump(exclude_unset=True)
    db_candidate.sqlmodel_update(candidate_data)

    session.add(db_candidate)
    session.commit()
    session.refresh(db_candidate)

    return db_candidate


def get_candidate_by_email(
    *, session: Session, email: str
) -> Candidate | None:
    statement = select(Candidate).where(Candidate.email == email)
    session_user = session.exec(statement).first()

    return session_user


def get_candidate_by_phone_number(
    *, session: Session, phone_number: str
) -> Candidate | None:
    statement = select(Candidate).where(
        Candidate.phone_number == phone_number
    )
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
            "hashed_password": get_password_hash(client_in.password)
        }
    )
    session.add(db_client)
    session.commit()
    session.refresh(db_client)

    return db_client


def authenticate_client(
    *, session: Session, email: str, password: str
) -> Client | None:
    client = session.query(Client).filter(Client.email == email).first()
    if client and verify_password(password, client.hashed_password):
        return client

    return None


def update_client(
    *, session: Session, db_client: Client, client_in: ClientUpdate
) -> Client:
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

def get_client_by_phone_number(
    *, session: Session, phone_number: str
) -> Client | None:
    statement = select(Client).where(
        Client.contact_phone_number == phone_number
    )
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


def get_jobs(
    session: Session, skip: int = 0, limit: int = 100
) -> tuple[List[Job], int]:

    statement = (
        select(Job, Client.company_name)
        .join(Client, Job.client_id == Client.id, isouter=True)
        .offset(skip)
        .limit(limit)
    )
    jobs = session.exec(statement).all()
    jobs = [
        JobPublic(**job.dict(), company_name=company_name)
        for job, company_name in jobs
    ]

    count = session.exec(select(func.count()).select_from(Job)).one()

    return jobs, count


def get_job_by_id(session: Session, job_id=uuid.UUID):
    job = session.get(Job, job_id)
    return job


def get_jobs_by_client(
    *, session: Session, client_id: uuid.UUID, skip: int, limit: int
) -> tuple[list[Job], int]:

    statement = select(Job).where(Job.client_id == client_id)
    jobs = session.exec(statement.offset(skip).limit(limit)).all()

    total_count = session.exec(
        select(func.count()).select_from(statement.subquery())).one()

    return jobs, total_count


def update_job(*, session: Session, db_client: Job, job_in: JobUpdate) -> Job:
    job_data = job_in.model_dump(exclude_unset=True)
    db_client.sqlmodel_update(job_data)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)

    return db_client


def search_jobs(
    *, session: Session, filters: JobSearch
) -> tuple[list[Job], int]:
    statement = select(Job)

    if filters.title:
        statement = statement.where(Job.title.ilike(f"%{filters.title}%"))
    if filters.location:
        statement = statement.where(Job.location.ilike(f"%{filters.location}%"))
    if filters.salary_min is not None:
        statement = statement.where(Job.salary_min >= filters.salary_min)
    if filters.salary_max is not None:
        statement = statement.where(Job.salary_max <= filters.salary_max)
    if filters.status:
        statement = statement.where(Job.status == filters.status)
    if filters.job_type:
        statement = statement.where(Job.job_type == filters.job_type)
    if filters.workplace_type:
        statement = statement.where(Job.workplace_type == filters.workplace_type)

    total_count = session.exec(
        select(func.count()).select_from(statement.subquery())
    ).one()

    jobs = session.exec(statement.offset(filters.skip).limit(filters.limit)).all()

    return jobs, total_count


def get_matching_jobs_for_candidate(
    *, session: Session, candidate: Candidate,
    skip: int, limit: int
):
    statement = select(Job).where(Job.status == "active")

    if candidate.job_titles_of_interest:
        statement = statement.where(
            Job.title.ilike(f"%{candidate.job_titles_of_interest.strip().lower()}%")
        )

    if candidate.location:
        statement = statement.where(
            Job.location.ilike(f"%{candidate.location.strip().lower()}%")
        )

    if candidate.job_type_preferences:
        statement = statement.where(
            Job.job_type.in_(candidate.job_type_preferences)
        )

    if candidate.minimum_acceptable_salary:
        statement = statement.where(
            Job.salary_min >= Decimal(candidate.minimum_acceptable_salary)
        )

    if candidate.general_salary_range:
        statement = statement.where(
            Job.salary_max <= Decimal(candidate.general_salary_range)
        )
    jobs = session.exec(statement.offset(skip).limit(limit)).all()

    total_count = session.exec(
        select(func.count()).select_from(statement.subquery())).one()

    return jobs, total_count


def get_market_insights(session: Session, filters: JobInsightsRequest):
    query = select(Job)

    if filters.title:
        query = query.where(Job.title.ilike(f"%{filters.title}%"))
    if filters.location:
        query = query.where(Job.location.ilike(f"%{filters.location}%"))
    if filters.requirements:
        query = query.where(Job.requirements.ilike(f"%{filters.requirements}%"))
    if filters.min_salary is not None:
        query = query.where(Job.salary_min >= filters.min_salary)
    if filters.max_salary is not None:
        query = query.where(Job.salary_max <= filters.max_salary)
    if filters.status:
        query = query.where(Job.status == filters.status)
    if filters.job_type:
        query = query.where(Job.job_type == filters.job_type)
    if filters.workplace_type:
        query = query.where(Job.workplace_type == filters.workplace_type)

    jobs = session.exec(query).all()
    if not jobs:
        return MarketInsightsResponse(
            average_salary=None,
            total_jobs=0,
            top_companies=[],
            job_type_distribution=[],
            salary_distribution=[],
        )

    # Total job postings
    total_jobs = len(jobs)

    # Average salary calculation
    avg_salary = session.exec(
        select(func.avg((Job.salary_min + Job.salary_max) / 2))
        .select_from(Job)
        .where(Job.id.in_([job.id for job in jobs]))
    ).one_or_none()

    # Top companies hiring
    company_counts = (
        session.exec(
            select(Client.company_name, func.count(Job.id))
            .join(Client, Client.id == Job.client_id)
            .where(Job.id.in_([job.id for job in jobs]))
            .group_by(Client.company_name)
            .order_by(func.count(Job.id).desc())
        ).all()
    )
    top_companies = [
        {"company_name": name, "job_count": count} for name, count in company_counts
    ]

    # Job type distribution
    job_type_counts = (
        session.exec(
            select(Job.job_type, func.count(Job.id))
            .where(Job.id.in_([job.id for job in jobs]))
            .group_by(Job.job_type)
        ).all()
    )
    job_type_distribution = [
        {"job_type": jt, "count": count} for jt, count in job_type_counts
    ]

    # Salary range distribution
    salary_ranges = [
        (0, 25000), (25000, 50000), (50000, 75000),
        (75000, 100000), (100000, None)
    ]
    salary_distribution = []
    for min_sal, max_sal in salary_ranges:
        range_label = f"{min_sal} - {max_sal if max_sal else 'Above'}"
        count = session.exec(
            select(func.count(Job.id))
            .where(
                Job.salary_min >= min_sal,
                (Job.salary_max <= max_sal) if max_sal else True,
                Job.id.in_([job.id for job in jobs])
            )
        ).one_or_none()
        salary_distribution.append({"range": range_label, "count": count})

    return MarketInsightsResponse(
        average_salary=avg_salary,
        total_jobs=total_jobs,
        top_companies=top_companies,
        job_type_distribution=job_type_distribution,
        salary_distribution=salary_distribution,
    )


def create_job_application(
    *, session: Session, application_in: JobApplicationCreate
) -> JobApplication:
    db_application = JobApplication.model_validate(application_in)
    session.add(db_application)
    session.commit()
    session.refresh(db_application)

    return db_application


def get_job_applications(
    session: Session, skip: int, limit: int
) -> tuple[list[JobApplication], int]:

    statement = select(JobApplication).offset(skip).limit(limit)
    applications = session.exec(statement).all()

    total_count = session.exec(
        select(func.count()).select_from(JobApplication)).one()

    return applications, total_count


def get_job_applications_by_job_id(
    session: Session, job_id: uuid.UUID, skip: int, limit: int
) -> tuple[list[JobApplication], int]:
    statement = select(JobApplication).where(JobApplication.job_id == job_id)
    applications = session.exec(statement.offset(skip).limit(limit)).all()

    total_count = session.exec(
        select(func.count()).select_from(statement.subquery())).one()

    return applications, total_count


def get_job_application_by_id(session: Session, application_id=uuid.UUID):
    job_application = session.get(JobApplication, application_id)
    return job_application


def get_job_applications_by_candidate_id(
    session: Session, candidate_id: uuid.UUID, skip: int, limit: int
) -> tuple[list[JobApplication], int]:
    statement = select(JobApplication).where(
        JobApplication.candidate_id == candidate_id
    )
    applications = session.exec(statement.offset(skip).limit(limit)).all()

    total_count = session.exec(
        select(func.count()).select_from(statement.subquery())).one()

    return applications, total_count


def update_job_application(
    *, session: Session, db_client: JobApplication,
    application_in: JobApplicationUpdate
) -> JobApplication:
    application_data = application_in.model_dump(exclude_unset=True)
    db_client.sqlmodel_update(application_data)

    session.add(db_client)
    session.commit()
    session.refresh(db_client)

    return db_client


def update_job_application_status(
    session: Session, application: JobApplication,
    application_status: JobApplicationStatusUpdate
) -> JobApplication:
    application.status = application_status
    session.add(application)
    session.commit()
    session.refresh(application)
    return application


def get_job_applications_status(
    session: Session, candidate_id: uuid.UUID, job_id: uuid.UUID,
) -> Optional[str]:
    """
    Fetch the application status of the current user for a specific job.
    """
    statement = select(JobApplication.status).where(
        JobApplication.job_id == job_id,
        JobApplication.candidate_id == candidate_id,
    )
    status = session.exec(statement).first()
    return status


def get_salary_recommendation_data(session: Session, candidate: Candidate):
    """
    Calculating required parameters for Salary Recommendation
    """
    # Internal median salary
    jobs, count = get_matching_jobs_for_candidate(
        session=session, candidate=candidate, skip=0, limit=100
    )
    salaries = [(job.salary_min + job.salary_max) / 2 \
        for job in jobs if job.salary_min and job.salary_max]
    I = int(sum(salaries) / len(salaries) if salaries else 0)

    # Candidate Skills Profiency, Weight and Market Premium
    candidate_key_skills = [skill['name'] for skill in candidate.key_skills]
    if not candidate_key_skills:
        raise HTTPException(status_code=422, detail="Candidate key skills not found")

    skills_data = session.exec(
        select(Skills).where(Skills.name.in_(candidate_key_skills))
    ).all()
    if not skills_data:
        raise HTTPException(status_code=422, detail="Candidate key skills not found")

    skill_proficiency = [skill["proficiency"] for skill in candidate.key_skills]
    skill_weights = [skill.weight for skill in skills_data]
    market_premiums = [skill.market_premium for skill in skills_data]

    # Candidate location multiplier
    location_data = session.exec(
        select(Locations).where(Locations.city == candidate.location)
    ).first()
    if not location_data:
        raise HTTPException(status_code=422, detail="Candidate location not found")

    location_multiplier = location_data.location_multiplier \
        if location_data.location_multiplier else 1.1

    # Candidate Industry Trends
    industry_data = session.exec(
        select(Industry).where(Industry.industry.in_(candidate.industries_of_interest))
    ).first()
    if not industry_data:
        raise HTTPException(status_code=422, detail="Candidate industries of interest not found")

    trend_percentage = industry_data.trend_percentage \
        if industry_data.trend_percentage else 3

    # Todo: Make all these values dynamic
    Wi = 0.4 # Internal weight
    E = 52000 # External market salary
    We = 0.5 # External weight

    C = 5000 # Customization factor
    Wc = 0.1 # Customization weight

    risk_percentage = 5 # Risk premium percentage
    benefits = 10000 # Value of benefits/equity

    transparency_score = 4 # Transparency score (1–5)
    transparency_weight = 0.02 # Weight for transparency

    equity_score = 4 # Diversity and equity score (1–5)
    diversity_premium = 2000 # Premium for diversity

    flexibility_score = 3 # Flexibility score (1–5)
    flexibility_multiplier = 1500 # Flexibility multiplier

    well_being_value = 3000 # Well-being benefits value

    functional_multiplier = 1.05 # Industry adjustment (e.g., 5% increase)
    market_demand_multiplier = 1.03 # Market demand adjustment (e.g., 3% increase)

    return (
        I, Wi, E, We, skill_proficiency, skill_weights, market_premiums,
        location_multiplier, trend_percentage, C, Wc, risk_percentage,
        benefits, transparency_score, transparency_weight,
        equity_score, diversity_premium, flexibility_score,
        flexibility_multiplier, well_being_value, functional_multiplier,
        market_demand_multiplier
    )
