# wpostgresql

<p align="center">
    <a href="https://pypi.org/project/wpostgresql/">
        <img src="https://img.shields.io/pypi/v/wpostgresql.svg" alt="PyPI version">
    </a>
    <a href="https://pypi.org/project/wpostgresql/">
        <img src="https://img.shields.io/pypi/pyversions/wpostgresql.svg" alt="Python versions">
    </a>
    <a href="https://github.com/wisrovi/wpostgresql/blob/main/LICENSE">
        <img src="https://img.shields.io/pypi/l/wpostgresql.svg" alt="License">
    </a>
    <a href="https://github.com/wisrovi/wpostgresql/actions">
        <img src="https://github.com/wisrovi/wpostgresql/actions/workflows/test.yml/badge.svg" alt="Tests">
    </a>
</p>

Simple and type-safe PostgreSQL ORM using Pydantic models. Define your schema with Pydantic, and wpostgresql handles the rest.

## Features

- **Pydantic Integration** - Define your database schema using Pydantic models
- **Auto Table Creation** - Tables are created/synchronized automatically
- **CRUD Operations** - Simple insert, get, update, delete methods
- **Column Sync** - Automatically adds new columns when your model changes
- **Constraints** - Support for Primary Key, UNIQUE, and NOT NULL
- **Type Safety** - Full type hints and Pydantic validation

## Installation

```bash
pip install wpostgresql
```

## Quick Start

```python
from pydantic import BaseModel
from wpostgresql import WPostgreSQL

# Database configuration
DB_CONFIG = {
    "dbname": "mydb",
    "user": "postgres",
    "password": "secret",
    "host": "localhost",
    "port": 5432,
}

# Define your model with Pydantic
class User(BaseModel):
    id: int
    name: str
    email: str

# Create database instance - table is created automatically
db = WPostgreSQL(User, DB_CONFIG)

# Insert data
db.insert(User(id=1, name="John", email="john@example.com"))

# Query data
users = db.get_all()
print(users)

# Query by field
john = db.get_by_field(name="John")
```

## Requirements

- Python 3.9+
- PostgreSQL
- psycopg2-binary
- pydantic
- loguru

## Examples

The `examples/` directory contains comprehensive examples:

| Folder | Description | Status |
|--------|-------------|--------|
| [01_crud](examples/01_crud/) | Create, Read, Update, Delete operations | ✅ |
| [02_new_columns](examples/02_new_columns/) | Adding columns to existing tables | ✅ |
| [03_restrictions](examples/03_restrictions/) | Primary Key, UNIQUE, NOT NULL | ✅ |
| [04_pagination](examples/04_pagination/) | LIMIT/OFFSET pagination | 🔄 |
| [05_transactions](examples/05_transactions/) | Database transactions | 🔄 |
| [06_bulk_operations](examples/06_bulk_operations/) | Bulk insert/update | 🔄 |
| [07_connection_pooling](examples/07_connection_pooling/) | Connection pooling | 🔄 |
| [08_logging](examples/08_logging/) | Logging configuration | 🔄 |
| [09_async](examples/09_async/) | Async/await support | 🔄 |

## Testing

Run tests with pytest:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=wpostgresql --cov-report=html
```

## Project Structure

```
wpostgresql/
├── wpostgresql/          # Main library
│   └── wpostgresql/
│       └── controller.py
├── examples/             # Usage examples
│   ├── 01_crud/
│   ├── 02_new_columns/
│   ├── 03_restrictions/
│   └── test/            # Example tests
├── test/                # Library tests
│   ├── unit/
│   └── integration/
├── docker/              # Docker configuration for local development
│   ├── docker-compose.yaml
│   └── Dockerfile.postgres
├── pyproject.toml       # Project configuration
└── README.md
```

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

William Steve Rodriguez Villamizar - [wisrovi.rodriguez@gmail.com](mailto:wisrovi.rodriguez@gmail.com)
