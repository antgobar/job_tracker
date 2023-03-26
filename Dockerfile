FROM python:3.10.2-slim-buster as build
WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app/job_tracker"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY job_tracker /app/job_tracker
COPY pyproject.toml poetry.lock /app/

RUN pip install --upgrade pip
RUN pip install poetry==1.4.1
RUN poetry config virtualenvs.create false
RUN poetry install --only main

FROM build as run
RUN useradd -r -s /bin/bash app_user
RUN chown -R app_user:app_user /app
USER app_user

ARG MONGO_URI
ARG API_USER
ARG API_KEY
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION

ENV MONGO_URI $MONGO_URI
ENV API_USER $API_USER
ENV API_KEY $API_KEY
ENV AWS_ACCESS_KEY_ID $AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY $AWS_SECRET_ACCESS_KEY
ENV AWS_DEFAULT_REGION $AWS_DEFAULT_REGION

COPY --from=build /app/job_tracker/ /app/job_tracker/

CMD ["uvicorn", "job_tracker.etl:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
