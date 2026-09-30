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
    <a href="https://pylint.org/">
        <img src="https://img.shields.io/badge/pylint-9.5%2B-green" alt="Pylint">
    </a>
    <a href="https://bandit.readthedocs.io/">
        <img src="https://img.shields.io/badge/bandit-passing-green" alt="Bandit">
    </a>
    <a href="https://pepy.tech/projects/wpostgresql">
        <img src="https://static.pepy.tech/personalized-badge/wpostgresql?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads" alt="PyPI Downloads">
    </a>
    <a href="https://github.com/wisrovi/wpostgresql/blob/main/LTS_POLICY.md">
        <img src="https://img.shields.io/badge/LTS-1.0.0-green" alt="LTS Version">
    </a>
</p>

**wpostgresql** is an enterprise-grade, type-safe PostgreSQL ORM and forensic automation engine that leverages Pydantic models for schema definition, multi-table management, and automatic audit trail tracking (`_forensic_audit_log`). It goes far beyond basic database CRUD by providing built-in change data capture (CDC), soft-deletion tracking, and full async/await support.

## Key Features

- **Enterprise Forensic Audit Engine** — Automatic creation and tracking of `_forensic_audit_log` (Ghost Table) storing before/after JSON snapshots and user audit metadata for all CRUD operations
- **Multi-Table Management** — Manage multiple database tables seamlessly from a single `WPostgreSQL([User, Product, Order])` instance with `db[User]` indexing, `db.product` attribute access, and auto-routing
- **Pydantic Integration** — Define database schemas using Pydantic v2 models with automatic type validation
- **Auto Table Synchronization** — Tables are created and updated automatically based on model changes
- **Type-Safe Operations** — Full type hints with Pydantic validation for data integrity
- **Async/Await Support** — Complete async API for high-performance applications
- **Connection Pooling** — Built-in connection pooling for both sync and async operations
- **Transaction Management** — Robust transaction support with automatic rollback
- **Bulk Operations** — Efficient bulk insert, update, and delete operations
- **SQLite Backup** — Export PostgreSQL table data directly to SQLite database files using `wsqlite`

## Technical Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| Database | PostgreSQL 13+ |
| ORM Core | psycopg 3.x, psycopg_pool |
| SQLite Backup | wsqlite |
| Validation | Pydantic 2.x |
| Logging | Loguru |
| CLI | Click |
| Testing | pytest, pytest-cov |
| Linting | ruff, pylint |
| Type Checking | mypy |
| Security | bandit, detect-secrets |
| Containerization | Docker, Docker Compose |
| Documentation | Sphinx, Read the Docs |

## Installation & Setup

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 13 or higher
- Docker (optional, for containerized setup)

### Using pip

```bash
pip install wpostgresql
```

### From Source

```bash
# Clone the repository
git clone https://github.com/wisrovi/wpostgresql.git
cd wpostgresql

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"
```

### Using Docker (Optional)

```bash
cd docker
docker-compose up -d
```

This starts:
- PostgreSQL 13.2 on port 5432
- pgAdmin4 on port 1717

## Architecture & Workflow

### File Tree

```
wpostgresql/
├── .github/
│   └── workflows/           # CI/CD pipelines
│       ├── pr-validation.yml
│       ├── test.yml
│       ├── pylint.yml
│       └── static.yml
├── src/wpostgresql/         # Core library
│   ├── __init__.py
│   ├── builders/            # SQL query builder
│   │   └── query_builder.py
│   ├── cli/                 # CLI tool
│   │   └── main.py
│   ├── core/                # ORM core
│   │   ├── connection.py    # Connection pooling
│   │   ├── repository.py   # WPostgreSQL class
│   │   └── sync.py         # Table sync
│   ├── exceptions/          # Custom exceptions
│   │   └── __init__.py
│   └── types/               # SQL type mapping
│       └── sql_types.py
├── docs/                    # Sphinx documentation
│   ├── getting_started/
│   ├── api_reference/
│   └── tutorials/
├── examples/                # Usage examples
│   ├── 01_crud/
│   ├── 02_new_columns/
│   ├── 03_restrictions/
│   ├── 04_pagination/
│   ├── 05_transactions/
│   ├── 06_bulk_operations/
│   ├── 07_connection_pooling/
│   ├── 08_logging/
│   ├── 09_async/
│   ├── 10_aggregations/
│   ├── 11_timestamps/
│   ├── 12_raw_sql/
│   ├── 13_soft_delete/
│   └── 14_relationships/
├── test/                    # Unit and integration tests
│   └── ...
├── docker/                  # Docker configuration
│   ├── docker-compose.yaml
│   └── Dockerfile.postgress
├── pyproject.toml          # Project configuration
└── README.md
```

### System Workflow

```mermaid
flowchart TD
    A[Developer defines Pydantic Model] --> B[WPostgreSQL Instance Created]
    B --> C{Table Exists?}
    C -->|No| D[TableSync creates table]
    C -->|Yes| E[Column sync check]
    D --> F[Schema synchronized]
    E -->|New columns detected| G[Add missing columns]
    E -->|No changes| H[Ready for operations]
    G --> F
    F --> H
    H --> I[CRUD Operations Available]
    I --> J[insert/get/update/delete]
    J --> K[Query Builder constructs SQL]
    K --> L[Connection Pool]
    L --> M[PostgreSQL Database]
    M --> N[Results returned as Pydantic models]
```

## Configuration

### Database Connection Configuration

Create a configuration dictionary:

```python
DB_CONFIG = {
    "dbname": "your_database",
    "user": "your_user",
    "password": "your_password",
    "host": "localhost",
    "port": 5432,
}
```

### Environment Variables (Recommended)

For production, use environment variables to avoid exposing credentials:

```python
import os

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "mydb"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
}
```

### Connection Pool Configuration

```python
POOL_CONFIG = {
    "min_size": 2,
    "max_size": 20,
    "timeout": 30,
}
```

## Usage

### Basic Sync Usage

```python
from pydantic import BaseModel
from wpostgresql import WPostgreSQL

class User(BaseModel):
    id: int
    name: str
    email: str

DB_CONFIG = {
    "dbname": "mydb",
    "user": "postgres",
    "password": "secret",
    "host": "localhost",
    "port": 5432,
}

db = WPostgreSQL(User, DB_CONFIG)

# Insert
db.insert(User(id=1, name="John", email="john@example.com"))

# Query all
users = db.get_all()

# Query by field
john = db.get_by_field(name="John")

# Update
db.update(1, User(id=1, name="Jane", email="jane@example.com"))

# Delete
db.delete(1)
```

### Async Usage

```python
import asyncio
from pydantic import BaseModel
from wpostgresql import WPostgreSQL

class User(BaseModel):
    id: int
    name: str
    email: str

async def main():
    db = WPostgreSQL(User, DB_CONFIG)
    
    await db.insert_async(User(id=1, name="John", email="john@example.com"))
    users = await db.get_all_async()
    print(users)

asyncio.run(main())
```

### SQLite Backup

Export PostgreSQL table data directly into an SQLite database file using `wsqlite`:

```python
# 1. Single Table Backup (Atomic replace by default)
db.backup_to_sqlite("backup.db")

# 2. Single Table In-place Update
db.backup_to_sqlite("backup.db", update=True)

# 3. Full Database Backup (All Pydantic models/tables into one SQLite file)
from wpostgresql import backup_db_to_sqlite, backup_db_to_sqlite_async

models = [User, Product, Order]
results = backup_db_to_sqlite(models, DB_CONFIG, "full_database.db")
# Async: await backup_db_to_sqlite_async(models, DB_CONFIG, "full_database.db")
```

### SQL Reconstruction Dump Script

Generate a standalone `.sql` script containing full DDL (`CREATE TABLE`) and DML (`INSERT INTO`) statements to reconstruct the entire database from scratch:

```python
from wpostgresql import export_to_sql_script, export_to_sql_script_async

# Export full database schema and data to a .sql script
sql_file = export_to_sql_script([User, Product, Order], DB_CONFIG, "reconstruct_db.sql")
# Async: await export_to_sql_script_async([User, Product, Order], DB_CONFIG, "reconstruct_db.sql")
```

### Forensic Audit & Soft Delete

Track user actions (`create_by`, `create_in`, `update_by`, `update_in`, `delete_by`, `delete_in`) and automatically soft-delete records (`status=99`):

```python
from wpostgresql import WPostgreSQL, ForensicModel

# Inheriting from ForensicModel automatically enables forensic audit tracking
class Document(ForensicModel):
    id: int
    title: str

db = WPostgreSQL(Document, DB_CONFIG)

# Insert with user ID tracking (defaults to 1 if omitted)
db.insert(Document(id=1, title="Report"), user_id=42)

# Update with user ID tracking
db.update(1, Document(id=1, title="Report V2"), user_id=99)

# Soft delete (sets status=99, delete_by=777, delete_in=UTC_NOW)
db.delete(1, user_id=777)

# Standard query automatically excludes soft-deleted records (WHERE status != 99)
active_docs = db.get_all()  # []

# Query including soft-deleted records
all_docs = db.get_all(include_deleted=True)  # [Document(id=1, status=99, ...)]
```

### CLI Commands

```bash
# View help
wpostgresql --help

# Sync table from model
wpostgresql sync path/to/model.py

# Check connection status
wpostgresql status
```

## Testing

Unit tests can be executed locally or inside an isolated Docker container:

```bash
# Run tests inside an isolated Docker container
./run_tests_docker.sh

# Calculate code coverage
./run_coverage.sh

# Run unit tests locally with pytest
PYTHONPATH=src pytest test/unit/
```

## Project Quality Metrics

| Metric | Status |
|--------|--------|
| Version | 1.0.0 (LTS) |
| Pylint Score | > 9.5 |
| Bandit Security | Passing |
| mypy Type Check | Passing |
| Code Coverage | 70%+ |
| Docstring Coverage | > 90% |
| Python Support | 3.9 - 3.13 |

## Contributing

Contributions are welcome. Please read our [Contributing Guide](CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE) file for details.

---

## 👤 Autor & Afiliación Oficial

* **William Steve Rodriguez Villamizar (Wisrovi)**
* **Cargo:** Principal AI Engineer & Applied AI Solutions Architect | Scientific Researcher
* 📧 **Email:** [wisrovi.rodriguez@gmail.com](mailto:wisrovi.rodriguez@gmail.com)
* 🌐 **Portal Oficial:** [wisrovi.dev](https://wisrovi.dev)
* 💼 **LinkedIn:** [wisrovi-rodriguez](https://www.linkedin.com/in/wisrovi-rodriguez/)
* 🆔 **ORCID:** [0009-0005-0710-1861](https://orcid.org/0009-0005-0710-1861)
* 📦 **PyPI:** [pypi.org/user/wisrovi/](https://pypi.org/user/wisrovi/)
* 🐙 **GitHub:** [@wisrovi](https://github.com/wisrovi)


