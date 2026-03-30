"""Main repository class for PostgreSQL operations."""

import logging
from typing import Any, Callable, Optional

from pydantic import BaseModel

from wpostgresql.core.connection import Transaction, get_connection, get_transaction
from wpostgresql.core.sync import TableSync
from wpostgresql.exceptions import SQLInjectionError, TransactionError

logger = logging.getLogger(__name__)


def validate_identifier(identifier: str) -> None:
    """Validate SQL identifier to prevent SQL injection.

    Args:
        identifier: Table or column name to validate.

    Raises:
        SQLInjectionError: If identifier contains invalid characters.
    """
    import re

    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
        raise SQLInjectionError(f"Invalid identifier: {identifier}")


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

    def get_paginated(
        self,
        limit: int = 10,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_desc: bool = False,
    ) -> list[BaseModel]:
        """Get records with pagination.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            order_by: Field name to order by.
            order_desc: If True, order descending.

        Returns:
            List of Pydantic model instances.
        """
        validate_identifier(self.table_name)
        if order_by:
            validate_identifier(order_by)
            order_clause = f" ORDER BY {order_by} {'DESC' if order_desc else 'ASC'}"
        else:
            order_clause = ""

        query = f"SELECT * FROM {self.table_name}{order_clause} LIMIT %s OFFSET %s"

        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, (limit, offset))
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

    def get_page(self, page: int = 1, per_page: int = 10) -> list[BaseModel]:
        """Get records by page number.

        Args:
            page: Page number (1-indexed).
            per_page: Number of records per page.

        Returns:
            List of Pydantic model instances.
        """
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10
        offset = (page - 1) * per_page
        return self.get_paginated(limit=per_page, offset=offset)

    def count(self) -> int:
        """Get total number of records in the table.

        Returns:
            Total count of records.
        """
        validate_identifier(self.table_name)
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
        return result[0] if result else 0

    def insert_many(self, data_list: list[BaseModel]) -> None:
        """Insert multiple records in a single transaction.

        Args:
            data_list: List of Pydantic model instances to insert.

        Raises:
            psycopg2.errors.UniqueViolation: If unique constraint is violated.
        """
        if not data_list:
            return

        data_dicts = [data.model_dump() for data in data_list]
        fields = ", ".join(data_dicts[0].keys())
        placeholders = ", ".join(["%s"] * len(data_dicts[0]))

        values = []
        for data_dict in data_dicts:
            values.extend(data_dict.values())

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                for data_dict in data_dicts:
                    values = tuple(data_dict.values())
                    cursor.execute(query, values)
            conn.commit()

    def update_many(self, updates: list[tuple[BaseModel, int]]) -> int:
        """Update multiple records.

        Args:
            updates: List of tuples (data, record_id) to update.

        Returns:
            Number of records updated.
        """
        if not updates:
            return 0

        validate_identifier(self.table_name)
        total_updated = 0

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                for data, record_id in updates:
                    data_dict = data.model_dump()
                    fields = ", ".join(f"{key} = %s" for key in data_dict.keys())
                    values = tuple(data_dict.values()) + (record_id,)
                    query = f"UPDATE {self.table_name} SET {fields} WHERE id = %s"
                    cursor.execute(query, values)
                    total_updated += cursor.rowcount
            conn.commit()

        return total_updated

    def delete_many(self, record_ids: list[int]) -> int:
        """Delete multiple records by their IDs.

        Args:
            record_ids: List of record IDs to delete.

        Returns:
            Number of records deleted.
        """
        if not record_ids:
            return 0

        validate_identifier(self.table_name)

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                for record_id in record_ids:
                    query = f"DELETE FROM {self.table_name} WHERE id = %s"
                    cursor.execute(query, (record_id,))
            conn.commit()

        return len(record_ids)

    def execute_transaction(self, operations: list[tuple[str, tuple]]) -> list[Any]:
        """Execute multiple operations in a transaction.

        Args:
            operations: List of tuples (query, values) to execute.

        Returns:
            List of results from each operation.

        Raises:
            TransactionError: If transaction fails.
        """
        results = []
        try:
            with get_transaction(self.db_config) as txn:
                for query, values in operations:
                    result = txn.execute(query, values)
                    if result is not None:
                        results.append(result)
                txn.commit()
                logger.info(f"Transaction completed with {len(operations)} operations")
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise TransactionError(f"Transaction failed: {e}") from e
        return results

    def with_transaction(self, func: Callable[[Transaction], Any]) -> Any:
        """Execute a function within a transaction.

        Args:
            func: Function that receives a Transaction and returns a result.

        Returns:
            Result from the function.

        Raises:
            TransactionError: If transaction fails.
        """
        try:
            with get_transaction(self.db_config) as txn:
                result = func(txn)
                txn.commit()
                logger.info("Transaction completed successfully")
                return result
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise TransactionError(f"Transaction failed: {e}") from e
