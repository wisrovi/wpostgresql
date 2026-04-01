"""Aggregation functions examples."""

from typing import Any

from pydantic import BaseModel

from wpostgresql import WPostgreSQL
from wpostgresql.core.connection import get_connection

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
    salary: float


db = WPostgreSQL(Person, db_config)

db.insert(Person(id=1, name="Alice", age=30, salary=5000))
db.insert(Person(id=2, name="Bob", age=25, salary=4000))
db.insert(Person(id=3, name="Charlie", age=35, salary=6000))
db.insert(Person(id=4, name="Diana", age=28, salary=5500))
db.insert(Person(id=5, name="Eve", age=32, salary=4500))


def aggregate(field: str, operation: str) -> Any:
    """Execute aggregation function.

    Args:
        field: Field to aggregate
        operation: Operation (COUNT, SUM, AVG, MIN, MAX)

    Returns:
        Aggregation result
    """
    valid_ops = {"COUNT", "SUM", "AVG", "MIN", "MAX"}
    if operation not in valid_ops:
        raise ValueError(f"Invalid operation: {operation}")

    query = f"SELECT {operation}({field}) as result FROM person"
    with get_connection(db_config) as conn, conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
    return result[0] if result else None


def aggregate_group_by(field: str, operation: str, group_by: str) -> list[dict]:
    """Execute aggregation with GROUP BY.

    Args:
        field: Field to aggregate
        operation: Operation (COUNT, SUM, AVG, MIN, MAX)
        group_by: Field to group by

    Returns:
        List of results
    """
    query = f"SELECT {group_by}, {operation}({field}) as result FROM person GROUP BY {group_by}"
    with get_connection(db_config) as conn, conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return [{"group": row[0], "result": row[1]} for row in rows]


print("COUNT:", aggregate("*", "COUNT"))
print("SUM salary:", aggregate("salary", "SUM"))
print("AVG salary:", aggregate("salary", "AVG"))
print("MIN age:", aggregate("age", "MIN"))
print("MAX age:", aggregate("age", "MAX"))

print("\nGroup by age ranges:")
db.execute_transaction(
    [
        ("ALTER TABLE person ADD COLUMN age_group VARCHAR(10)", None),
    ]
)

db.execute_transaction(
    [
        ("UPDATE person SET age_group = 'young' WHERE age < 30", None),
        ("UPDATE person SET age_group = 'mid' WHERE age >= 30 AND age < 40", None),
        ("UPDATE person SET age_group = 'senior' WHERE age >= 40", None),
    ]
)

results = aggregate_group_by("salary", "AVG", "age_group")
print(results)
