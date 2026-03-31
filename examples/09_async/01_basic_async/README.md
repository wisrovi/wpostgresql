# Async / Await (v0.3.0)

Este ejemplo demuestra el uso de las operaciones asíncronas en wpostgresql.

## Uso

```bash
python example.py
```

## API (v0.3.0)

```python
import asyncio
from wpostgresql import WPostgreSQL

# Misma clase, mismos métodos + versiones async
db = WPostgreSQL(User, db_config)

# Métodos sync (como antes)
db.insert(user)
db.get_all()

# Métodos async (nuevo)
await db.insert_async(user)
await db.get_all_async()
await db.get_by_field_async(name="Alice")
await db.update_async(id, user)
await db.delete_async(id)
```

## Código Completo

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
    
    # CRUD async
    await db.insert_async(Person(id=1, name="Alice", age=25))
    await db.insert_async(Person(id=2, name="Bob", age=30))
    
    users = await db.get_all_async()
    print("Usuarios:", users)
    
    await db.update_async(1, Person(id=1, name="Alice", age=26))
    await db.delete_async(2)

asyncio.run(main())
```

## Métodos Async Disponibles

| Método Sync | Método Async |
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

## Beneficios

- **No bloqueante**: Otras tareas pueden ejecutarse mientras espera la BD
- **Alto rendimiento**: Ideal para APIs con muchas solicitudes simultáneas
- **Concurrente**: Ejecuta múltiples consultas en paralelo

## Diferencias entre Sync y Async

| Sync | Async |
|------|-------|
| `db.insert(user)` | `await db.insert_async(user)` |
| `db.get_all()` | `await db.get_all_async()` |
| Bloquea el hilo | No bloquea el hilo |

## Cuándo Usar Async

- APIs web con FastAPI
- Aplicaciones con muchas conexiones simultáneas
- Microservicios
- Scripts de procesamiento en paralelo

## Requisitos

```bash
pip install wpostgresql
# O instalando dependencias directamente:
pip install psycopg[binary]>=3.1.0 psycopg_pool>=3.1.0
```

## Backwards Compatibility

Los 18,000 usuarios sync existentes pueden actualizar sin cambios:

```python
# Funciona igual que antes
db.insert(user)
users = db.get_all()

# Y ahora también puedes usar async si lo necesitas
await db.insert_async(user)
users = await db.get_all_async()
```
