import asyncio

from pydantic import BaseModel

from wpostgresql import WPostgreSQLAsync

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


asyncio.run(main())
