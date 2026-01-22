FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install all system dependencies in a single layer (reduces image size)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Application code
COPY src/ /app/src

# Default command (CLI mode) - overridden by docker-compose.yml
CMD ["python", "-m", "src.main_menu"]
