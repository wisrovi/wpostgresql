# Example 16: Forensic Audit Fields & Soft Delete

This example directory demonstrates how to use `ForensicModel` and `forensic=True` in `wpostgresql` to automatically track user actions and timestamps across database records without manually managing audit columns.

## Key Features
- **Automatic Audit Metadata**: Tracks `create_by`, `create_in`, `update_by`, `update_in`, `delete_by`, `delete_in`.
- **Soft Delete (`status=99`)**: `db.delete(id)` marks records as status 99 instead of deleting them physically.
- **Default Filtering**: Read queries automatically filter out soft-deleted records (`WHERE status != 99`) unless `include_deleted=True` is supplied.
- **Flexible Activation**: Disabled by default (`forensic=False`) for standard Pydantic models, activated automatically by inheriting from `ForensicModel` or passing `forensic=True`.

## Relevant Technologies & Key Libraries
- **Python 3.9+**: High-performance type hints and datetime timezone support.
- **Pydantic v2**: Data validation and type-safe schema definitions.
- **psycopg 3**: Modern PostgreSQL database driver for Python.
- **wpostgresql**: Type-safe PostgreSQL ORM with automatic schema synchronization.

## How to Run Examples
Make sure a PostgreSQL database server is running on localhost:5432 and execute:

```bash
python 01_standard_vs_forensic.py
python 02_forensic_crud.py
```
