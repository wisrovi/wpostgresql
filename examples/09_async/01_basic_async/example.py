"""Async PostgreSQL operations with wpostgresql."""

import asyncio

from pydantic import BaseModel

from wpostgresql import WPostgreSQL


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
    db = WPostgreSQL(Person, db_config)

    await db.insert_async(Person(id=1, name="Alice", age=25))
    await db.insert_async(Person(id=2, name="Bob", age=30))

    users = await db.get_all_async()
    print("Usuarios:", users)

    await db.update_async(1, Person(id=1, name="Alice", age=26))

    await db.delete_async(2)

    users_after_delete = await db.get_all_async()
    print("Usuarios despues de eliminar:", users_after_delete)


asyncio.run(main())
