.. _quickstart:

Quickstart Guide
================

.. hero::
   :title: Get Started in Minutes
   :subtitle: Learn the basics of wpostgresql with this hands-on guide
   :image: _static/quickstart.png
   :alt: Quickstart illustration
   :btn1_text: Installation Guide
   :btn1_url: #installation
   :btn2_text: View Full Examples
   :btn2_url: #examples
   :btn2_alt: Examples
   :btn2_class: btn-secondary
   :btn1_class: btn-primary
   :color: primary

.. tab-set::

   .. tab-item:: Synchronous
      :sync: true

      This guide will help you get started with wpostgresql synchronous operations in minutes.

      Basic Usage
      -----------
      
      Create a Pydantic model and initialize the database connection:

      .. code-block:: python
         :linenos:
         :emphasize-lines: 15,30

         from pydantic import BaseModel
         from wpostgresql import WPostgreSQL

         class User(BaseModel):
             id: int
             name: str
             email: str

         db_config = {
             "dbname": "mydatabase",
             "user": "myuser",
             "password": "mypassword",
             "host": "localhost",
             "port": 5432,
         }

         db = WPostgreSQL(User, db_config)

      CRUD Operations
      ----------------

      Create:
      
      .. code-block:: python
         :linenos:

         db.insert(User(id=1, name="John Doe", email="john@example.com"))

      Read:
      
      .. code-block:: python
         :linenos:

         all_users = db.get_all()
         john = db.get_by_field(name="John Doe")

      Update:
      
      .. code-block:: python
         :linenos:

         db.update(1, User(id=1, name="John Smith", email="john.smith@example.com"))

      Delete:
      
      .. code-block:: python
         :linenos:

         db.delete(1)

   .. tab-item:: Asynchronous
      :sync: true

      Learn how to use wpostgresql with async/await for high-performance applications.

      Async Operations
      ----------------

      .. code-block:: python
         :linenos:
         :emphasize-lines: 6,12,15

         import asyncio
         from pydantic import BaseModel
         from wpostgresql import WPostgreSQL

         class User(BaseModel):
             id: int
             name: str
             email: str

         async def main():
             db_config = {
                 "dbname": "mydatabase",
                 "user": "myuser",
                 "password": "mypassword",
                 "host": "localhost",
                 "port": 5432,
             }

             db = WPostgreSQL(User, db_config)
             
             # Insert a new record asynchronously
             await db.insert_async(User(id=2, name="Jane", email="jane@example.com"))
             
             # Get all records asynchronously
             users = await db.get_all_async()
             print(users)

         asyncio.run(main())

      Async CRUD Operations
      ---------------------

      Create:
      
      .. code-block:: python
         :linenos:

         await db.insert_async(User(id=1, name="John Doe", email="john@example.com"))

      Read:
      
      .. code-block:: python
         :linenos:

         all_users = await db.get_all_async()
         john = await db.get_by_field_async(name="John Doe")

      Update:
      
      .. code-block:: python
         :linenos:

         await db.update_async(1, User(id=1, name="John Smith", email="john.smith@example.com"))

      Delete:
      
      .. code-block:: python
         :linenos:

         await db.delete_async(1)

.. section-separator::

.. _next-steps:

Next Steps
----------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card::
      :title: Configuration Guide
      :link: configuration.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Learn how to configure database connections, connection pooling, and SSL settings for production use.

   .. grid-item-card::
      :title: CRUD Tutorial
      :link: ../tutorials/crud_operations.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Dive deeper into CRUD operations with advanced filtering, validation, and bulk operations.

   .. grid-item-card::
      :title: API Reference
      :link: ../api_reference/index.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Explore the complete API documentation with detailed method descriptions and parameter information.

   .. grid-item-card::
      :title: Examples Gallery
      :link: ../examples/index.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Browse through practical examples demonstrating all features of wpostgresql.

.. section-separator::

.. include:: examples/01_crud/README.md
   :start-line: 90
   :end-line: 114