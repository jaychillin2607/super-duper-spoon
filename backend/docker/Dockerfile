FROM python:3.13-slim

WORKDIR /app


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=prod


COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt


COPY ./app /app/app
COPY ./alembic /app/alembic
COPY alembic.ini /app/





CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]