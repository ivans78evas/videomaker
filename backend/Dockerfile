FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy dependency files
COPY pyproject.toml .
# In a real environment, we'd copy uv.lock too
# COPY uv.lock .

# Install dependencies using uv
RUN uv pip install --system .

# Copy project files
COPY . .

# Create storage directories
RUN mkdir -p backend/storage/raw_videos backend/storage/audio_stems backend/storage/transcripts

# Expose port
EXPOSE 8000

# Default command (overridden by docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
