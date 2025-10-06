FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
# Copy uv files
COPY pyproject.toml uv.lock ./
COPY /src/ ./
COPY data_test ./data
ENV PATH="/app/.venv/bin:$PATH"


RUN pip install --upgrade pip
RUN pip install uv
RUN uv sync



ENTRYPOINT ["python3", "ingestion.py"]
