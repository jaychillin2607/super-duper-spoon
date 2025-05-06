FROM python:3.13-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=prod

# Install dependencies
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY ./app /app/app
COPY ./alembic /app/alembic
COPY alembic.ini /app/

# Run migrations 
# RUN alembic upgrade head

# Run migrations and start app
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]