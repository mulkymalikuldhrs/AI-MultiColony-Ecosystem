# =============================================================================
# AI-MultiColony-Ecosystem - Production Dockerfile
# Multi-stage build for optimized production deployment
# =============================================================================

# --- Build stage ---
FROM python:3.12-slim AS builder

ARG BUILD_DATE
ARG VERSION=0.4.0
ARG COMMIT_SHA

LABEL maintainer="Mulky Malikul Dhaher <mulkymalikul@gmail.com>"
LABEL description="AI-MultiColony-Ecosystem - Autonomous Multi-Agent Intelligence Platform"
LABEL version=${VERSION}
LABEL build-date=${BUILD_DATE}
LABEL commit-sha=${COMMIT_SHA}
LABEL org.opencontainers.image.title="AI-MultiColony-Ecosystem"
LABEL org.opencontainers.image.description="Autonomous Multi-Agent Intelligence Platform"
LABEL org.opencontainers.image.source="https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# --- Development stage ---
FROM python:3.12-slim AS development

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=development

CMD ["/bin/bash"]

# --- Production stage ---
FROM python:3.12-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r agentic && useradd -r -g agentic -d /app -s /sbin/nologin agentic

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy application code
COPY --chown=agentic:agentic . .

# Create necessary directories with proper permissions
RUN mkdir -p data logs reports projects && \
    chown -R agentic:agentic /app

# Environment defaults
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    WEB_INTERFACE_HOST=0.0.0.0 \
    WEB_INTERFACE_PORT=5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/api/system/status || exit 1

USER agentic

EXPOSE 5000

VOLUME ["/app/data", "/app/logs"]

# Production: gunicorn with gevent workers
CMD ["gunicorn", \
     "--worker-class", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:5000", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "web_interface.app:app"]
