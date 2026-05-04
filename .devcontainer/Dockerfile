FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get clean

ENV PATH="/root/.local/bin:$PATH"