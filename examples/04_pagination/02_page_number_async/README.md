# Paginación por Número de Página (Async)

Este ejemplo muestra cómo paginar resultados usando número de página con async/await.

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
    
    # Insertar registros
    for i in range(1, 21):
        await db.insert_async(Person(id=i, name=f"Person {i}", age=20 + i))
    
    # Primera pagina (5 registros)
    page1 = await db.get_page_async(page=1, per_page=5)
    
    # Segunda pagina
    page2 = await db.get_page_async(page=2, per_page=5)
    
    # Contar total
    total = await db.count_async()

asyncio.run(main())
```

## Métodos

| Método | Descripción |
|--------|-------------|
| `get_page_async(page, per_page)` | Obtiene registros por número de página |
| `get_paginated_async(limit, offset, order_by, order_desc)` | Obtiene con límite y offset |
| `count_async()` | Cuenta total de registros |

## Diferencias con Sync

| Sync | Async |
|------|-------|
| `db.get_page(1, 5)` | `await db.get_page_async(1, 5)` |
| `db.count()` | `await db.count_async()` |
