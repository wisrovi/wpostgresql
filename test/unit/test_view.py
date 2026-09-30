"""Unit tests for WPostgreSQL Database Views functionality with @view decorator."""

import pytest
from pydantic import BaseModel, Field

from wpostgresql import ForeignType, WPostgreSQL, view
from wpostgresql.exceptions import OperationError


class ViewCustomer(BaseModel):
    name: str
    email: str


class ViewOrder(BaseModel):
    customer_id: int = Field(
        json_schema_extra={
            "foreign_key": ViewCustomer,
            "foreign_type": ForeignType.ONE_MANY,
        }
    )
    amount: float


@view(
    name="customer_order_summary",
    depends_on=[ViewCustomer, ViewOrder],
    query="""
        SELECT 
            c.id AS customer_id,
            c.name AS customer_name,
            COUNT(o.id) AS total_orders,
            COALESCE(SUM(o.amount), 0.0) AS total_amount
        FROM viewcustomer c
        LEFT JOIN vieworder o ON c.id = o.customer_id
        GROUP BY c.id, c.name
    """,
)
class CustomerOrderSummary(BaseModel):
    customer_id: int
    customer_name: str
    total_orders: int
    total_amount: float


@pytest.fixture
def db_config():
    return {
        "dbname": "wpostgresql",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": 5432,
    }


def test_database_views_creation_and_query(db_config):
    """Test creating tables + views using @view decorator, inserting data, and querying the view via ORM."""
    db = WPostgreSQL(
        models=[ViewCustomer, ViewOrder, CustomerOrderSummary],
        db_config=db_config,
    )

    # Insert sample data
    u1 = db[ViewCustomer].insert(ViewCustomer(name="ViewTest User 1", email="vt1@example.com"))
    db[ViewCustomer].insert(ViewCustomer(name="ViewTest User 2", email="vt2@example.com"))

    db[ViewOrder].insert(ViewOrder(customer_id=u1.id, amount=100.0))
    db[ViewOrder].insert(ViewOrder(customer_id=u1.id, amount=200.0))

    # Query view
    summaries = db[CustomerOrderSummary].get_all()
    assert isinstance(summaries, list)
    matching = [s for s in summaries if s.customer_id == u1.id]
    assert len(matching) == 1
    assert matching[0].customer_name == "ViewTest User 1"
    assert matching[0].total_orders == 2
    assert matching[0].total_amount == 300.0


def test_database_views_read_only_restriction(db_config):
    """Test that mutation operations (insert, update, delete) on Views raise OperationError."""
    db = WPostgreSQL(
        models=[ViewCustomer, ViewOrder, CustomerOrderSummary],
        db_config=db_config,
    )

    dummy_item = CustomerOrderSummary(
        customer_id=999,
        customer_name="Dummy",
        total_orders=0,
        total_amount=0.0,
    )

    # Test insert restriction
    with pytest.raises(OperationError, match="Database Views are read-only"):
        db[CustomerOrderSummary].insert(dummy_item)

    # Test update restriction
    with pytest.raises(OperationError, match="Database Views are read-only"):
        db[CustomerOrderSummary].update(1, dummy_item)

    # Test delete restriction
    with pytest.raises(OperationError, match="Database Views are read-only"):
        db[CustomerOrderSummary].delete(1)
