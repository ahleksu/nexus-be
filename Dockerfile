# Dockerfile for FastAPI backend REST API

FROM python:3.11-slim

WORKDIR /app

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies if any (e.g., for database drivers)
# RUN apt-get update && apt-get install -y some-package

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./app /app/app

# Expose the port the API runs on (should match Uvicorn command)
EXPOSE 8000

# Default command to run the Uvicorn server for the FastAPI application
# --reload is good for development, consider removing for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]