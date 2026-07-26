FROM python:3.13.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY mcp/requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt

# The MCP service is an adapter over the shared Cube client and validation
# policy; it does not maintain a second query implementation.
COPY shared ./shared
COPY mcp/server.py ./

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
