==================
Async Operations
==================

wpostgresql provides full async support for all database operations, enabling non-blocking I/O for high-performance applications.

Basic Async Operations
-----------------------

Initialize and perform async CRUD operations:

.. code-block:: python

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

        # Insert
        await db.insert_async(Person(id=1, name="Alice", age=25))
        await db.insert_async(Person(id=2, name="Bob", age=30))

        # Read
        all_people = await db.get_all_async()
        print("All people:", all_people)

        # Filter
        alice = await db.get_by_field_async(name="Alice")
        print("Found Alice:", alice)

        # Update
        await db.update_async(1, Person(id=1, name="Alice Updated", age=26))

        # Delete
        await db.delete_async(2)

        remaining = await db.get_all_async()
        print("Remaining:", remaining)

    asyncio.run(main())

**Output**::

    All people: [Person(id=1, name='Alice', age=25), Person(id=2, name='Bob', age=30)]
    Found Alice: [Person(id=1, name='Alice', age=25)]
    Remaining: [Person(id=1, name='Alice Updated', age=26)]

Async Pagination
-----------------

Retrieve paginated results asynchronously:

.. code-block:: python

    import asyncio
    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    class Person(BaseModel):
        id: int
        name: str
        age: int

    async def main():
        db = WPostgreSQL(Person, db_config)

        # Get page 1 with 10 items per page
        page1 = await db.get_page_async(page=1, per_page=10)
        print("Page 1:", page1)

        # Get page 2
        page2 = await db.get_page_async(page=2, per_page=10)
        print("Page 2:", page2)

        # Get with limit and offset
        paginated = await db.get_paginated_async(limit=5, offset=10)
        print("Paginated:", paginated)

        # With ordering
        ordered = await db.get_paginated_async(
            limit=10,
            offset=0,
            order_by="name",
            order_desc=False
        )
        print("Ordered by name:", ordered)

    asyncio.run(main())

Async Bulk Operations
---------------------

Perform bulk operations asynchronously:

.. code-block:: python

    import asyncio
    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    class Person(BaseModel):
        id: int
        name: str
        age: int

    async def main():
        db = WPostgreSQL(Person, db_config)

        # Bulk insert
        persons = [
            Person(id=i, name=f"Person {i}", age=20 + i)
            for i in range(1, 11)
        ]
        await db.insert_many_async(persons)
        print("Inserted 10 records")

        # Bulk update
        updates = [
            (Person(id=i, name=f"Updated Person {i}", age=30 + i), i)
            for i in range(1, 6)
        ]
        count = await db.update_many_async(updates)
        print(f"Updated {count} records")

        # Bulk delete
        deleted = await db.delete_many_async([6, 7, 8, 9, 10])
        print(f"Deleted {deleted} records")

        remaining = await db.get_all_async()
        print(f"Remaining: {len(remaining)} records")

    asyncio.run(main())

Async Count
-----------

Count records asynchronously:

.. code-block:: python

    import asyncio
    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    class Person(BaseModel):
        id: int
        name: str
        age: int

    async def main():
        db = WPostgreSQL(Person, db_config)

        total = await db.count_async()
        print(f"Total records: {total}")

    asyncio.run(main())

Async Transactions
------------------

Execute async transactions:

.. code-block:: python

    import asyncio
    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    class Account(BaseModel):
        id: int
        name: str
        balance: float

    async def main():
        db = WPostgreSQL(Account, db_config)

        # Setup initial data
        await db.insert_async(Account(id=1, name="Alice", balance=1000))
        await db.insert_async(Account(id=2, name="Bob", balance=500))

        # Execute transaction
        operations = [
            ("UPDATE account SET balance = balance - 100 WHERE id = 1", ()),
            ("UPDATE account SET balance = balance + 100 WHERE id = 2", ()),
        ]

        results = await db.execute_transaction_async(operations)
        print("Transaction completed")

        # Check final balances
        alice = await db.get_by_field_async(id=1)
        bob = await db.get_by_field_async(id=2)
        print(f"Alice: {alice[0].balance}, Bob: {bob[0].balance}")

    asyncio.run(main())

FastAPI Integration
-------------------

Use with FastAPI for async web applications:

.. code-block:: python

    from fastapi import FastAPI
    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL
    import asyncio

    app = FastAPI()

    db_config = {
        "dbname": "wpostgresql",
        "user": "postgres",
        "password": "postgres",
    }

    class Item(BaseModel):
        id: int
        name: str
        price: float

    db = WPostgreSQL(Item, db_config)

    @app.post("/items/")
    async def create_item(item: Item):
        await db.insert_async(item)
        return item

    @app.get("/items/")
    async def get_items():
        return await db.get_all_async()

    @app.get("/items/{item_id}")
    async def get_item(item_id: int):
        items = await db.get_by_field_async(id=item_id)
        if not items:
            return {"error": "Item not found"}
        return items[0]

    @app.put("/items/{item_id}")
    async def update_item(item_id: int, item: Item):
        await db.update_async(item_id, item)
        return item

    @app.delete("/items/{item_id}")
    async def delete_item(item_id: int):
        await db.delete_async(item_id)
        return {"message": "Deleted"}