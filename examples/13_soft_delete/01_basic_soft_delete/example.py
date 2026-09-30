"""Soft delete example using WPostgreSQL ORM forensic mode."""

from pydantic import BaseModel
from wpostgresql import WPostgreSQL, ForensicModel

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "port": 5432,
    "host": "localhost",
}


class Person(ForensicModel):
    """Person model with built-in forensic soft delete support."""

    name: str
    age: int


def main():
    db = WPostgreSQL(Person, db_config, forensic=True)
    try:
        db._sync.drop_table()
    except Exception:
        pass
    db = WPostgreSQL(Person, db_config, forensic=True)

    # Insert records
    p1 = db.insert(Person(name="Alice", age=30), user_id=101)
    p2 = db.insert(Person(name="Bob", age=25), user_id=101)
    p3 = db.insert(Person(name="Charlie", age=35), user_id=101)

    p1_id = getattr(p1, "id", 1)
    p2_id = getattr(p2, "id", 2)
    p3_id = getattr(p3, "id", 3)

    print("Initial active records:")
    for p in db.get_all():
        print(f"  [{getattr(p, 'id', 1)}] {p.name} (age {p.age})")

    # Soft delete Bob (sets status=99)
    print("\nSoft deleting Bob (ID = 2):")
    db.delete(p2_id, hard=False, user_id=999)

    print("\nActive records (soft-deleted excluded automatically):")
    for p in db.get_all():
        print(f"  [{getattr(p, 'id', 1)}] {p.name} (age {p.age})")

    print("\nDeleted records (retrieved via include_deleted=True):")
    deleted_records = db.get_by_field(include_deleted=True, status=99)
    for p in deleted_records:
        print(f"  [{getattr(p, 'id', 2)}] {p.name} (status={getattr(p, 'status', 99)})")

    # Hard delete Charlie (permanently removes row)
    print("\nHard deleting Charlie (ID = 3):")
    db.delete(p3_id, hard=True)

    print("\nFinal active records:")
    for p in db.get_all():
        print(f"  [{getattr(p, 'id', 1)}] {p.name} (age {p.age})")


if __name__ == "__main__":
    main()
