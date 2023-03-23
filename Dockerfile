FROM python:3.10.2-slim-buster as build
WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app/job_tracker"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY job_tracker /app/job_tracker
COPY pyproject.toml poetry.lock .env /app/
RUN pip install --upgrade pip
RUN pip install poetry==1.4.1
RUN poetry config virtualenvs.create false
RUN poetry install --only main
FROM build as run
COPY --from=build /app/job_tracker/ /app/job_tracker/
CMD ["uvicorn", "job_tracker.etl:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
