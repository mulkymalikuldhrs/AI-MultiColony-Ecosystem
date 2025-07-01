# 🐳 Agentic AI System - Production Docker Image
# Multi-stage build for optimized production deployment
# Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION
ARG COMMIT_SHA

# Add labels
LABEL maintainer="Mulky Malikul Dhaher <mulkymalikul@gmail.com>"
LABEL description="Agentic AI System - Autonomous Multi-Agent Intelligence Platform"
LABEL version=${VERSION}
LABEL build-date=${BUILD_DATE}
LABEL commit-sha=${COMMIT_SHA}
LABEL org.opencontainers.image.title="Agentic AI System"
LABEL org.opencontainers.image.description="🇮🇩 Made with ❤️ in Indonesia"
LABEL org.opencontainers.image.source="https://github.com/jakForever/Agentic-AI-Ecosystem"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r agentic && useradd -r -g agentic agentic

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=agentic:agentic . .

# Create necessary directories
RUN mkdir -p data logs reports projects ui/generated && \
    chown -R agentic:agentic /app

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production
ENV WEB_INTERFACE_HOST=0.0.0.0
ENV WEB_INTERFACE_PORT=5000

# Chrome/Selenium configuration
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_PATH=/usr/lib/chromium/
ENV SELENIUM_HEADLESS=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/api/system/status || exit 1

# Switch to app user
USER agentic

# Expose ports
EXPOSE 5000 8765

# Volume for persistent data
VOLUME ["/app/data", "/app/logs"]

# Default command
CMD ["python", "main.py"]

# Development stage (optional)
FROM production as development

USER root

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    flake8 \
    ipython \
    notebook

USER agentic

# Override command for development
CMD ["python", "main.py", "--debug"]
