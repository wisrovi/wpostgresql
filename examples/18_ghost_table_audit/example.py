"""Example showing Enterprise Ghost Table Audit Trail (_forensic_audit_log) in WPostgreSQL.

This example demonstrates:
1. Automatic creation of global _forensic_audit_log table when forensic=True.
2. Automatic change tracking across INSERT, UPDATE, SOFT_DELETE, and HARD_DELETE.
3. Querying the audit trail using db.get_ghost_audit_log() without raw SQL or get_connection.
"""

from typing import Optional
from pydantic import BaseModel
from wpostgresql import WPostgreSQL, ForensicModel

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class BankAccount(ForensicModel):
    """Bank account model with forensic audit enabled."""

    id: int
    holder_name: str
    balance: float


def inspect_ghost_audit_log(db: WPostgreSQL):
    """Fetch and print recorded entries from global _forensic_audit_log ghost table via ORM API."""
    rows = db.get_ghost_audit_log()
    print(f"\n--- Global Audit Log (_forensic_audit_log) [{len(rows)} entries] ---")
    for row in rows:
        print(f"Audit #{row['id']} | Action: {row['action_type']} on [{row['table_name']}] ID={row['record_id']} by User={row['create_by']}")
        if row["data_before"]:
            print(f"   BEFORE: {row['data_before']}")
        if row["data_after"]:
            print(f"   AFTER : {row['data_after']}")
        print("-" * 60)


def main():
    """Execute ghost table audit trail demonstration."""
    print("--- Enterprise Ghost Table Audit Trail Demonstration ---")

    # 1. Initialize WPostgreSQL with a ForensicModel
    db = WPostgreSQL(BankAccount, db_config)

    # 2. Perform INSERT with User ID=100
    print("\n1. Inserting Bank Account (User ID = 100)...")
    account = BankAccount(id=1, holder_name="William Rodriguez", balance=15000.00)
    db.insert(account, user_id=100)

    # 3. Perform UPDATE with User ID=200
    print("\n2. Updating Balance (User ID = 200)...")
    updated_account = BankAccount(id=1, holder_name="William Rodriguez", balance=18500.50)
    db.update(1, updated_account, user_id=200)

    # 4. Perform SOFT DELETE with User ID=999
    print("\n3. Soft Deleting Account (User ID = 999)...")
    db.delete(1, user_id=999, hard=False)

    # 5. Inspect recorded audit trail via ORM API
    inspect_ghost_audit_log(db)


if __name__ == "__main__":
    main()
