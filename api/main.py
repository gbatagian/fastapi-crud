from fastapi import FastAPI
from fastapi import Response

from api.endpoints.portfolio import portfolio_api
from api.endpoints.users import user_api

app = FastAPI()
app.include_router(user_api)
app.include_router(portfolio_api)


@app.get("/")
def get_root() -> Response:
    return Response(content="OK", status_code=200)
