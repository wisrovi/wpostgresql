"""Advanced query examples."""

from pydantic import BaseModel

from wpostgresql import WPostgreSQL

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
    email: str
    age: int
    city: str
    salary: float


db = WPostgreSQL(Person, db_config)

db.insert(Person(id=1, name="Alice", email="alice@email.com", age=30, city="NYC", salary=5000))
db.insert(Person(id=2, name="Bob", email="bob@email.com", age=25, city="LA", salary=4000))
db.insert(Person(id=3, name="Charlie", email="charlie@email.com", age=35, city="NYC", salary=6000))
db.insert(Person(id=4, name="Diana", email="diana@email.com", age=28, city="NYC", salary=5500))
db.insert(Person(id=5, name="Eve", email="eve@email.com", age=32, city="LA", salary=4500))

# Using QueryBuilder for complex queries
from wpostgresql import QueryBuilder

qb = (
    QueryBuilder("person")
    .where("age", ">", 25)
    .where("city", "=", "NYC")
    .order_by("salary", descending=True)
    .limit(10)
)

query, values = qb.build_select()
print("Query:", query)
print("Values:", values)

results = db.get_by_field(age__gt=25, city="NYC")
print("Filtered results:", results)

# Get with ordering
all_people = db.get_paginated(order_by="name", order_desc=False)
print("All people ordered by name:", all_people)
