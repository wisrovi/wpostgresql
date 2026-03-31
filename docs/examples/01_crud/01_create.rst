.. _examples-crud-create:

Create - Insert Records
=======================

.. hero::
   :title: Insert Records with wpostgresql
   :subtitle: Learn how to insert new records into your PostgreSQL database
   :image: _static/create.png
   :alt: Create operation illustration
   :btn1_text: View Complete Example
   :btn1_url: https://github.com/wisrovi/wpostgresql/tree/main/examples/01_crud/01_create
   :btn2_text: Run This Example
   :btn2_url: #running-this-example
   :btn2_alt: Run Example
   :btn2_class: btn-secondary
   :btn1_class: btn-primary
   :color: primary

.. section-separator::

.. _running-this-example:

Running This Example
--------------------

To run this example directly:

.. code-block:: bash

   # From the project root
   python examples/01_crud/01_create/example.py

Expected output:

.. code-block:: none

   Usuarios creados: [Person(id=1, name='Juan Pérez', age=30, is_active=True), Person(id=2, name='Ana López', age=25, is_active=True)]

.. section-separator::

.. _example-code:

Complete Example Code
---------------------

.. literalinclude:: ../../../examples/01_crud/01_create/example.py
   :language: python
   :linenos:
   :caption: examples/01_crud/01_create/example.py

.. section-separator::

.. _step-by-step:

Step-by-Step Explanation
------------------------

.. tab-set::

   .. tab-item:: Step 1: Import Dependencies
      :sync: true

      .. code-block:: python
         :linenos:
         :emphasize-lines: 1,3

         from pydantic import BaseModel
         from wpostgresql import WPostgreSQL

      We import the necessary modules:
      
      - ``BaseModel`` from Pydantic for defining our data schema
      - ``WPostgreSQL`` from wpostgresql for database operations

   .. tab-item:: Step 2: Configure Database Connection
      :sync: true

      .. code-block:: python
         :linenos:
         :emphasize-lines: 5-11

         db_config = {
             "dbname": "wpostgresql",
             "user": "postgres",
             "password": "postgres",
             "host": "localhost",
             "port": 5432,
         }

      We define our database connection parameters. In a real application, you would typically:
      
      - Use environment variables for security
      - Adjust these values for your specific PostgreSQL setup
      - Consider using connection pooling for production applications

   .. tab-item:: Step 3: Define Data Model
      :sync: true

      .. code-block:: python
         :linenos:
         :emphasize-lines: 14-18

         class Person(BaseModel):
             id: int
             name: str
             age: int
             is_active: bool

      We define a Pydantic model that represents our database table structure:
      
      - Each attribute corresponds to a column in the database
      - Type annotations ensure data integrity
      - wpostgresql will automatically create the table based on this model

   .. tab-item:: Step 4: Initialize wpostgresql
      :sync: true

      .. code-block:: python
         :linenos:
         :emphasize-lines: 21

         db = WPostgreSQL(Person, db_config)

      Creating a WPostgreSQL instance:
      
      - Automatically creates the ``persons`` table if it doesn't exist
      - Synchronizes the table schema with our model definition
      - Sets up connection pooling for efficient database access

   .. tab-item:: Step 5: Insert Records
      :sync: true

      .. code-block:: python
         :linenos:
         :emphasize-lines: 23-25

         db.insert(Person(id=1, name="Juan Pérez", age=30, is_active=True))
         db.insert(Person(id=2, name="Ana López", age=25, is_active=True))
         print("Usuarios creados:", db.get_all())

      Inserting data into the database:
      
      - We create ``Person`` instances with our data
      - The ``insert()`` method validates the data using Pydantic before inserting
      - Each insert returns the inserted record (though we're not capturing it here)
      - Finally, we retrieve and print all records to verify our inserts worked

.. section-separator::

.. _key-points:

Key Points to Remember
----------------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card::
      :title: Automatic Table Creation
      :text: wpostgresql automatically creates tables based on your Pydantic models if they don't already exist.
      :class-card: wpostgresql-card
      :img-top: _static/auto-create.png
      ^^^

   .. grid-item-card::
      :title: Data Validation
      :text: All data is validated using Pydantic before being inserted into the database, ensuring data integrity.
      :class-card: wpostgresql-card
      :img-top: _static/validation.png
      ^^^

   .. grid-item-card::
      :title: Type Safety
      :text: Full type hints throughout the operation ensure you catch errors at development time, not runtime.
      :class-card: wpostgresql-card
      :img-top: _static/typesafety.png
      ^^^

   .. grid-item-card::
      :title: Error Handling
      :text: Proper exception handling is built-in, with meaningful error messages when operations fail.
      :class-card: wpostgresql-card
      :img-top: _static/errorhandling.png
      ^^^

.. section-separator::

.. _related-examples:

Related Examples
----------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card::
      :title: Read Records
      :link: 02_read.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Learn how to query and retrieve data from your database.

   .. grid-item-card::
      :title: Update Records
      :link: 03_update.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Discover how to modify existing records in your database.

   .. grid-item-card::
      :title: Delete Records
      :link: 04_delete.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Explore how to remove records from your database safely.

   .. grid-item-card::
      :title: Bulk Insert
      :link: ../06_bulk_operations/01_insert_many.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      See how to efficiently insert multiple records at once.

.. section-separator::

.. _references:

References
----------

For more information, see:

- :doc:`WPostgreSQL class documentation <../api_reference/repository>`
- :doc:`Pydantic documentation <https://docs.pydantic.dev/>`
- :doc:`PostgreSQL INSERT documentation <https://www.postgresql.org/docs/current/sql-insert.html>`