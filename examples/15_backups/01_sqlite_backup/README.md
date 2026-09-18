# SQLite Backup Example

This example demonstrates how to export/backup records from a PostgreSQL table to an SQLite database file using `wsqlite`.

## Key Technologies & Libraries

- **WPostgreSQL**: PostgreSQL ORM leveraging Pydantic models.
- **wsqlite**: Lightweight SQLite ORM leveraging Pydantic models.
- **Pydantic v2**: Data validation and schema definitions.

## How it works

1. Define a Pydantic model (`Product`).
2. Initialize `WPostgreSQL(Product, db_config)` to manage PostgreSQL table operations.
3. Call backup methods:
   - **Sync Atomic Replace (`update=False`, default):** `db.backup_to_sqlite("products_backup.db")`
   - **Sync In-Place Update (`update=True`):** `db.backup_to_sqlite("products_backup.db", update=True)`
   - **Async Atomic Replace:** `await db.backup_to_sqlite_async("products_backup_async.db")`
   - **Async In-Place Update (`update=True`):** `await db.backup_to_sqlite_async("products_backup_async.db", update=True)`

## Execution

```bash
python example.py
```
