# Salary Safe - Backend
Ensure Fair Pay. Promote Equity

## Getting Started
To get started with Salary Safe locally, follow these steps.

#### Prerequisites
- Python 3.8+
- PostgreSQL

## Tech Stack

### Backend
- **Python**: Core programming language.
- **FastAPI**: Framework for building REST APIs.
- **SQLAlchemy**: ORM for database interaction.
- **Alembic**: Tool for handling database migrations.
- **PostgreSQL**: Database for storing application data.

### Server
- **Nginx**: Reverse proxy server for routing and load balancing.
- **Gunicorn**: WSGI HTTP Server for running Python applications.
- **Uvicorn**: ASGI server for running FastAPI applications.
- **Certbot**: Tool for managing SSL certificates (HTTPS).

## Setup Instructions
1. Clone the repository
    ```bash
    git clone https://github.com/{username}/SalarySafe.git
    cd salary-safe
    ```

2. Create a virtual environment and activate it
    ```bash
    python -m venv env
    source env/bin/activate   # On Windows: `env\Scripts\activate`
    ````

3. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables

    Create a .env file and provide the necessary environment variables (e.g., database URL, Secret Key, email credentials).

5. Run database migrations

    Use Alembic to handle database migrations. First, apply the existing migrations:
    ```bash
    # makemigrations
    alembic revision --autogenerate -m "describe your migration here"
    # migrate
    alembic upgrade head
    ```

6. Run the application

    Development
    ```bash
    fastapi dev --reload app/main.py --host 0.0.0.0 --port 5000 
    ```

    Production
    ```bash
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app  

    ```
