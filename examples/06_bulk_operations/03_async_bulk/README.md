# Operaciones Bulk Asíncronas

Este ejemplo muestra cómo realizar operaciones en lote con async/await.

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
    age: int

async def main():
    db = WPostgreSQL(Person, db_config)
    
    # Insertar múltiples registros
    users = [
        Person(id=1, name="Alice", age=25),
        Person(id=2, name="Bob", age=30),
        Person(id=3, name="Charlie", age=35),
    ]
    await db.insert_many_async(users)
    
    # Actualizar múltiples
    await db.update_many_async([
        (Person(id=1, name="Alice", age=26), 1),
        (Person(id=2, name="Bob", age=31), 2),
    ])
    
    # Eliminar múltiples
    await db.delete_many_async([3])

asyncio.run(main())
```

## Métodos Async

| Método | Descripción |
|--------|-------------|
| `insert_many_async(data_list)` | Inserta múltiples registros |
| `update_many_async(updates)` | Actualiza múltiples registros |
| `delete_many_async(record_ids)` | Elimina múltiples registros |

## Diferencias con Sync

| Sync | Async |
|------|-------|
| `db.insert_many(users)` | `await db.insert_many_async(users)` |
| `db.update_many([(...)])` | `await db.update_many_async([(...)])` |
| `db.delete_many([1,2])` | `await db.delete_many_async([1,2])` |

## Resultado Esperado

```
Insertados: 5
Actualizados
Restantes: 3
```
