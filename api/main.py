from fastapi import FastAPI
from fastapi import Request
from fastapi import Response

from api.endpoints.portfolio import portfolio_api
from api.endpoints.users import user_api
from repositories.base import SessionManager
from repositories.base import session_manager_context

app = FastAPI()
app.include_router(user_api)
app.include_router(portfolio_api)


@app.middleware("http")
async def set_db_context(request: Request, call_next):
    try:
        db = SessionManager()
        token = session_manager_context.set(db)

        response = await call_next(request)
    finally:
        db.close()
        session_manager_context.reset(token)

    return response


@app.get("/")
def get_root() -> Response:
    return Response(content="OK", status_code=200)
