=============
Transactions
=============

Transactions ensure data integrity by grouping multiple operations into a single atomic unit.

Basic Transaction
------------------

Execute multiple operations in a single transaction:

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
        balance: float

    db = WPostgreSQL(Person, db_config)

    # Setup initial data
    db.insert(Person(id=1, name="Alice", balance=1000))
    db.insert(Person(id=2, name="Bob", balance=500))

    # Execute a transaction: transfer 100 from Alice to Bob
    try:
        result = db.execute_transaction([
            ("UPDATE person SET balance = balance - 100 WHERE id = 1", None),
            ("UPDATE person SET balance = balance + 100 WHERE id = 2", None),
        ])
        print("Transaction successful")
    except Exception as e:
        print(f"Transaction failed: {e}")

    # Verify the transfer
    alice = db.get_by_field(id=1)[0]
    bob = db.get_by_field(id=2)[0]
    print(f"Alice balance: {alice.balance}")
    print(f"Bob balance: {bob.balance}")

**Output**::

    Transaction successful
    Alice balance: 900.0
    Bob balance: 600.0

Transaction Context Manager
----------------------------

Use ``with_transaction()`` for more complex operations:

.. code-block:: python

    from wpostgresql import WPostgreSQL, Transaction

    class Account(BaseModel):
        id: int
        name: str
        balance: float

    def transfer_funds(db: WPostgreSQL, from_id: int, to_id: int, amount: float):
        """Transfer funds between accounts using a transaction context manager."""
        def execute_transfer(txn: Transaction):
            # Deduct from source
            txn.execute(
                "UPDATE account SET balance = balance - %s WHERE id = %s",
                (amount, from_id)
            )
            # Add to destination
            txn.execute(
                "UPDATE account SET balance = balance + %s WHERE id = %s",
                (amount, to_id)
            )
            # Log the transaction
            txn.execute(
                "INSERT INTO transaction_log (from_id, to_id, amount) VALUES (%s, %s, %s)",
                (from_id, to_id, amount)
            )

        return db.with_transaction(execute_transfer)

    # Usage
    db = WPostgreSQL(Account, db_config)
    db.insert(Account(id=1, name="Checking", balance=1000))
    db.insert(Account(id=2, name="Savings", balance=500))

    transfer_funds(db, from_id=1, to_id=2, amount=250)

    print("Transfer complete")
    print(f"Checking: {db.get_by_field(id=1)[0].balance}")
    print(f"Savings: {db.get_by_field(id=2)[0].balance}")

**Output**::

    Transfer complete
    Checking: 750.0
    Savings: 750.0

Transaction with Multiple Inserts
-----------------------------------

Insert multiple related records atomically:

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
        product_name: str
        quantity: int
        price: float

    def create_order_with_items(db: WPostgreSQL, order: Order, items: list[OrderItem]):
        """Create an order with multiple items in a transaction."""
        operations = [
            ("INSERT INTO order_table (id, customer_id, total) VALUES (%s, %s, %s)",
             (order.id, order.customer_id, order.total))
        ]

        for item in items:
            operations.append(
                ("INSERT INTO order_item (id, order_id, product_name, quantity, price) VALUES (%s, %s, %s, %s, %s)",
                 (item.id, item.order_id, item.product_name, item.quantity, item.price))
            )

        return db.execute_transaction(operations)

    # Usage
    db = WPostgreSQL(Order, db_config)

    order = Order(id=1, customer_id=100, total=150.00)
    items = [
        OrderItem(id=1, order_id=1, product_name="Widget A", quantity=2, price=25.00),
        OrderItem(id=2, order_id=1, product_name="Widget B", quantity=1, price=100.00),
    ]

    create_order_with_items(db, order, items)
    print("Order created with items")

Async Transactions
------------------

.. code-block:: python

    import asyncio
    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    class Account(BaseModel):
        id: int
        name: str
        balance: float

    async def async_transfer(db: WPostgreSQL, from_id: int, to_id: int, amount: float):
        """Transfer funds asynchronously."""
        operations = [
            ("UPDATE account SET balance = balance - %s WHERE id = %s", (amount, from_id)),
            ("UPDATE account SET balance = balance + %s WHERE id = %s", (amount, to_id)),
        ]

        await db.execute_transaction_async(operations)

    async def main():
        db = WPostgreSQL(Account, db_config)

        db.insert(Account(id=1, name="Checking", balance=1000))
        db.insert(Account(id=2, name="Savings", balance=500))

        await async_transfer(db, from_id=1, to_id=2, amount=300)

        print(f"Checking: {db.get_by_field(id=1)[0].balance}")
        print(f"Savings: {db.get_by_field(id=2)[0].balance}")

    asyncio.run(main())

**Output**::

    Checking: 700.0
    Savings: 800.0

Transaction with Rollback
--------------------------

If any operation fails, all changes are automatically rolled back:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    class Person(BaseModel):
        id: int
        name: str
        age: int

    db = WPostgreSQL(Person, db_config)

    # Initial data
    db.insert(Person(id=1, name="Test", age=25))

    try:
        # This transaction will fail on the second operation
        operations = [
            ("UPDATE person SET age = 30 WHERE id = 1", ()),
            ("INSERT INTO nonexistent_table VALUES (1)", ()),  # This will fail
        ]
        db.execute_transaction(operations)
    except Exception as e:
        print(f"Transaction rolled back: {e}")

    # Verify that the first update was rolled back
    person = db.get_by_field(id=1)[0]
    print(f"Person age after rollback: {person.age}")

**Output**::

    Transaction rolled back: ...
    Person age after rollback: 25