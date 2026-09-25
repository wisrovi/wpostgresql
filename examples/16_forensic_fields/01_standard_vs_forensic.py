"""Example 16: Standard vs Forensic Mode in WPostgreSQL.

This example demonstrates:
1. Standard Mode (forensic=False by default for BaseModel): Performs direct physical CRUD.
2. Forensic Mode (inheriting from ForensicModel or passing forensic=True): Automatically manages audit columns and soft delete (status=99).
"""

from pydantic import BaseModel
from wpostgresql import ForensicModel, WPostgreSQL

# Connection configuration
DB_CONFIG = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


# 1. Standard Pydantic model (Standard mode)
class StandardUser(BaseModel):
    id: int
    name: str
    email: str


# 2. Forensic Pydantic model (Forensic mode)
class ForensicUser(ForensicModel):
    id: int
    name: str
    email: str


def main():
    print("--- 1. Standard Mode ---")
    db_std = WPostgreSQL(StandardUser, DB_CONFIG)
    print(f"Standard DB Forensic Mode Enabled: {db_std.forensic}")

    user1 = StandardUser(id=1, name="Alice", email="alice@example.com")
    db_std.insert(user1)
    print(f"Active Users in Standard Mode: {len(db_std.get_all())}")

    db_std.delete(1)
    print(f"Users after physical deletion: {len(db_std.get_all())}")

    print("\n--- 2. Forensic Mode ---")
    db_forensic = WPostgreSQL(ForensicUser, DB_CONFIG)
    print(f"Forensic DB Forensic Mode Enabled: {db_forensic.forensic}")

    user2 = ForensicUser(id=2, name="Bob", email="bob@example.com")
    db_forensic.insert(user2, user_id=101)  # Created by user ID 101

    records = db_forensic.get_all()
    print(
        f"Inserted record: name={records[0].name}, create_by={records[0].create_by}, status={records[0].status}"
    )

    # Update record
    updated_bob = ForensicUser(
        id=2, name="Bob Builder", email="bob.builder@example.com"
    )
    db_forensic.update(2, updated_bob, user_id=202)  # Updated by user ID 202

    # Soft delete record (sets status=99, delete_by=303)
    db_forensic.delete(2, user_id=303)

    print(f"Active Users after soft delete (status!=99): {len(db_forensic.get_all())}")
    deleted_records = db_forensic.get_all(include_deleted=True)
    print(f"Total Users including soft-deleted: {len(deleted_records)}")
    print(
        f"Soft deleted item: status={deleted_records[0].status}, delete_by={deleted_records[0].delete_by}"
    )


if __name__ == "__main__":
    main()
