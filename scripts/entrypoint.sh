#!/bin/bash
# Docker entrypoint script for AI MultiColony Ecosystem

set -e

echo "Starting AI MultiColony Ecosystem..."

# Ensure data directory exists
mkdir -p /app/data

# Wait for Redis if needed
if [ -n "$REDIS_URL" ]; then
    echo "Waiting for Redis..."
    for i in $(seq 1 30); do
        if python -c "import redis; r=redis.from_url('$REDIS_URL'); r.ping()" 2>/dev/null; then
            echo "Redis is ready"
            break
        fi
        echo "  Attempt $i/30..."
        sleep 1
    done
fi

# Wait for Qdrant if needed
if [ -n "$QDRANT_URL" ]; then
    echo "Waiting for Qdrant..."
    for i in $(seq 1 30); do
        if curl -sf "$QDRANT_URL/health" > /dev/null 2>&1; then
            echo "Qdrant is ready"
            break
        fi
        echo "  Attempt $i/30..."
        sleep 1
    done
fi

# Execute the main command
exec "$@"
