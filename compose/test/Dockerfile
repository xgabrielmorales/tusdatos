FROM --platform=linux/x86_64 python:3.11-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH "${PYTHONPATH}:/app"

ARG APP_NAME="tusdatos"

RUN groupadd --system "${APP_NAME}" \
    && adduser \
        --no-create-home \
        --disabled-password \
        --shell "/sbin/nologin" \
        --ingroup "${APP_NAME}" \
        "${APP_NAME}"

RUN python3 -m pip install poetry \
  && poetry config virtualenvs.create false

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pypoetry \
  --mount=type=bind,source=./pyproject.toml,target=./pyproject.toml \
  --mount=type=bind,source=./poetry.lock,target=./poetry.lock \
  poetry install --no-directory --no-root --with test

COPY --chmod=0755 ./compose/dev/start /start

USER ${APP_NAME}
