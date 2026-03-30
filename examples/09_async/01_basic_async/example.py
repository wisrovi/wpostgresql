import asyncio
from typing import Optional
from contextlib import asynccontextmanager

from pydantic import BaseModel
import psycopg2
from psycopg2 import pool
import psycopg2.extras


class WPostgreSQLAsync:
    """Async PostgreSQL repository using Pydantic models."""

    def __init__(self, model: type[BaseModel], db_config: dict):
        self.model = model
        self.db_config = db_config
        self.table_name = model.__name__.lower()
        self._pool = pool.ThreadedConnectionPool(1, 10, **db_config)

    @asynccontextmanager
    async def _get_connection(self):
        conn = self._pool.getconn()
        try:
            yield conn
        finally:
            self._pool.putconn(conn)

    async def insert(self, data: BaseModel) -> None:
        data_dict = data.model_dump()
        fields = ", ".join(data_dict.keys())
        placeholders = ", ".join(["%s"] * len(data_dict))
        values = tuple(data_dict.values())

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"

        async with self._get_connection() as conn:
            with conn.cursor() as cursor:
                await asyncio.to_thread(cursor.execute, query, values)
            conn.commit()

    async def get_all(self) -> list[BaseModel]:
        query = f"SELECT * FROM {self.table_name}"

        async with self._get_connection() as conn:
            with conn.cursor() as cursor:
                await asyncio.to_thread(cursor.execute, query)
                rows = await asyncio.to_thread(cursor.fetchall)

        return [self.model(**dict(zip(self.model.model_fields.keys(), row))) for row in rows]

    async def update(self, record_id: int, data: BaseModel) -> None:
        data_dict = data.model_dump()
        fields = ", ".join(f"{key} = %s" for key in data_dict.keys())
        values = tuple(data_dict.values()) + (record_id,)
        query = f"UPDATE {self.table_name} SET {fields} WHERE id = %s"

        async with self._get_connection() as conn:
            with conn.cursor() as cursor:
                await asyncio.to_thread(cursor.execute, query, values)
            conn.commit()

    async def delete(self, record_id: int) -> None:
        query = f"DELETE FROM {self.table_name} WHERE id = %s"

        async with self._get_connection() as conn:
            with conn.cursor() as cursor:
                await asyncio.to_thread(cursor.execute, query, (record_id,))
            conn.commit()

    def close(self):
        self._pool.closeall()


db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class Person(BaseModel):
    id: int
    name: str
    age: int


async def main():
    db = WPostgreSQLAsync(Person, db_config)

    await db.insert(Person(id=1, name="Alice", age=25))
    await db.insert(Person(id=2, name="Bob", age=30))

    users = await db.get_all()
    print("Usuarios:", users)

    await db.update(1, Person(id=1, name="Alice", age=26))

    await db.delete(2)

    db.close()


asyncio.run(main())
