# Roadmap wpostgresql

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
- [ ] Documentación API completa
- [ ] CLI tool

## v1.0.0 - Release
- [ ] Código estable y testeado
- [ ] Documentación completa
- [ ] Cobertura de tests > 80% (actualmente 100%)

---

## Ejemplos disponibles

| Carpeta | Funcionalidad | Estado |
|---------|---------------|--------|
| 01_crud | Create, Read, Update, Delete | ✅ Implementado |
| 02_new_columns | Añadir columnas | ✅ Implementado |
| 03_restrictions | PK, UNIQUE, NOT NULL | ✅ Implementado |
| 04_pagination | LIMIT/OFFSET, página | ✅ Implementado |
| 05_transactions | Transacciones | ✅ Implementado |
| 06_bulk_operations | insert_many, update_many | ✅ Implementado |
| 07_connection_pooling | Pool de conexiones | ✅ Implementado |
| 08_logging | Logging con loguru | ✅ Implementado |
| 09_async | Async/await | ✅ Implementado |

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
