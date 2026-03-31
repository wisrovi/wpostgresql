================
CRUD Operations
================

Create (Insert)
----------------

Insert a single record into the database:

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
        is_active: bool

    db = WPostgreSQL(Person, db_config)

    db.insert(Person(id=1, name="John Doe", age=30, is_active=True))
    db.insert(Person(id=2, name="Jane Smith", age=25, is_active=True))

    print("Created users:", db.get_all())

**Output**::

    Created users: [Person(id=1, name='John Doe', age=30, is_active=True), Person(id=2, name='Jane Smith', age=25, is_active=True)]

Insert Multiple Records
------------------------

Use ``insert_many()`` for efficient bulk insertion:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    db_config = {
        "dbname": "wpostgresql",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
    }

    class Person(BaseModel):
        id: int
        name: str
        age: int
        is_active: bool

    db = WPostgreSQL(Person, db_config)

    persons = [
        Person(id=1, name="John", age=30, is_active=True),
        Person(id=2, name="Jane", age=25, is_active=True),
        Person(id=3, name="Bob", age=35, is_active=False),
        Person(id=4, name="Alice", age=28, is_active=True),
    ]

    db.insert_many(persons)
    print(f"Inserted {len(persons)} records")

Read
-----

Get all records from the table:

.. code-block:: python

    all_people = db.get_all()
    for person in all_people:
        print(f"{person.id}: {person.name}")

Get records filtered by specific fields:

.. code-block:: python

    active_people = db.get_by_field(is_active=True)
    print("Active users:", active_people)

    people_named_john = db.get_by_field(name="John")
    print("Users named John:", people_named_john)

    # Multiple filters
    young_active = db.get_by_field(age=25, is_active=True)
    print("Young active users:", young_active)

Update
------

Update a record by ID:

.. code-block:: python

    updated_person = Person(id=1, name="John Updated", age=31, is_active=False)
    db.update(1, updated_person)

    print("Updated record:", db.get_by_field(id=1))

Update multiple records at once:

.. code-block:: python

    updates = [
        (Person(id=1, name="John Doe", age=30), 1),
        (Person(id=2, name="Jane Doe", age=26), 2),
    ]

    count = db.update_many(updates)
    print(f"Updated {count} records")

Delete
------

Delete a single record by ID:

.. code-block:: python

    db.delete(1)
    print("Deleted record with ID 1")

Delete multiple records:

.. code-block:: python

    deleted_count = db.delete_many([1, 2, 3])
    print(f"Deleted {deleted_count} records")

Advanced Queries
-----------------

Using Pydantic Field validation:

.. code-block:: python

    from pydantic import BaseModel, Field
    from typing import Optional

    class User(BaseModel):
        id: int
        name: str = Field(max_length=100)
        email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
        age: Optional[int] = Field(ge=0, le=150)
        is_active: bool = True

    db = WPostgreSQL(User, db_config)

    # This will validate before inserting
    user = User(id=1, name="testuser", email="test@example.com", age=25)
    db.insert(user)