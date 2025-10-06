FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy uv files
COPY pyproject.toml uv.lock ./
COPY /src/ingestion.py ./app
COPY data_test ./data

RUN pip install --upgrade pip
RUN pip install uv
RUN uv sync  # installs all dependencies from lock file


ENTRYPOINT ["python3", "ingestion.py"]
