# BASE
FROM python:3.9.7-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# DEVELOPMENT
FROM base as dev
COPY . .
RUN pip install --no-cache-dir -e .

# PRODUCTION
FROM base as prod
COPY . .
RUN pip install --no-deps --no-cache-dir .