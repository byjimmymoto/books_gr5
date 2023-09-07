#!/bin/bash
screen -dm bash -c 'celery -A celery_tasks.tasks.celery worker --loglevel=info'
screen -dm bash -c 'celery -A celery_tasks.tasks.celery flower --port=5555'
uvicorn main:app --host 0.0.0.0 --port 8000


