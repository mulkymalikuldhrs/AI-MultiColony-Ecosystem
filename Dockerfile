# Agentic AI System - Docker Configuration
# Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=web_interface.app
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs logs/shell data temp reports

# Create non-root user
RUN useradd -m -u 1000 agentic && \
    chown -R agentic:agentic /app

# Switch to non-root user
USER agentic

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/system/status || exit 1

# Default command
CMD ["python", "start_system.py"]

# Alternative commands for different deployment scenarios:
# For development:
# CMD ["python", "start_system.py"]
# 
# For production with Gunicorn:
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "web_interface.app:app"]
