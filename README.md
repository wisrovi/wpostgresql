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
- **Async Support** - Full async/await support for high-performance applications
- **Connection Pooling** - Built-in connection pooling for both sync and async

## Installation

```bash
pip install wpostgresql
```

## Quick Start (Sync)

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

## Quick Start (Async)

```python
import asyncio
from pydantic import BaseModel
from wpostgresql import WPostgreSQL

DB_CONFIG = {
    "dbname": "mydb",
    "user": "postgres",
    "password": "secret",
    "host": "localhost",
    "port": 5432,
}

class User(BaseModel):
    id: int
    name: str
    email: str

async def main():
    db = WPostgreSQL(User, DB_CONFIG)
    
    # Async insert
    await db.insert_async(User(id=1, name="John", email="john@example.com"))
    
    # Async query
    users = await db.get_all_async()
    print(users)

asyncio.run(main())
```

## Requirements

- Python 3.9+
- PostgreSQL
- psycopg (version 3.x)
- psycopg_pool
- pydantic
- loguru

## Examples

The `examples/` directory contains comprehensive examples:

| Folder | Description | Status |
|--------|-------------|--------|
| [01_crud](examples/01_crud/) | Create, Read, Update, Delete operations | ✅ |
| [02_new_columns](examples/02_new_columns/) | Adding columns to existing tables | ✅ |
| [03_restrictions](examples/03_restrictions/) | Primary Key, UNIQUE, NOT NULL | ✅ |
| [04_pagination](examples/04_pagination/) | LIMIT/OFFSET pagination | ✅ |
| [05_transactions](examples/05_transactions/) | Database transactions | ✅ |
| [06_bulk_operations](examples/06_bulk_operations/) | Bulk insert/update | ✅ |
| [07_connection_pooling](examples/07_connection_pooling/) | Connection pooling | ✅ |
| [08_logging](examples/08_logging/) | Logging configuration | ✅ |
| [09_async](examples/09_async/) | Async/await support | ✅ |

## API Overview

### WPostgreSQL (Sync Methods)

| Method | Description |
|--------|-------------|
| `insert(data)` | Insert a record |
| `get_all()` | Get all records |
| `get_by_field(**filters)` | Get records by field filter |
| `update(record_id, data)` | Update a record |
| `delete(record_id)` | Delete a record |
| `get_paginated(limit, offset, order_by, order_desc)` | Get paginated records |
| `get_page(page, per_page)` | Get records by page number |
| `count()` | Count total records |
| `insert_many(data_list)` | Insert multiple records |
| `update_many(updates)` | Update multiple records |
| `delete_many(record_ids)` | Delete multiple records |
| `execute_transaction(operations)` | Execute multiple operations in a transaction |
| `with_transaction(func)` | Execute a function within a transaction |

### WPostgreSQL (Async Methods)

All sync methods have async equivalents with `_async` suffix:

| Method | Description |
|--------|-------------|
| `insert_async(data)` | Insert a record (async) |
| `get_all_async()` | Get all records (async) |
| `get_by_field_async(**filters)` | Get records by field filter (async) |
| `update_async(record_id, data)` | Update a record (async) |
| `delete_async(record_id)` | Delete a record (async) |
| `get_paginated_async(...)` | Get paginated records (async) |
| `get_page_async(page, per_page)` | Get records by page number (async) |
| `count_async()` | Count total records (async) |
| `insert_many_async(data_list)` | Insert multiple records (async) |
| `update_many_async(updates)` | Update multiple records (async) |
| `delete_many_async(record_ids)` | Delete multiple records (async) |
| `execute_transaction_async(operations)` | Execute transaction (async) |
| `with_transaction_async(func)` | Execute function in transaction (async) |

### TableSync

| Method | Description |
|--------|-------------|
| `create_if_not_exists()` | Create table if not exists |
| `sync_with_model()` | Sync table with Pydantic model |
| `table_exists()` | Check if table exists |
| `drop_table()` | Drop the table |
| `get_columns()` | Get list of columns |
| `create_index(columns, index_name, unique)` | Create an index |
| `drop_index(index_name)` | Drop an index |
| `get_indexes()` | Get list of indexes |

Async versions available with `_async` suffix.

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
├── src/wpostgresql/        # Main library
│   ├── core/
│   │   ├── connection.py   # Connection management
│   │   ├── repository.py  # WPostgreSQL class
│   │   └── sync.py        # Table synchronization
│   ├── builders/          # Query builder
│   ├── exceptions/        # Custom exceptions
│   ├── types/             # SQL type mapping
│   └── cli/              # CLI tool
├── examples/              # Usage examples
│   ├── 01_crud/
│   ├── 02_new_columns/
│   ├── 03_restrictions/
│   └── 09_async/         # Async examples
├── test/                  # Library tests
│   ├── unit/
│   └── integration/
├── docker/                # Docker configuration
├── pyproject.toml         # Project configuration
└── README.md
```

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

William Steve Rodriguez Villamizar - [wisrovi.rodriguez@gmail.com](mailto:wisrovi.rodriguez@gmail.com)
