# Dockerfile для Playwright Lambda
FROM mcr.microsoft.com/playwright/python:v1.56.0-noble

WORKDIR /workspace

COPY . /workspace

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
