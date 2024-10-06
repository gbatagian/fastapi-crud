FROM  python:3.12-slim-bullseye

RUN apt-get update
RUN apt-get -y install libpq-dev gcc
RUN pip3 install --upgrade pip
RUN pip3 install poetry

ENV POETRY_VIRTUALENVS_IN_PROJECT=1

WORKDIR /app
COPY . .

RUN poetry install

ENV PATH="/app/.venv/bin:$PATH"
