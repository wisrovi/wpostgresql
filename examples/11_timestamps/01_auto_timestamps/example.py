"""Automatic timestamps example using WPostgreSQL ORM."""

import time
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field
from wpostgresql import WPostgreSQL, ForensicModel

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class Person(BaseModel):
    """Person model with timestamp fields."""

    name: str
    age: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class ForensicPerson(ForensicModel):
    """Person model with built-in automatic forensic timestamps (create_in, update_in)."""

    name: str
    age: int


def main():
    print("--- 1. Pydantic Model with Timestamp Fields ---")
    db = WPostgreSQL(Person, db_config)
    try:
        db._sync.drop_table()
    except Exception:
        pass
    db = WPostgreSQL(Person, db_config)

    # Insert with automatic timestamps
    person = db.insert(Person(name="Alice", age=30))
    person_id = getattr(person, "id", 1)

    results = db.get_by_field(id=person_id)
    print("After insert:")
    print(f"  created_at: {results[0].created_at}")
    print(f"  updated_at: {results[0].updated_at}")

    time.sleep(0.5)

    # Update timestamp
    updated_person = Person(
        name="Alice Smith",
        age=31,
        created_at=results[0].created_at,
        updated_at=datetime.now(timezone.utc),
    )
    db.update(person_id, updated_person)

    results = db.get_by_field(id=person_id)
    print("\nAfter update:")
    print(f"  name: {results[0].name}")
    print(f"  age: {results[0].age}")
    print(f"  created_at: {results[0].created_at}")
    print(f"  updated_at: {results[0].updated_at}")

    print("\n--- 2. Built-in Forensic Timestamps (ForensicModel) ---")
    f_db = WPostgreSQL(ForensicPerson, db_config)
    try:
        f_db._sync.drop_table()
    except Exception:
        pass
    f_db = WPostgreSQL(ForensicPerson, db_config)

    f_person = f_db.insert(ForensicPerson(name="Bob", age=25), user_id=100)
    f_id = getattr(f_person, "id", 1)
    print(f"Inserted ForensicPerson Bob (ID={f_id}) with automatic create_in timestamp!")

    f_updated = ForensicPerson(name="Bob Smith", age=26)
    f_db.update(f_id, f_updated, user_id=200)
    print(f"Updated ForensicPerson Bob with automatic update_in timestamp!")


if __name__ == "__main__":
    main()
