# SQLite Backup Example

This example demonstrates how to export/backup records from a PostgreSQL table to an SQLite database file using `wsqlite`.

## Key Technologies & Libraries

- **WPostgreSQL**: PostgreSQL ORM leveraging Pydantic models.
- **wsqlite**: Lightweight SQLite ORM leveraging Pydantic models.
- **Pydantic v2**: Data validation and schema definitions.

## How it works

1. Define a Pydantic model (`Product`).
2. Initialize `WPostgreSQL(Product, db_config)` to manage PostgreSQL table operations.
3. Call `db.backup_to_sqlite("products_backup.db")` to automatically export table rows into an SQLite database powered by `wsqlite`.

## Execution

```bash
python example.py
```
