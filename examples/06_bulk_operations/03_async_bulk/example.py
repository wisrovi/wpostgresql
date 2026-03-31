"""Async bulk operations example."""

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

    users = [
        Person(id=1, name="Alice", age=25),
        Person(id=2, name="Bob", age=30),
        Person(id=3, name="Charlie", age=35),
        Person(id=4, name="Diana", age=28),
        Person(id=5, name="Eve", age=32),
    ]

    await db.insert_many_async(users)
    print("Insertados:", len(await db.get_all_async()))

    await db.update_many_async(
        [
            (Person(id=1, name="Alice", age=26), 1),
            (Person(id=2, name="Bob", age=31), 2),
        ]
    )
    print("Actualizados")

    await db.delete_many_async([4, 5])
    print("Restantes:", await db.count_async())


if __name__ == "__main__":
    asyncio.run(main())
