"""Aggregation functions example using WPostgreSQL ORM."""

from typing import Optional
from pydantic import BaseModel, Field
from wpostgresql import WPostgreSQL

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class Person(BaseModel):
    name: str
    age: int
    salary: float
    age_group: Optional[str] = None


def main():
    db = WPostgreSQL(Person, db_config)
    try:
        db._sync.drop_table()
    except Exception:
        pass
    db = WPostgreSQL(Person, db_config)

    db.insert(Person(name="Alice", age=30, salary=5000, age_group="mid"))
    db.insert(Person(name="Bob", age=25, salary=4000, age_group="young"))
    db.insert(Person(name="Charlie", age=35, salary=6000, age_group="mid"))
    db.insert(Person(name="Diana", age=28, salary=5500, age_group="young"))
    db.insert(Person(name="Eve", age=32, salary=4500, age_group="mid"))

    print("COUNT:", db.count())
    print("SUM salary:", db.sum("salary"))
    print("AVG salary:", db.avg("salary"))
    print("MIN age:", db.min("age"))
    print("MAX age:", db.max("age"))

    print("\nGroup by age ranges (AVG salary):")
    grouped = db.aggregate("salary", "AVG", group_by="age_group")
    print(grouped)


if __name__ == "__main__":
    main()
