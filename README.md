## About

This project demonstrates a sample CRUD API in Python using FastAPI, SQLModel, and Pydantic. The project architecture consists of two Docker containers: one for the `api` and another for the database (`api_db`). Upon startup, the `api_db` container creates the schema and populates it with mock data based on queries in `/db/schema_queries`. The `api` service implements an ORM-Repository pattern design, where the SQLModel library is used to define ORM models representing the underlying database tables. These ORM models are used by repository classes to describe database queries. The `api` service is designed to create a unique database session for each HTTP request, which is closed upon completion. The sample API provides services for two resources: `users` and `portfolios`, representing investment portfolios (e.g., stocks, ETFs) held by users.

## Setup

### Container run:
1. Create a copy of the environment file: `cp .env.sample .env`
2. Fill in the `.env` file with appropriate values (sample values for local development are provided)
3. Run the containers: `docker compose up`
4. Verify the service is running: `curl http://127.0.0.1:8000/`

### Local development:
1. Create a copy of the environment file: `cp .env.sample .env`
2. Fill in the `.env` file with appropriate values (sample values for local development are provided)
3. Create the virtual environment: `make venv` (ensure `poetry` is installed on your system, if not run `pip install poetry` first)
4. Activate the virtual environment: `poetry shell`
5. Load the environment variables: `source .env`
6. Start the database service: `docker compose up api_db`
7. Run the FastAPI server: `fastapi run api/main.py`
 
* For easy local testing (with the `api_db` container running and `.env` sourced), `ipython` can be used:
    ```python
    >> ipython
    In [1]: from api.repositories.base import SessionManager

    In [2]: from api.repositories.user import UserRepository

    In [3]: db = SessionManager()

    In [4]: UserRepository(db=db).get('b04fb2c6-30d3-469e-b6d2-ad1e480c67a4')
    Out[4]: UserModel(surname='Smith', id=UUID('b04fb2c6-30d3-469e-b6d2-ad1e480c67a4'), name='Jane', email='jane.smith@example.com', plan=<SubscriptionPlan.PREMIUM: 'premium'>)
    ```
* To query the database directly from a database session run `make db-session` (while the `api_db` container is running):
  ```sql
    >> make db-session
    docker compose exec api_db psql -U postgres -d api
    psql (17.0 (Debian 17.0-1.pgdg110+1))
    Type "help" for help.

    api=# \dt
            List of relations
    Schema |    Name    | Type  |  Owner   
    --------+------------+-------+----------
    public | portfolios | table | postgres
    public | users      | table | postgres
    (2 rows)

    api=# select * from users;
                    id                  | name | surname |         email          |   plan   
    --------------------------------------+------+---------+------------------------+----------
    bd35d25a-be7e-4f82-b68f-02ee8a9e61fd | John | Smith   | john.smith@example.com | freemium
    b04fb2c6-30d3-469e-b6d2-ad1e480c67a4 | Jane | Smith   | jane.smith@example.com | premium
    d8c3cebc-c225-43f1-a2fe-e0cccd872ad7 | Alex | Smith   | alex.smith@example.com | gold
    (3 rows)
  ```
* To re-build the `api` image run: `make build`
* To stop the containers run: `make down`
* To format on a clean style the python codebase run: `make reformat`