# Async / Await (v0.3.0)

This example demonstrates the use of asynchronous operations in wpostgresql.

## Usage

```bash
python example.py
```

## API (v0.3.0)

```python
import asyncio
from wpostgresql import WPostgreSQL

# Same class, same methods + async versions
db = WPostgreSQL(User, db_config)

# Sync methods (as before)
db.insert(user)
db.get_all()

# Async methods (new)
await db.insert_async(user)
await db.get_all_async()
await db.get_by_field_async(name="Alice")
await db.update_async(id, user)
await db.delete_async(id)
```

## Complete Code

```python
import asyncio
from pydantic import BaseModel
from wpostgresql import WPostgreSQL

class Person(BaseModel):
    id: int
    name: str
    age: int

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}

async def main():
    db = WPostgreSQL(Person, db_config)
    
    # Async CRUD
    await db.insert_async(Person(id=1, name="Alice", age=25))
    await db.insert_async(Person(id=2, name="Bob", age=30))
    
    users = await db.get_all_async()
    print("Users:", users)
    
    await db.update_async(1, Person(id=1, name="Alice", age=26))
    await db.delete_async(2)

asyncio.run(main())
```

## Available Async Methods

| Sync Method | Async Method |
|-------------|--------------|
| `insert()` | `insert_async()` |
| `get_all()` | `get_all_async()` |
| `get_by_field()` | `get_by_field_async()` |
| `update()` | `update_async()` |
| `delete()` | `delete_async()` |
| `get_paginated()` | `get_paginated_async()` |
| `get_page()` | `get_page_async()` |
| `count()` | `count_async()` |
| `insert_many()` | `insert_many_async()` |
| `update_many()` | `update_many_async()` |
| `delete_many()` | `delete_many_async()` |
| `execute_transaction()` | `execute_transaction_async()` |
| `with_transaction()` | `with_transaction_async()` |

## Benefits

- **Non-blocking**: Other tasks can execute while waiting for DB
- **High performance**: Ideal for APIs with many simultaneous requests
- **Concurrent**: Execute multiple queries in parallel

## Sync vs Async Differences

| Sync | Async |
|------|-------|
| `db.insert(user)` | `await db.insert_async(user)` |
| `db.get_all()` | `await db.get_all_async()` |
| Blocks thread | Non-blocking thread |

## When to Use Async

- Web APIs with FastAPI
- Applications with many simultaneous connections
- Microservices
- Parallel processing scripts

## Requirements

```bash
pip install wpostgresql
# Or installing dependencies directly:
pip install psycopg[binary]>=3.1.0 psycopg_pool>=3.1.0
```

## Backwards Compatibility

Existing 18,000 sync users can upgrade without changes:

```python
# Works the same as before
db.insert(user)
users = db.get_all()

# And now you can also use async if needed
await db.insert_async(user)
users = await db.get_all_async()
```

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
