"""Example showing how to manage multiple PostgreSQL tables using WPostgreSQL.

This example demonstrates:
1. Multi-table initialization passing a list of Pydantic models.
2. Dictionary indexing (db[User]) and direct attribute access (db.product).
3. Automatic routing of insert() operations.
4. Multi-table transactions across multiple models.
"""

from typing import Optional
from pydantic import BaseModel
from wpostgresql import WPostgreSQL, ForensicModel, get_transaction

# Database connection configuration
db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class User(ForensicModel):
    """User account model with forensic auditing enabled."""

    __tablename__ = "users"
    id: int
    name: str
    email: str



class Product(BaseModel):
    """Catalog product model."""

    id: int
    title: str
    price: float


class Order(BaseModel):
    """Customer purchase order model."""

    __tablename__ = "orders"
    id: int
    user_id: int
    product_id: int
    total_amount: float



def main():
    """Execute multi-table management demonstration."""
    print("--- Initializing WPostgreSQL in Multi-Table Mode ---")

    # 1. Initialize WPostgreSQL with a list of Pydantic models
    db = WPostgreSQL([User, Product, Order], db_config)

    # 2. Insert records using dictionary indexing or direct attribute access
    print("\n--- Inserting records into multiple tables ---")

    user = User(id=1, name="William Rodriguez", email="william@example.com")
    product = Product(id=101, title="Antigravity AI License", price=199.99)
    order = Order(id=5001, user_id=1, product_id=101, total_amount=199.99)

    # Method A: Indexing by class (Type-safe)
    db[User].insert(user)

    # Method B: Direct attribute access by model name in lowercase
    db.product.insert(product)

    # Method C: Auto-routing insert via main db instance
    db.insert(order)

    print("Insertion complete across all tables!")

    # 3. Query records from each table repository
    print("\n--- Fetching records from each table ---")

    users = db[User].get_all()
    products = db.product.get_all()
    orders = db[Order].get_all()

    print(f"Users in DB: {len(users)} -> {users[0].name}")
    print(f"Products in DB: {len(products)} -> {products[0].title} (${products[0].price})")
    print(f"Orders in DB: {len(orders)} -> Order #{orders[0].id}")

    # 4. Multi-table Transaction Example
    print("\n--- Executing Multi-Table Transaction ---")
    with get_transaction(db_config) as txn:
        # Transactions work seamlessly across all repositories sharing the db_config pool
        db[User].insert(User(id=2, name="Alice Smith", email="alice@example.com"))
        db.product.insert(Product(id=102, title="Cloud Storage Subscription", price=49.99))
        txn.commit()


    print("Transaction committed successfully!")


if __name__ == "__main__":
    main()
