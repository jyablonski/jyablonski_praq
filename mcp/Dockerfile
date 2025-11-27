FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

# Syncs dependencies into /app/.venv
RUN uv sync --frozen

# FIX: Add the virtual environment to the PATH so the shell finds 'uvicorn'
ENV PATH="/app/.venv/bin:$PATH"

COPY server.py .

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]