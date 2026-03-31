# Async Transactions

This example demonstrates how to use async transactions for atomic operations.

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
    balance: float

async def main():
    db = WPostgreSQL(Person, db_config)
    
    await db.insert_async(Person(id=1, name="Alice", balance=1000))
    await db.insert_async(Person(id=2, name="Bob", balance=500))
    
    try:
        await db.execute_transaction_async([
            ("UPDATE person SET balance = balance - 100 WHERE id = 1", None),
            ("UPDATE person SET balance = balance + 100 WHERE id = 2", None),
        ])
        print("Transaction successful")
    except Exception as e:
        print("Transaction failed:", e)

asyncio.run(main())
```

## Async Methods

| Method | Description |
|--------|-------------|
| `execute_transaction_async(operations)` | Execute multiple operations in transaction |
| `with_transaction_async(func)` | Execute function within transaction |

## Differences with Sync

| Sync | Async |
|------|-------|
| `db.execute_transaction([...])` | `await db.execute_transaction_async([...])` |
| `db.with_transaction(func)` | `await db.with_transaction_async(func)` |

## Example with with_transaction_async

```python
async def transfer(txn):
    await txn.execute("UPDATE person SET balance = balance - 100 WHERE id = 1", ())
    await txn.execute("UPDATE person SET balance = balance + 100 WHERE id = 2", ())

await db.with_transaction_async(transfer)
```

## Expected Output

```
Transaction successful
Final balance Alice: 900
Final balance Bob: 600
```

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
