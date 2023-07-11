FROM python:3.9.17-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    git

RUN python -m pip install --upgrade pip

COPY ./src/requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r ./requirements.txt

COPY ./src /app

RUN pip install --editable .

RUN chmod +x docker-entrypoint.sh update.sh server-gunicorn.sh celery-worker.sh

ENTRYPOINT ./docker-entrypoint.sh
