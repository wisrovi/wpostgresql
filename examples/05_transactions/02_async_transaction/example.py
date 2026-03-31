"""Async transaction example."""

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
    balance: float


async def main():
    db = WPostgreSQL(Person, db_config)

    await db.insert_async(Person(id=1, name="Alice", balance=1000))
    await db.insert_async(Person(id=2, name="Bob", balance=500))

    try:
        result = await db.execute_transaction_async(
            [
                ("UPDATE person SET balance = balance - 100 WHERE id = 1", None),
                ("UPDATE person SET balance = balance + 100 WHERE id = 2", None),
            ]
        )
        print("Transacción exitosa")
    except Exception as e:
        print("Transacción fallida:", e)

    alice = await db.get_by_field_async(id=1)
    bob = await db.get_by_field_async(id=2)
    print("Saldo final Alice:", alice[0].balance)
    print("Saldo final Bob:", bob[0].balance)


if __name__ == "__main__":
    asyncio.run(main())
