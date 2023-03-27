FROM public.ecr.aws/lambda/python:3.10 as build
WORKDIR /${LAMBDA_TASK_ROOT}

ENV PYTHONPATH "${PYTHONPATH}:/${LAMBDA_TASK_ROOT}/job_tracker"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY job_tracker /${LAMBDA_TASK_ROOT}/job_tracker
COPY pyproject.toml poetry.lock /${LAMBDA_TASK_ROOT}/

RUN pip install --upgrade pip
RUN pip install poetry==1.4.1
RUN poetry config virtualenvs.create false
RUN poetry install --only main

FROM build as run

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

COPY --from=build /${LAMBDA_TASK_ROOT}/job_tracker/ /${LAMBDA_TASK_ROOT}/job_tracker/

CMD ["uvicorn", "job_tracker.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
