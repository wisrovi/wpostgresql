#!/bin/bash
# Stress test runner for wpostgresql
# Usage: ./run_stress_test.sh [--users N] [--requests M] [--async] [--host HOST] [--port PORT]

# Default values
USERS=10000
REQUESTS=1000
ASYNC=false
HOST=localhost
PORT=5432

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --users)
            USERS="$2"
            shift 2
            ;;
        --requests)
            REQUESTS="$2"
            shift 2
            ;;
        --async)
            ASYNC=true
            shift
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--users N] [--requests M] [--async] [--host HOST] [--port PORT]"
            exit 1
            ;;
    esac
done

echo "Starting wpostgresql stress test..."
echo "Users: $USERS, Requests per user: $REQUESTS, Async: $ASYNC, Host: $HOST, Port: $PORT"

cd stress_test
if [ "$ASYNC" = true ]; then
    python run.py --users "$USERS" --requests "$REQUESTS" --async --host "$HOST" --port "$PORT"
else
    python run.py --users "$USERS" --requests "$REQUESTS" --host "$HOST" --port "$PORT"
fi

echo "Stress test completed."