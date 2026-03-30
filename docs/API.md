# API Reference

## WPostgreSQL

Main class for PostgreSQL operations using Pydantic models.

```python
from wpostgresql import WPostgreSQL
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
    age: int

db = WPostgreSQL(Person, db_config)
```

### Constructor

```python
WPostgreSQL(model: type[BaseModel], db_config: dict)
```

**Parameters:**
- `model` (type[BaseModel]): Pydantic BaseModel class defining the table schema.
- `db_config` (dict): PostgreSQL connection configuration.
  ```python
  db_config = {
      "dbname": "mydb",
      "user": "postgres",
      "password": "password",
      "host": "localhost",
      "port": 5432,
  }
  ```

### Methods

#### insert

```python
db.insert(data: BaseModel) -> None
```

Insert a new record into the database.

```python
db.insert(Person(id=1, name="Alice", age=25))
```

#### get_all

```python
db.get_all() -> list[BaseModel]
```

Get all records from the table.

```python
all_people = db.get_all()
```

#### get_by_field

```python
db.get_by_field(**filters) -> list[BaseModel]
```

Get records filtered by specified fields.

```python
people = db.get_by_field(age=25)
people = db.get_by_field(name="Alice", age=25)
```

#### update

```python
db.update(record_id: int, data: BaseModel) -> None
```

Update a record by ID.

```python
db.update(1, Person(id=1, name="Alice", age=26))
```

#### delete

```python
db.delete(record_id: int) -> None
```

Delete a record by ID.

```python
db.delete(1)
```

#### get_paginated

```python
db.get_paginated(
    limit: int = 10,
    offset: int = 0,
    order_by: Optional[str] = None,
    order_desc: bool = False
) -> list[BaseModel]
```

Get records with pagination and optional ordering.

```python
# First 10 records
people = db.get_paginated(limit=10)

# Skip first 20, get 10
people = db.get_paginated(limit=10, offset=20)

# Order by name descending
people = db.get_paginated(limit=10, order_by="name", order_desc=True)
```

#### get_page

```python
db.get_page(page: int = 1, per_page: int = 10) -> list[BaseModel]
```

Get records by page number (1-indexed).

```python
# Get first page (10 records)
page1 = db.get_page(page=1, per_page=10)

# Get second page
page2 = db.get_page(page=2, per_page=10)
```

#### count

```python
db.count() -> int
```

Get total number of records.

```python
total = db.count()
```

#### insert_many

```python
db.insert_many(data_list: list[BaseModel]) -> None
```

Insert multiple records in a single transaction.

```python
people = [
    Person(id=1, name="Alice", age=25),
    Person(id=2, name="Bob", age=30),
    Person(id=3, name="Charlie", age=35),
]
db.insert_many(people)
```

#### update_many

```python
db.update_many(updates: list[tuple[BaseModel, int]]) -> int
```

Update multiple records. Returns number of records updated.

```python
updates = [
    (Person(id=1, name="Alice", age=26), 1),
    (Person(id=2, name="Bob", age=31), 2),
]
count = db.update_many(updates)
```

#### delete_many

```python
db.delete_many(record_ids: list[int]) -> int
```

Delete multiple records by their IDs. Returns number of records deleted.

```python
count = db.delete_many([1, 2, 3])
```

#### execute_transaction

```python
db.execute_transaction(operations: list[tuple[str, tuple]]) -> list[Any]
```

Execute multiple operations in a transaction.

```python
result = db.execute_transaction([
    ("UPDATE person SET balance = balance - 100 WHERE id = 1", None),
    ("UPDATE person SET balance = balance + 100 WHERE id = 2", None),
])
```

#### with_transaction

```python
db.with_transaction(func: Callable[[Transaction], Any]) -> Any
```

Execute a function within a transaction.

```python
def transfer(txn):
    txn.execute("UPDATE person SET balance = balance - 100 WHERE id = 1", ())
    txn.execute("UPDATE person SET balance = balance + 100 WHERE id = 2", ())

db.with_transaction(transfer)
```

---

## TableSync

Handles table synchronization between Pydantic models and PostgreSQL.

```python
from wpostgresql import TableSync

sync = TableSync(Person, db_config)
```

### Methods

#### create_if_not_exists

```python
sync.create_if_not_exists() -> None
```

Create the table if it doesn't exist.

#### sync_with_model

```python
sync.sync_with_model() -> None
```

Sync the table with the Pydantic model, adding new columns if necessary.

#### table_exists

```python
sync.table_exists() -> bool
```

Check if the table exists.

#### drop_table

```python
sync.drop_table() -> None
```

Drop the table from the database.

#### get_columns

```python
sync.get_columns() -> list[str]
```

Get list of column names.

#### create_index

```python
sync.create_index(
    columns: list[str],
    index_name: Optional[str] = None,
    unique: bool = False
) -> None
```

Create an index on specified columns.

```python
sync.create_index(["name"])
sync.create_index(["email"], unique=True)
sync.create_index(["last_name", "first_name"], index_name="idx_name")
```

#### drop_index

```python
sync.drop_index(index_name: str) -> None
```

Drop an index.

```python
sync.drop_index("idx_name")
```

#### get_indexes

```python
sync.get_indexes() -> list[dict]
```

Get list of indexes on the table.

```python
indexes = sync.get_indexes()
for idx in indexes:
    print(idx["name"], idx["definition"])
```

---

## ConnectionManager

Manages PostgreSQL connection pooling.

```python
from wpostgresql import ConnectionManager

pool = ConnectionManager(db_config, min_connections=1, max_connections=10)
conn = pool.get_connection()
# ... use connection ...
pool.release_connection(conn)
pool.close_all()
```

### Constructor

```python
ConnectionManager(
    db_config: dict,
    min_connections: int = 1,
    max_connections: int = 10
)
```

### Methods

#### get_connection

```python
pool.get_connection() -> connection
```

Get a connection from the pool.

#### release_connection

```python
pool.release_connection(conn: connection) -> None
```

Release a connection back to the pool.

#### close_all

```python
pool.close_all() -> None
```

Close all connections in the pool.

---

## Transaction

Context manager for database transactions.

```python
from wpostgresql import get_transaction

with get_transaction(db_config) as txn:
    txn.execute("INSERT INTO person VALUES (1, 'Alice')", ())
    txn.commit()
```

### Methods

#### execute

```python
txn.execute(query: str, values: tuple = None) -> Any
```

Execute a query within the transaction.

#### commit

```python
txn.commit() -> None
```

Commit the transaction.

#### rollback

```python
txn.rollback() -> None
```

Rollback the transaction.

---

## QueryBuilder

Builder for constructing SQL queries safely.

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

### Methods

#### where

```python
qb.where(field: str, operator: str, value: Any) -> QueryBuilder
```

Add WHERE condition. Valid operators: `=`, `<`, `>`, `<=`, `>=`, `!=`, `LIKE`, `IN`, `IS NULL`, `IS NOT NULL`.

#### order_by

```python
qb.order_by(field: str, descending: bool = False) -> QueryBuilder
```

Add ORDER BY clause.

#### limit

```python
qb.limit(limit: int) -> QueryBuilder
```

Add LIMIT clause.

#### offset

```python
qb.offset(offset: int) -> QueryBuilder
```

Add OFFSET clause.

#### build_select

```python
qb.build_select() -> tuple[str, tuple]
```

Build SELECT query.

#### build_count

```python
qb.build_count() -> tuple[str, tuple]
```

Build COUNT query.

#### build_delete

```python
qb.build_delete() -> tuple[str, tuple]
```

Build DELETE query.

#### reset

```python
qb.reset() -> QueryBuilder
```

Reset builder to initial state.

---

## Exceptions

### WPostgreSQLError

Base exception for all wpostgresql errors.

### ConnectionError

Raised for connection errors.

### TableSyncError

Raised during table synchronization.

### ValidationError

Raised for validation errors.

### OperationError

Raised for database operation errors.

### SQLInjectionError

Raised when SQL injection is detected.

### TransactionError

Raised for transaction errors.

---

## CLI Tool

wpostgresql provides a CLI tool for common operations.

### Installation

```bash
pip install wpostgresql
```

### Commands

#### test-connection

```bash
wpostgresql test-connection config.json
```

Test database connection.

#### init

```python
wpostgresql init config.json model.py
```

Initialize database table from Pydantic model.

#### list

```bash
wpostgresql list config.json model.py --limit 10
```

List records from a table.

#### insert

```bash
wpostgresql insert config.json model.py '{"id": 1, "name": "Alice", "age": 25}'
```

Insert a record.

#### get

```bash
wpostgresql get config.json model.py 1
```

Get a record by ID.

#### delete

```bash
wpostgresql delete config.json model.py 1
```

Delete a record by ID.

#### count

```bash
wpostgresql count config.json model.py
```

Count records in a table.

#### drop

```bash
wpostgresql drop config.json model.py
```

Drop the table.
