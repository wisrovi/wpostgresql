# Full Database Backup & SQL Script Export Example

This example demonstrates how to:
1. Export/backup multiple PostgreSQL tables (entire database) into a single SQLite database file using `backup_db_to_sqlite` / `backup_db_to_sqlite_async`.
2. Generate a clean SQL reconstruction script (`.sql`) containing DDL (`CREATE TABLE`) and DML (`INSERT INTO`) using `export_to_sql_script` / `export_to_sql_script_async`.

## Key Technologies & Libraries

- **WPostgreSQL**: PostgreSQL ORM leveraging Pydantic models.
- **wsqlite**: Lightweight SQLite ORM leveraging Pydantic models.
- **Pydantic v2**: Data validation and schema definitions.

## How it works

1. Define your Pydantic models (`User`, `Order`).
2. Pass the list of models `[User, Order]` and `db_config` to:
   - `backup_db_to_sqlite(models, db_config, "full_db.db")` to back up all tables to a single SQLite database.
   - `export_to_sql_script(models, db_config, "dump.sql")` to export an SQL script that can reconstruct the DB from scratch.

## Execution

```bash
python example.py
```
