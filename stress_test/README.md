# Stress Test Configuration

This directory contains stress tests for the wpostgresql library.

## Quick Start

### Run sync stress test (1000 users x 100 requests = 100,000 operations):
```bash
cd stress_test
python run.py --users 100 --requests 10
```

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)

### Run async stress test:
```bash
cd stress_test
python run.py --users 1000 --requests 100 --async
```

### Run with custom database:
```bash
python run.py --host localhost --port 5432 --users 500 --requests 50
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--users` | Number of concurrent users | 1000 |
| `--requests` | Requests per user | 100 |
| `--async` | Run async version | false |
| `--workers` | Max workers (sync only) | 50 |
| `--verbose` | Verbose output | false |
| `--host` | PostgreSQL host | localhost |
| `--port` | PostgreSQL port | 5432 |

## Environment Variables

You can also use environment variables:

```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=wpostgresql
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres

python run.py
```

## Requirements

- PostgreSQL running and accessible
- wpostgresql installed (`pip install wpostgresql`)
- Environment variables or CLI args for database connection

## Docker Setup

```bash
# Start PostgreSQL
cd docker
docker-compose up -d

# Run stress test
cd stress_test
python run.py --users 100 --requests 10
```
