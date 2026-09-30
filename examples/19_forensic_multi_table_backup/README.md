# Example 19: Multi-Table Forensic Audit & SQLite Backup

This example demonstrates enterprise multi-table database management in `wpostgresql` with global forensic audit tracking enabled and a complete export to SQLite.

## Key Concepts Demonstrated

1. **Pydantic Inheritance (`BaseModel`)**: Models inherit directly from `pydantic.BaseModel` without requiring explicit base classes.
2. **Forensic Mode (`forensic=True`)**: Enabled centrally during `WPostgreSQL` initialization for all managed models.
3. **Table Relationships**: `Customer` -> `Invoice` -> `InvoiceItem` linked via foreign key field references (`customer_id`, `invoice_id`).
4. **No Raw SQL / `get_connection`**: All CRUD, filtering, soft-delete, and audit-tracking operations are handled natively by the repository API (`db[Model]` or `db.table_name`).
5. **Multi-Table SQLite Backup**: Uses `backup_db_to_sqlite` to export all managed PostgreSQL tables directly into a single SQLite database file.

## Key Technologies & Ecosystem Libraries

- **Python 3.10+**: Core programming language.
- **Pydantic v2**: Schema definition, validation, and data modeling.
- **WPostgreSQL**: Type-safe PostgreSQL ORM with automatic schema synchronization, connection pooling, multi-table repository management, and forensic audit logging.
- **WSQLite**: High-performance SQLite engine used internally for seamless PostgreSQL-to-SQLite database backups.
- **Psycopg 3 / psycopg_pool**: Underlying PostgreSQL driver and connection pooling.

## How to Run

Make sure PostgreSQL is running and your connection configuration in `example.py` is updated:

```bash
python examples/19_forensic_multi_table_backup/example.py
```
