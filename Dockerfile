# Use official UV Docker image
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv pip (faster than uv sync)
RUN uv pip install --system -r pyproject.toml --no-cache

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/data /app/output

EXPOSE 8000

# Run with uvicorn directly (no need for "uv run")
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]