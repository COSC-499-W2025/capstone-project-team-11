FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install Git (and clean up to keep image small)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libmagic1 curl && \
    rm -rf /var/lib/apt/lists/*

#Python deps from requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

#App code fallback
COPY src/ /app/src

# ---- CLI mode (to run current scan) ----
CMD ["python", "-m", "src.scan"]

# ---- FastAPI mode (later) ----
# 1) Add these to requirements.txt:
#    fastapi==0.115.0
#    uvicorn[standard]==0.30.6
# 2) Uncomment EXPOSE and swap the CMD below, then rebuild.
# EXPOSE 8000
# CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
