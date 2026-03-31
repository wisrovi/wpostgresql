"""Async pagination example using page number."""

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

    for i in range(1, 21):
        await db.insert_async(Person(id=i, name=f"Person {i}", age=20 + i))

    print("Primera pagina:", await db.get_page_async(page=1, per_page=5))
    print("Segunda pagina:", await db.get_page_async(page=2, per_page=5))
    print("Total registros:", await db.count_async())


if __name__ == "__main__":
    asyncio.run(main())
