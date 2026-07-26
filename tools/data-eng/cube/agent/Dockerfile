FROM python:3.13.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY agent/requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt

COPY shared ./shared
COPY agent/app.py agent/evaluations.yml agent/policies.py agent/prompts.py agent/tools.py ./
COPY agent/tests ./tests

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
