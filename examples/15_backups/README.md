# 15_backups

Examples demonstrating backup and export features in WPostgreSQL.

## Key Technologies & Libraries

- **WPostgreSQL**: PostgreSQL ORM leveraging Pydantic models.
- **wsqlite**: Lightweight SQLite ORM leveraging Pydantic models.
- **Pydantic v2**: Data validation and schema definitions.

## Subdirectories

- **01_sqlite_backup**: Export a single PostgreSQL table directly to an SQLite database file using `wsqlite`.
- **02_full_db_backup**: Export multiple PostgreSQL tables (entire database) to a single SQLite database file and generate standalone `.sql` reconstruction scripts.
