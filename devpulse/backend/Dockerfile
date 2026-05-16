# /devpulse/backend/Dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.11-slim

# TODO: Push image to ECR — aws ecr get-login-password | docker login, then tag and push

RUN useradd -m appuser
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY . /app
USER appuser
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
