"""Main repository class for PostgreSQL operations."""

from typing import Any

from pydantic import BaseModel

from wpostgresql.core.connection import get_connection
from wpostgresql.core.sync import TableSync


class WPostgreSQL:
    """PostgreSQL repository using Pydantic models.

    Provides a simple interface for CRUD operations on PostgreSQL tables,
    with automatic table creation and schema synchronization.

    Example:
        from pydantic import BaseModel
        from wpostgresql import WPostgreSQL

        class User(BaseModel):
            id: int
            name: str
            email: str

        db = WPostgreSQL(User, db_config)
        db.insert(User(id=1, name="John", email="john@example.com"))
    """

    def __init__(self, model: type[BaseModel], db_config: dict):
        """Initialize the repository with a Pydantic model.

        Args:
            model: Pydantic BaseModel class defining the table schema.
            db_config: PostgreSQL connection configuration dictionary.
                Expected keys: dbname, user, password, host, port.
        """
        self.model = model
        self.db_config = db_config
        self.table_name = model.__name__.lower()
        self._sync = TableSync(model, db_config)

        self._sync.create_if_not_exists()
        self._sync.sync_with_model()

    def insert(self, data: BaseModel) -> None:
        """Insert a new record into the database.

        Args:
            data: Pydantic model instance to insert.

        Raises:
            psycopg2.errors.UniqueViolation: If unique constraint is violated.
            psycopg2.errors.ForeignKeyViolation: If foreign key constraint is violated.
        """
        data_dict = data.model_dump()
        fields = ", ".join(data_dict.keys())
        placeholders = ", ".join(["%s"] * len(data_dict))
        values = tuple(data_dict.values())

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
            conn.commit()

    def get_all(self) -> list[BaseModel]:
        """Get all records from the table.

        Returns:
            List of Pydantic model instances.
        """
        query = f"SELECT * FROM {self.table_name}"
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    def get_by_field(self, **filters) -> list[BaseModel]:
        """Get records filtered by specified fields.

        Args:
            **filters: Field name/value pairs to filter by.

        Returns:
            List of matching Pydantic model instances.
        """
        if not filters:
            return self.get_all()

        conditions = " AND ".join(f"{key} = %s" for key in filters)
        values = tuple(filters.values())
        query = f"SELECT * FROM {self.table_name} WHERE {conditions}"

        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, values)
            rows = cursor.fetchall()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    def update(self, record_id: int, data: BaseModel) -> None:
        """Update a record in the database.

        Args:
            record_id: ID of the record to update.
            data: Pydantic model instance with updated values.
        """
        data_dict = data.model_dump()
        fields = ", ".join(f"{key} = %s" for key in data_dict.keys())
        values = tuple(data_dict.values()) + (record_id,)
        query = f"UPDATE {self.table_name} SET {fields} WHERE id = %s"

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
            conn.commit()

    def delete(self, record_id: int) -> None:
        """Delete a record from the database.

        Args:
            record_id: ID of the record to delete.
        """
        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (record_id,))
            conn.commit()

    def _default_value(self, field: str) -> Any:
        """Get default value for a field when database value is NULL.

        Args:
            field: Field name.

        Returns:
            Default value based on field type: "" for str, 0 for int,
            False for bool, None for other types.
        """
        field_type = self.model.model_fields[field].annotation
        if field_type is str:
            return ""
        elif field_type is int:
            return 0
        elif field_type is bool:
            return False
        return None
