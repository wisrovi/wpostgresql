============
Pagination
============

wpostgresql provides flexible pagination options for retrieving large datasets.

Limit and Offset
-----------------

Basic pagination using limit and offset:

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

    # Insert test data
    for i in range(1, 21):
        db.insert(Person(id=i, name=f"Person {i}", age=20 + (i % 10)))

    # Get first 10 records
    first_10 = db.get_paginated(limit=10, offset=0)
    print(f"First 10: {[p.name for p in first_10]}")

    # Get next 10 records
    next_10 = db.get_paginated(limit=10, offset=10)
    print(f"Next 10: {[p.name for p in next_10]}")

    # Get records 5-15 (offset 4, limit 10)
    middle = db.get_paginated(limit=10, offset=4)
    print(f"Middle: {[p.name for p in middle]}")

**Output**::

    First 10: ['Person 1', 'Person 2', ..., 'Person 10']
    Next 10: ['Person 11', 'Person 12', ..., 'Person 20']
    Middle: ['Person 5', 'Person 6', ..., 'Person 14']

By Page Number
--------------

Use page-based pagination for easier usage:

.. code-block:: python

    # Get page 1 (first 20 items per page)
    page1 = db.get_page(page=1, per_page=20)
    print(f"Page 1: {len(page1)} items")

    # Get page 2
    page2 = db.get_page(page=2, per_page=20)
    print(f"Page 2: {len(page2)} items")

    # Page 3 (empty if only 20 records)
    page3 = db.get_page(page=3, per_page=20)
    print(f"Page 3: {len(page3)} items")

With Ordering
-------------

Sort results before pagination:

.. code-block:: python

    # Order by name ascending (A-Z)
    ordered_asc = db.get_paginated(
        limit=5,
        offset=0,
        order_by="name",
        order_desc=False
    )
    print("Ascending by name:", [p.name for p in ordered_asc])

    # Order by age descending (oldest first)
    ordered_desc = db.get_paginated(
        limit=5,
        offset=0,
        order_by="age",
        order_desc=True
    )
    print("Descending by age:", [(p.name, p.age) for p in ordered_desc])

    # Order by multiple fields
    multi_ordered = db.get_paginated(
        limit=5,
        offset=0,
        order_by="age",
        order_desc=True
    )
    # Results first sorted by age desc, then by name for same age

Count Total Records
-------------------

Get the total count for pagination UI:

.. code-block:: python

    total = db.count()
    print(f"Total records in table: {total}")

    # Calculate total pages
    per_page = 10
    total_pages = (total + per_page - 1) // per_page
    print(f"Total pages: {total_pages}")

    # Example: Display pagination info
    current_page = 1
    print(f"Showing page {current_page} of {total_pages} ({total} total)")

Async Pagination
----------------

Asynchronous pagination for async applications:

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

        # Async page retrieval
        page1 = await db.get_page_async(page=1, per_page=10)
        page2 = await db.get_page_async(page=2, per_page=10)

        # Async paginated with offset
        results = await db.get_paginated_async(
            limit=5,
            offset=10,
            order_by="name"
        )

        # Async count
        total = await db.count_async()
        print(f"Total async count: {total}")

    asyncio.run(main())

Complete Pagination Example
----------------------------

Full example with navigation controls:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    class Product(BaseModel):
        id: int
        name: str
        price: float
        category: str

    db = WPostgreSQL(Product, db_config)

    def get_page_with_info(db: WPostgreSQL, page: int, per_page: int):
        """Get paginated results with metadata."""
        total = db.count()
        total_pages = (total + per_page - 1) // per_page

        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages

        offset = (page - 1) * per_page
        items = db.get_paginated(
            limit=per_page,
            offset=offset,
            order_by="id"
        )

        return {
            "items": items,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    # Usage
    result = get_page_with_info(db, page=1, per_page=10)
    print(f"Page {result['page']} of {result['total_pages']}")
    print(f"Total items: {result['total']}")
    print(f"Has next: {result['has_next']}, Has prev: {result['has_prev']}")
    print("Items:", result["items"])