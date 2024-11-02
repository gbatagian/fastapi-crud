import asyncio
import datetime

import httpx
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi.responses import JSONResponse

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


@app.get("/benchmark-serial")
async def benchmark_serial() -> Response:
    start = datetime.datetime.now()
    stats = {}
    while True:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://localhost:8000/users")

        if r.status_code in stats:
            stats[r.status_code] += 1
        else:
            stats[r.status_code] = 1

        if datetime.datetime.now() - start > datetime.timedelta(minutes=1):
            break

    return JSONResponse(content=stats, status_code=200)


@app.get("/benchmark-concurrent/{n}")
async def benchmark_concurrent(n: int) -> Response:

    stats = {}
    async with httpx.AsyncClient(timeout=None) as client:
        tasks = [client.get("http://localhost:8000/users") for _ in range(n)]

        start = datetime.datetime.now()
        await asyncio.gather(*tasks)

    stats["time_taken"] = f"{datetime.datetime.now() - start}"
    return JSONResponse(content=stats, status_code=200)
