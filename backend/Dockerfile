FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml .

# Install dependencies using uv
RUN uv pip install --system .

# Copy project files
COPY . .

# Create storage directories
RUN mkdir -p backend/storage/raw_videos \
    backend/storage/audio_stems \
    backend/storage/transcripts \
    backend/storage/translated_audio \
    backend/storage/final_videos

# Expose port
EXPOSE 8000

# Default command (overridden by docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
