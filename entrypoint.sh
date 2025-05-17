#!/bin/sh

if [ "$ENV" = "production" ]; then
    echo "Running in production mode with Gunicorn"
    exec gunicorn -k uvicorn.workers.UvicornWorker main:app \
        --bind 0.0.0.0:8003 \
        --workers 1 \
        --threads 2 \
        --timeout 120
elif [ "$ENV" = "testing" ]; then
    echo "Running in testing mode with Gunicorn"
    exec gunicorn -k uvicorn.workers.UvicornWorker main:app \
        --bind 0.0.0.0:8002 \
        --workers 1 \
        --timeout 120
else
    echo "Running in development mode with Uvicorn"
    exec uvicorn main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload
fi

