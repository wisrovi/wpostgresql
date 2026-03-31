===============
Bulk Operations
===============

wpostgresql provides efficient bulk operations for inserting, updating, and deleting multiple records.

Insert Many
-----------

Insert multiple records in a single transaction for better performance:

.. code-block:: python

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

    db = WPostgreSQL(Person, db_config)

    persons = [
        Person(id=1, name="Alice", age=25),
        Person(id=2, name="Bob", age=30),
        Person(id=3, name="Charlie", age=35),
        Person(id=4, name="Diana", age=28),
        Person(id=5, name="Eve", age=32),
    ]

    db.insert_many(persons)
    print(f"Inserted {len(persons)} records")
    print("All persons:", db.get_all())

**Output**::

    Inserted 5 records
    All persons: [Person(id=1, name='Alice', age=25), ...]

Large Batch Insert
-------------------

For very large datasets, insert in batches:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    class Product(BaseModel):
        id: int
        name: str
        price: float

    db = WPostgreSQL(Product, db_config)

    # Insert 1000 products in batches of 100
    batch_size = 100
    total_records = 1000

    for batch_num in range(0, total_records, batch_size):
        batch = [
            Product(
                id=i,
                name=f"Product {i}",
                price=round(10.0 + (i * 0.5), 2)
            )
            for i in range(batch_num + 1, min(batch_num + batch_size + 1, total_records + 1))
        ]
        db.insert_many(batch)
        print(f"Inserted batch {batch_num // batch_size + 1}")

    print(f"Total products: {db.count()}")

Update Many
-----------

Update multiple records at once:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    class Person(BaseModel):
        id: int
        name: str
        age: int
        status: str

    db = WPostgreSQL(Person, db_config)

    # Setup test data
    persons = [
        Person(id=i, name=f"Person {i}", age=20 + i, status="active")
        for i in range(1, 6)
    ]
    db.insert_many(persons)

    # Update multiple records
    updates = [
        (Person(id=1, name="Alice Updated", age=26, status="active"), 1),
        (Person(id=2, name="Bob Updated", age=31, status="inactive"), 2),
        (Person(id=3, name="Charlie Updated", age=36, status="active"), 3),
    ]

    count = db.update_many(updates)
    print(f"Updated {count} records")

    for person in db.get_all():
        print(f"  {person.id}: {person.name}, age={person.age}, status={person.status}")

**Output**::

    Updated 3 records
      1: Alice Updated, age=26, status=active
      2: Bob Updated, age=31, status=inactive
      3: Charlie Updated, age=36, status=active
      4: Person 4, age=24, status=active
      5: Person 5, age=25, status=active

Delete Many
-----------

Delete multiple records efficiently:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    class Person(BaseModel):
        id: int
        name: str
        age: int

    db = WPostgreSQL(Person, db_config)

    # Setup test data
    persons = [Person(id=i, name=f"Person {i}", age=20 + i) for i in range(1, 11)]
    db.insert_many(persons)
    print(f"Initial count: {db.count()}")

    # Delete specific IDs
    deleted_count = db.delete_many([1, 3, 5, 7, 9])
    print(f"Deleted {deleted_count} records")
    print(f"Remaining count: {db.count()}")

    # Show remaining records
    remaining = db.get_all()
    print("Remaining IDs:", [p.id for p in remaining])

**Output**::

    Initial count: 10
    Deleted 5 records
    Remaining count: 5
    Remaining IDs: [2, 4, 6, 8, 10]

Async Bulk Operations
-----------------------

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

        # Bulk insert async
        persons = [
            Person(id=i, name=f"Async Person {i}", age=20 + i)
            for i in range(1, 101)
        ]
        await db.insert_many_async(persons)
        print("Inserted 100 records async")

        # Bulk update async
        updates = [
            (Person(id=i, name=f"Updated {i}", age=30 + i), i)
            for i in range(1, 51)
        ]
        count = await db.update_many_async(updates)
        print(f"Updated {count} records async")

        # Bulk delete async
        deleted = await db.delete_many_async(range(51, 101))
        print(f"Deleted {deleted} records async")

        remaining = await db.count_async()
        print(f"Remaining: {remaining} records")

    asyncio.run(main())

**Output**::

    Inserted 100 records async
    Updated 50 records async
    Deleted 50 records async
    Remaining: 50 records

Bulk with Transactions
-----------------------

Combine bulk operations in a transaction:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    class Order(BaseModel):
        id: int
        customer_id: int
        total: float

    class OrderItem(BaseModel):
        id: int
        order_id: int
        product: str
        quantity: int

    def bulk_create_order(db: WPostgreSQL, order: Order, items: list[OrderItem]):
        """Create order with items in a single transaction."""
        operations = [
            ("INSERT INTO order_table (id, customer_id, total) VALUES (%s, %s, %s)",
             (order.id, order.customer_id, order.total))
        ]

        for item in items:
            operations.append(
                ("INSERT INTO order_item (id, order_id, product, quantity) VALUES (%s, %s, %s, %s)",
                 (item.id, item.order_id, item.product, item.quantity))
            )

        return db.execute_transaction(operations)

    # Usage
    db = WPostgreSQL(Order, db_config)

    order = Order(id=1, customer_id=100, total=250.00)
    items = [
        OrderItem(id=1, order_id=1, product="Widget A", quantity=5),
        OrderItem(id=2, order_id=1, product="Widget B", quantity=3),
        OrderItem(id=3, order_id=1, product="Widget C", quantity=2),
    ]

    bulk_create_order(db, order, items)
    print("Order with items created successfully")