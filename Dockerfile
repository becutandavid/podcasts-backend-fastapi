FROM python:3.10

WORKDIR /app

COPY pyproject.toml /app/
COPY requirements.txt /app/
RUN pip install -r requirements.txt


