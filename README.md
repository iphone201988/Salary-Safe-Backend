# Salary Safe - Backend
Ensure Fair Pay. Promote Equity

## Getting Started
To get started with Salary Safe locally, follow these steps.

#### Prerequisites
- Python 3.8+
- PostgreSQL

## Setup Instructions
1. Clone the repository
    ```bash
    git clone https://github.com/Techwinlabs-Python/SalarySafe.git
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
    ```bash
    # Check fastapi docs for other mode (prod)
    fastapi dev --reload app/main.py --host 0.0.0.0 --port 5000 
    ```

