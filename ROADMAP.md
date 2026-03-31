# Roadmap wpostgresql

## v0.3.0 - Async Support (Current)

- [x] Migrate from psycopg2-binary to psycopg (v3.x)
- [x] Add psycopg_pool for connection pooling
- [x] Full async/await support (13 new async methods in WPostgreSQL)
- [x] AsyncTableSync class (9 async methods)
- [x] AsyncTransaction and AsyncConnectionManager
- [x] Backwards compatibility maintained (18,000+ users)
- [x] 89 unit tests passing

## v0.2.0 - Estabilidad

- [x] Tests con pytest (111 tests, 100% coverage)
- [x] Connection pooling (ConnectionManager class)
- [x] Logging con loguru (integración nativa)
- [x] Excepciones personalizadas (SQLInjectionError, TransactionError, etc.)
- [x] Validación anti-SQL injection (validate_identifier)

## v0.3.0 - Funcionalidad

- [x] Paginación en get_paginated() y get_page()
- [x] Soporte para transacciones (execute_transaction, with_transaction)
- [x] Métodos bulk (insert_many, update_many, delete_many)
- [x] Query builder básico (QueryBuilder class)

## v0.4.0 - Enhancements

- [x] Soporte para índices (create_index, drop_index, get_indexes)
- [x] Async support (WPostgreSQLAsync example)
- [x] Documentación API completa (docs/API.md)
- [x] CLI tool (wpostgresql CLI)

## v1.0.0 - Release

- [x] Código estable y testeado
- [x] Documentación completa
- [x] Cobertura de tests > 80% (actualmente 98%)

---

## Ejemplos disponibles

| Carpeta | Funcionalidad | Estado |
|---------|---------------|--------|
| 01_crud | Create, Read, Update, Delete | ✅ |
| 02_new_columns | Añadir columnas | ✅ |
| 03_restrictions | PK, UNIQUE, NOT NULL | ✅ |
| 04_pagination | LIMIT/OFFSET, página | ✅ |
| 05_transactions | Transacciones | ✅ |
| 06_bulk_operations | insert_many, update_many | ✅ |
| 07_connection_pooling | Pool de conexiones | ✅ |
| 08_logging | Logging con loguru | ✅ |
| 09_async | Async/await | ✅ |

---

## Nuevas características implementadas

### Paginación
```python
# Usando limit/offset
db.get_paginated(limit=10, offset=0, order_by="name", order_desc=True)

# Usando número de página
db.get_page(page=1, per_page=10)

# Contar registros
db.count()
```

### Transacciones
```python
# Método simple
db.execute_transaction([
    ("UPDATE person SET balance = balance - 100 WHERE id = 1", None),
    ("UPDATE person SET balance = balance + 100 WHERE id = 2", None),
])

# Método con función
db.with_transaction(lambda txn: txn.execute("SELECT 1", ()))
```

### Bulk Operations
```python
# Insertar muchos
db.insert_many([Person(id=1, name="Alice"), Person(id=2, name="Bob")])

# Actualizar muchos
db.update_many([(Person(id=1, name="Alice"), 1), (Person(id=2, name="Bob"), 2)])

# Eliminar muchos
db.delete_many([1, 2, 3])
```

### Índices
```python
sync = TableSync(Person, db_config)
sync.create_index(["name", "age"], unique=False)
sync.drop_index("idx_name")
indexes = sync.get_indexes()
```

### Query Builder
```python
from wpostgresql import QueryBuilder

qb = (
    QueryBuilder("users")
    .where("age", ">", 18)
    .where("city", "=", "NYC")
    .order_by("name", descending=True)
    .limit(10)
    .offset(20)
)

query, values = qb.build_select()
```

### Validación Anti-SQL Injection
```python
from wpostgresql import validate_identifier

validate_identifier("users")  # OK
validate_identifier("users; DROP TABLE")  # Raises SQLInjectionError
```

### Async/Await Support (v0.3.0)

```python
import asyncio
from wpostgresql import WPostgreSQL

class User(BaseModel):
    id: int
    name: str
    email: str

async def main():
    db = WPostgreSQL(User, db_config)
    
    # Async CRUD operations
    await db.insert_async(User(id=1, name="John", email="john@example.com"))
    users = await db.get_all_async()
    await db.update_async(1, User(id=1, name="John", email="john@example.com"))
    await db.delete_async(1)
    
    # Async pagination
    users = await db.get_paginated_async(limit=10, offset=0)
    users = await db.get_page_async(page=1, per_page=10)
    count = await db.count_async()
    
    # Async bulk operations
    await db.insert_many_async([User(...) for i in range(100)])
    await db.update_many_async([(User(...), id) for id in ids])
    await db.delete_many_async([1, 2, 3])
    
    # Async transactions
    await db.execute_transaction_async([("INSERT...", (...)), ("UPDATE...", (...))])
    await db.with_transaction_async(async lambda txn: txn.execute(...))

asyncio.run(main())
```

### Async TableSync

```python
sync = TableSync(Person, db_config)

# Sync operations
sync.create_if_not_exists()
sync.sync_with_model()

# Async operations
await sync.create_if_not_exists_async()
await sync.sync_with_model_async()
await sync.table_exists_async()
await sync.drop_table_async()
await sync.get_columns_async()
await sync.create_index_async(["name"], unique=False)
await sync.drop_index_async("idx_name")
await sync.get_indexes_async()
```
