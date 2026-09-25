#!/usr/bin/env bash
set -e

echo "Running pytest code coverage calculation..."
PYTHONPATH=src pytest --cov=wpostgresql --cov-report=term-missing --cov-report=html test/unit/
