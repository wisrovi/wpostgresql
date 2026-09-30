"""Example 20: Database Views with WPostgreSQL using the @view decorator.

Demonstrates how to define multi-tables with foreign key relationships,
define a Database View elegantly using the `@view(name=..., depends_on=..., query=...)` decorator,
and execute type-safe ORM read queries on the view.
"""

from pydantic import BaseModel, Field

from wpostgresql import ForeignType, WPostgreSQL, view
from wpostgresql.exceptions import OperationError

# Database configuration
DB_CONFIG = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


# 1. Base Domain Tables
class Customer(BaseModel):
    """Customer entity with auto-generated id."""

    name: str = Field(description="Customer full name")
    email: str = Field(description="Customer email address")


class Invoice(BaseModel):
    """Invoice entity linked to Customer via foreign_key."""

    customer_id: int = Field(
        description="Foreign key to Customer",
        json_schema_extra={
            "foreign_key": Customer,
            "foreign_type": ForeignType.ONE_MANY,
        },
    )
    total_amount: float = Field(description="Invoice total amount")
    invoice_status: str = Field(default="PAID", description="Invoice payment status")


# 2. Database View defined with the elegant @view decorator
@view(
    name="customer_invoice_summary",
    depends_on=[Customer, Invoice],  # Defines parent dependencies for topological DDL creation
    query="""
        SELECT 
            c.id AS customer_id,
            c.name AS customer_name,
            c.email AS customer_email,
            COUNT(i.id) AS total_invoices,
            COALESCE(SUM(i.total_amount), 0.0) AS total_spent
        FROM customer c
        LEFT JOIN invoice i ON c.id = i.customer_id
        GROUP BY c.id, c.name, c.email
    """,
)
class CustomerInvoiceSummary(BaseModel):
    """Pydantic model representing a Database View."""

    customer_id: int
    customer_name: str
    customer_email: str
    total_invoices: int
    total_spent: float


def main():
    print("=" * 80)
    print("🚀 WPostgreSQL Example 20: Database Views (@view Decorator)")
    print("=" * 80)

    # Initialize WPostgreSQL multi-table manager including the View model
    db = WPostgreSQL(
        models=[Customer, Invoice, CustomerInvoiceSummary],
        db_config=DB_CONFIG,
    )

    print("\n1. Inserting sample data into Customer and Invoice tables...")
    alice = db[Customer].insert(Customer(name="Alice Smith", email="alice@example.com"))
    bob = db[Customer].insert(Customer(name="Bob Jones", email="bob@example.com"))

    # Add invoices for Alice
    db[Invoice].insert(Invoice(customer_id=alice.id, total_amount=150.50, invoice_status="PAID"))
    db[Invoice].insert(Invoice(customer_id=alice.id, total_amount=89.99, invoice_status="PAID"))

    # Add invoice for Bob
    db[Invoice].insert(Invoice(customer_id=bob.id, total_amount=300.00, invoice_status="PENDING"))

    print("\n2. Querying Database View (CustomerInvoiceSummary)...")
    summaries = db[CustomerInvoiceSummary].get_all()
    for summary in summaries:
        print(
            f"  • Customer #{summary.customer_id} ({summary.customer_name}): "
            f"Invoices={summary.total_invoices}, Total Spent=${summary.total_spent:.2f}"
        )

    print("\n3. Filtering Database View by criteria...")
    high_spenders = db[CustomerInvoiceSummary].filter(customer_name="Alice Smith")
    print(f"  • Found {len(high_spenders)} view record(s) matching 'Alice Smith':")
    for record in high_spenders:
        print(f"    - Email: {record.customer_email}, Total Spent: ${record.total_spent:.2f}")

    print("\n4. Verifying read-only restriction on Database Views...")
    try:
        dummy_view_item = CustomerInvoiceSummary(
            customer_id=999,
            customer_name="Fake",
            customer_email="fake@example.com",
            total_invoices=0,
            total_spent=0.0,
        )
        db[CustomerInvoiceSummary].insert(dummy_view_item)
    except OperationError as err:
        print(f"  ✓ Expected OperationError caught successfully: {err}")

    print("\n✅ Example 20 completed successfully!")


if __name__ == "__main__":
    main()
