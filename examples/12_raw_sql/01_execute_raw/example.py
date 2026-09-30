"""Raw SQL execution and transactions example using WPostgreSQL."""

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
    name: str
    age: int


def main():
    db = WPostgreSQL(Person, db_config)
    try:
        db._sync.drop_table()
    except Exception:
        pass
    db = WPostgreSQL(Person, db_config)

    db.insert(Person(name="Alice", age=30))
    db.insert(Person(name="Bob", age=25))

    print("=== Raw SQL & Transaction Examples ===\n")

    # 1. ORM queries
    print("1. All records:")
    for p in db.get_all():
        print(f"   [{getattr(p, 'id', None)}] {p.name} (age {p.age})")

    # 2. Filter query
    print("\n2. People named Alice:")
    for p in db.filter(name="Alice"):
        print(f"   [{getattr(p, 'id', None)}] {p.name}")

    # 3. Executing queries via execute_transaction
    print("\n3. Transaction with multiple operations:")
    db.execute_transaction(
        [
            ("INSERT INTO person (name, age) VALUES (%s, %s)", ("Diana", 28)),
            ("INSERT INTO person (name, age) VALUES (%s, %s)", ("Eve", 22)),
            ("UPDATE person SET age = age + 1 WHERE name = %s", ("Alice",)),
        ]
    )

    print("   Final state:")
    for p in db.get_all():
        print(f"   [{getattr(p, 'id', None)}] {p.name} (age {p.age})")

    # 4. Aggregate query via execute_transaction
    print("\n4. Aggregate count query via execute_transaction:")
    results = db.execute_transaction(
        [
            ("SELECT COUNT(*) FROM person", None),
        ]
    )
    print(f"   Count: {results[0][0] if results else 0}")


if __name__ == "__main__":
    main()
