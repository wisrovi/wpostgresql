#!/usr/bin/env bash
set -e

echo "Running unit tests inside Docker container..."
docker run --rm \
  --network host \
  -v "$(pwd):/app" \
  -w /app \
  python:3.11-slim \
  bash -c "pip install -e .[dev] loguru pytest psycopg[binary] pydantic && pytest test/unit/"
