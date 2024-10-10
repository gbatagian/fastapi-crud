import os

DB_SERVICE_IP = (
    "api_db" if os.getenv("ENVIRONMENT") == "docker" else "127.0.0.1"
)
DB_USER = os.getenv("POSTGRES_USER")
BD_PWD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_PORT = os.getenv("POSTGRES_PORT")

DB_URL = f"{DB_USER}:{BD_PWD}@{DB_SERVICE_IP}:{DB_PORT}/{DB_NAME}"
DB_LOG = bool(os.getenv("DB_LOG"))
