# syntax=docker/dockerfile:1
# Multi-platform build support for amd64, arm64
FROM --platform=$BUILDPLATFORM python:3.11-slim AS base

# Build arguments for multi-platform support
ARG BUILDPLATFORM
ARG TARGETPLATFORM
ARG TARGETARCH

# Labels for metadata
LABEL maintainer="Business Gemini Pool"
LABEL description="Business Gemini Pool - Google Gemini Enterprise API Proxy Service"
LABEL version="latest"
LABEL org.opencontainers.image.source="https://github.com/your-org/business-gemini-pool"
LABEL org.opencontainers.image.licenses="MIT"

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=60 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies for all platforms
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user with consistent UID across platforms
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies with robust error handling
RUN echo "Starting Python dependencies installation..." && \
    pip install --no-cache-dir --upgrade pip setuptools wheel && \
    echo "pip upgrade successful, installing requirements..." && \
    pip install --no-cache-dir -r requirements.txt && \
    echo "Requirements installed successfully, cleaning cache..." && \
    pip cache purge || echo "Cache purge completed (or failed, continuing)"

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/image /app/logs && \
    chown -R appuser:appuser /app && \
    chmod 755 /app

# Health check dependencies
RUN pip install --no-cache-dir requests

# Switch to non-root user
USER appuser

# Expose the port (Note: This is for documentation, actual port mapping is done at runtime)
EXPOSE 8000

# Health check with timeout and error handling
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys, requests, time; \
               try: \
                   requests.get('http://localhost:8000/health', timeout=5); \
                   sys.exit(0); \
               except Exception as e: \
                   sys.exit(1)" || \
    exit 1

# Default command
CMD ["python", "-u", "app.py"]
