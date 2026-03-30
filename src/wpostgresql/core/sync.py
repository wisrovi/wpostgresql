"""Table synchronization with Pydantic models."""

from typing import Optional

from wpostgresql.core.connection import get_connection
from wpostgresql.types.sql_types import get_sql_type


class TableSync:
    """Handles table synchronization between Pydantic models and PostgreSQL."""

    def __init__(self, model, db_config: dict):
        """Initialize table sync.

        Args:
            model: Pydantic BaseModel class.
            db_config: PostgreSQL connection configuration.
        """
        self.model = model
        self.db_config = db_config
        self.table_name = model.__name__.lower()

    def create_if_not_exists(self):
        """Create the table if it doesn't exist."""
        fields = ", ".join(
            f"{field} {get_sql_type(typ)}" for field, typ in self.model.model_fields.items()
        )
        query = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({fields})"
        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
            conn.commit()

    def sync_with_model(self):
        """Sync the table with the Pydantic model, adding new columns if necessary."""
        query = "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, (self.table_name,))
            rows = cursor.fetchall()
            existing_columns = {row[0] for row in rows}

        model_fields = set(self.model.model_fields.keys())
        new_fields = model_fields - existing_columns

        if new_fields:
            with get_connection(self.db_config) as conn:
                with conn.cursor() as cursor:
                    for field in new_fields:
                        field_type = get_sql_type(self.model.model_fields[field])
                        alter_query = f"ALTER TABLE {self.table_name} ADD COLUMN {field} {field_type} DEFAULT NULL"
                        cursor.execute(alter_query)
                conn.commit()

    def table_exists(self) -> bool:
        """Check if the table exists in the database.

        Returns:
            True if the table exists, False otherwise.
        """
        query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)"
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, (self.table_name,))
            return cursor.fetchone()[0]

    def drop_table(self):
        """Drop the table from the database."""
        query = f"DROP TABLE IF EXISTS {self.table_name}"
        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
            conn.commit()

    def get_columns(self) -> list[str]:
        """Get list of column names in the table.

        Returns:
            List of column names.
        """
        query = (
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = %s ORDER BY ordinal_position"
        )
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, (self.table_name,))
            return [row[0] for row in cursor.fetchall()]

    def create_index(
        self, columns: list[str], index_name: Optional[str] = None, unique: bool = False
    ):
        """Create an index on the specified columns.

        Args:
            columns: List of column names to index.
            index_name: Name for the index. If None, auto-generated.
            unique: Whether to create a unique index.
        """
        if index_name is None:
            index_name = f"idx_{self.table_name}_{'_'.join(columns)}"

        columns_str = ", ".join(columns)
        unique_str = "UNIQUE " if unique else ""
        query = f"CREATE {unique_str}INDEX IF NOT EXISTS {index_name} ON {self.table_name} ({columns_str})"

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
            conn.commit()

    def drop_index(self, index_name: str):
        """Drop an index from the table.

        Args:
            index_name: Name of the index to drop.
        """
        query = f"DROP INDEX IF EXISTS {index_name}"
        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
            conn.commit()

    def get_indexes(self) -> list[dict]:
        """Get list of indexes on the table.

        Returns:
            List of dictionaries with index information.
        """
        query = "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = %s"
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, (self.table_name,))
            return [{"name": row[0], "definition": row[1]} for row in cursor.fetchall()]
