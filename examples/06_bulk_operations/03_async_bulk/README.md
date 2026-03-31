# Async Bulk Operations

This example demonstrates how to perform bulk operations with async/await.

## Usage

```bash
python example.py
```

## Code

```python
import asyncio
from pydantic import BaseModel
from wpostgresql import WPostgreSQL

class Person(BaseModel):
    id: int
    name: str
    age: int

async def main():
    db = WPostgreSQL(Person, db_config)
    
    # Insert multiple records
    users = [
        Person(id=1, name="Alice", age=25),
        Person(id=2, name="Bob", age=30),
        Person(id=3, name="Charlie", age=35),
    ]
    await db.insert_many_async(users)
    
    # Update multiple
    await db.update_many_async([
        (Person(id=1, name="Alice", age=26), 1),
        (Person(id=2, name="Bob", age=31), 2),
    ])
    
    # Delete multiple
    await db.delete_many_async([3])

asyncio.run(main())
```

## Async Methods

| Method | Description |
|--------|-------------|
| `insert_many_async(data_list)` | Insert multiple records |
| `update_many_async(updates)` | Update multiple records |
| `delete_many_async(record_ids)` | Delete multiple records |

## Differences with Sync

| Sync | Async |
|------|-------|
| `db.insert_many(users)` | `await db.insert_many_async(users)` |
| `db.update_many([(...)])` | `await db.update_many_async([(...)])` |
| `db.delete_many([1,2])` | `await db.delete_many_async([1,2])` |

## Expected Output

```
Inserted: 5
Updated
Remaining: 3
```

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
