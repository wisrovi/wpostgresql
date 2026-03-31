===============
Query Builder
===============

.. automodule:: wpostgresql.builders.query_builder
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: wpostgresql.QueryBuilder
   :members:
   :show-inheritance:

Usage
-----

.. code-block:: python

    from wpostgresql import QueryBuilder

    query = (
        QueryBuilder()
        .select("id", "name", "email")
        .from_table("users")
        .where("age", ">", 18)
        .order_by("name")
        .limit(10)
    )

    sql, params = query.build()