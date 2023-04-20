FROM python:3.10

WORKDIR /app

COPY pyproject.toml /app/
COPY poetry.lock /app/
RUN pip install poetry && poetry install --only main


