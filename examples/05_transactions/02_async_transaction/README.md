# Transacciones Asíncronas

Este ejemplo muestra cómo usar transacciones async para operaciones atómicas.

## Uso

```bash
python example.py
```

## Código

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
        print("Transacción exitosa")
    except Exception as e:
        print("Transacción fallida:", e)

asyncio.run(main())
```

## Métodos Async

| Método | Descripción |
|--------|-------------|
| `execute_transaction_async(operations)` | Ejecuta múltiples operaciones en transacción |
| `with_transaction_async(func)` | Ejecuta función dentro de transacción |

## Diferencias con Sync

| Sync | Async |
|------|-------|
| `db.execute_transaction([...])` | `await db.execute_transaction_async([...])` |
| `db.with_transaction(func)` | `await db.with_transaction_async(func)` |

## Ejemplo con with_transaction_async

```python
async def transfer(txn):
    await txn.execute("UPDATE person SET balance = balance - 100 WHERE id = 1", ())
    await txn.execute("UPDATE person SET balance = balance + 100 WHERE id = 2", ())

await db.with_transaction_async(transfer)
```

## Resultado Esperado

```
Transacción exitosa
Saldo final Alice: 900
Saldo final Bob: 600
```
