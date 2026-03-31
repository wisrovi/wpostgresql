=============
Basic Usage
=============

Model Definition
----------------

Define your database schema using Pydantic models:

.. code-block:: python

    from pydantic import BaseModel, Field

    class User(BaseModel):
        id: int
        name: str = Field(max_length=100)
        email: str
        age: int | None = None
        is_active: bool = True

Field Types
-----------

wpostgresql supports various Pydantic field types:

.. code-block:: python

    from datetime import datetime
    from typing import Optional

    class Product(BaseModel):
        id: int
        name: str
        price: float
        created_at: datetime
        description: Optional[str] = None
        stock: int = 0

Automatic Table Creation
------------------------

Tables are automatically created when you initialize WPostgreSQL:

.. code-block:: python

    from wpostgresql import WPostgreSQL

    db = WPostgreSQL(User, db_config)

The table ``users`` will be automatically created if it doesn't exist.

Schema Synchronization
-----------------------

The library automatically synchronizes your model schema with the database:

.. code-block:: python

    class User(BaseModel):
        id: int
        name: str
        email: str
        new_field: str = "default_value"

    db = WPostgreSQL(User, db_config)

If the table already exists and you add a new field, it will be added to the table.

Working with Data
-----------------

.. code-block:: python

    user = User(id=1, name="Alice", email="alice@example.com")
    db.insert(user)

    users = db.get_all()
    filtered = db.get_by_field(is_active=True)

    user.name = "Alice Smith"
    db.update(1, user)

    db.delete(1)