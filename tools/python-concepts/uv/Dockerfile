FROM python:3.12-slim AS base

ENV POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1

FROM base AS python-deps

# Update and upgrade system packages before installing uv
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync

FROM base AS runtime

COPY --from=python-deps ./.venv ./.venv
ENV PATH="/.venv/bin:$PATH"

RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser

COPY main.py ./

CMD ["python", "main.py"]