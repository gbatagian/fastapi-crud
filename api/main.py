from fastapi import FastAPI
from fastapi import Request
from fastapi import Response

from api.endpoints.portfolio import portfolio_api
from api.endpoints.users import user_api
from repositories.base import db_context
from repositories.base import new_db_instance

app = FastAPI()
app.include_router(user_api)
app.include_router(portfolio_api)


@app.middleware("http")
async def set_db_context(request: Request, call_next):
    try:
        async with new_db_instance() as db:
            token = db_context.set(db)

            response = await call_next(request)
    finally:
        db_context.reset(token)

    return response


@app.get("/")
def get_root() -> Response:
    return Response(content="OK", status_code=200)
