# Pagination by Page Number (Async)

This example demonstrates how to paginate results using page number with async/await.

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
    
    # Insert records
    for i in range(1, 21):
        await db.insert_async(Person(id=i, name=f"Person {i}", age=20 + i))
    
    # First page (5 records)
    page1 = await db.get_page_async(page=1, per_page=5)
    
    # Second page
    page2 = await db.get_page_async(page=2, per_page=5)
    
    # Count total
    total = await db.count_async()

asyncio.run(main())
```

## Methods

| Method | Description |
|--------|-------------|
| `get_page_async(page, per_page)` | Get records by page number |
| `get_paginated_async(limit, offset, order_by, order_desc)` | Get with limit and offset |
| `count_async()` | Count total records |

## Differences with Sync

| Sync | Async |
|------|-------|
| `db.get_page(1, 5)` | `await db.get_page_async(1, 5)` |
| `db.count()` | `await db.count_async()` |

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
