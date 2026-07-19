ARG PYTHON_IMAGE=python:3.12.11-slim
FROM ${PYTHON_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --system recoverops \
    && useradd --system --gid recoverops --home-dir /app recoverops

COPY recoverops_api ./recoverops_api

USER recoverops
EXPOSE 8080

CMD ["uvicorn", "recoverops_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
