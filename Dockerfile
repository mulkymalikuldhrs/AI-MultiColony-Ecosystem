# ╔══════════════════════════════════════════════════════════════════════╗
# ║    AI-MultiColony-Ecosystem  —  Multi-stage Production Dockerfile    ║
# ╚══════════════════════════════════════════════════════════════════════╝

# ── Stage 1: Builder ──────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.5

# Copy dependency files first (for Docker layer caching)
COPY pyproject.toml ./

# Install dependencies (no dev, no root project)
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi || \
    pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings \
    sqlalchemy alembic asyncpg redis numpy pandas scipy scikit-learn \
    langgraph langchain-core httpx orjson rich click structlog tenacity psutil

# ── Stage 2: Production ──────────────────────────────────────────────
FROM python:3.12-slim AS production

# Metadata
LABEL maintainer="AI-MultiColony-Ecosystem Team"
LABEL description="Colony-Based Autonomous Agent Operating System"
LABEL version="0.2.0"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r amce \
    && useradd -r -g amce -d /app -s /sbin/nologin amce

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code (ai_multicolony is the actual package)
COPY --chown=amce:amce ai_multicolony/ ./ai_multicolony/
COPY --chown=amce:amce quant_nanggroe/ ./quant_nanggroe/
COPY --chown=amce:amce alembic/ ./alembic/
COPY --chown=amce:amce alembic.ini ./alembic.ini
COPY --chown=amce:amce scripts/ ./scripts/
COPY --chown=amce:amce database/ ./database/
COPY --chown=amce:amce connectors/ ./connectors/
COPY --chown=amce:amce config/ ./config/
COPY --chown=amce:amce main.py ./main.py

# Environment
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Make entrypoint executable
RUN chmod +x /app/scripts/entrypoint.sh

# Run as non-root user
USER amce

# Entrypoint runs migrations then starts the app
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Default command (can be overridden for worker service)
CMD ["uvicorn", "ai_multicolony.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
