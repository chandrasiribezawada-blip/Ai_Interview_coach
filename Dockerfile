# syntax=docker/dockerfile:1

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

COPY app.py streamlit_app.py ./
COPY src ./src
COPY ui ./ui

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]