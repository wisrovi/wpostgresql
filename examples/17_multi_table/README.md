# 17 - Multi-Table Management Example

This example demonstrates how to manage multiple PostgreSQL tables using a single `WPostgreSQL` instance.

---

## 🛠️ Key Technologies & Libraries

* **Python 3.10+**: Core programming language.
* **WPostgreSQL**: Type-safe ORM and table sync engine for PostgreSQL.
* **Pydantic**: Data validation and schema definition via `BaseModel`.
* **Psycopg 3**: High-performance PostgreSQL database adapter for Python.
* **Psycopg Pool**: Efficient connection pooling for synchronous and asynchronous operations.

---

## 🚀 Overview

Instead of creating separate repository objects manually for each table, you can pass a list of Pydantic models directly to `WPostgreSQL`:

```python
from wpostgresql import WPostgreSQL

# Register multiple tables in one place
db = WPostgreSQL([User, Product, Order], db_config)

# Access repositories by Pydantic class:
db[User].insert(user_instance)

# Access repositories by attribute name:
products = db.product.get_all()

# Auto-routed insert:
db.insert(order_instance)
```

---

## 📋 Running the Example

Make sure PostgreSQL is running (e.g. via Docker Compose in `docker/`):

```bash
python examples/17_multi_table/example.py
```

---

## 👨‍💻 Author

**William Rodríguez** - AI Leader & Solutions Architect
