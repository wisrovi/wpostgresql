============
Installation
============

Requirements
------------

* Python 3.9 or higher
* PostgreSQL 12 or higher
* psycopg 3.1+
* pydantic 2.0+

Installation Methods
--------------------

Using pip (recommended):

.. code-block:: bash

    pip install wpostgresql

Using poetry:

.. code-block:: bash

    poetry add wpostgresql

From source:

.. code-block:: bash

    git clone https://github.com/wisrovi/wpostgresql.git
    cd wpostgresql
    pip install -e .

Optional Dependencies
----------------------

For development and testing:

.. code-block:: bash

    pip install wpostgresql[dev]

For full async support:

.. code-block:: bash

    pip install wpostgresql[async]

Verify Installation
-------------------

.. code-block:: python

    >>> import wpostgresql
    >>> print(wpostgresql.__version__)
    0.3.0