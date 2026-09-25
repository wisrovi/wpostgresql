"""Example 16: Comprehensive Forensic Audit CRUD Operations.

Demonstrates tracking user IDs and UTC timestamps across create, update, and soft delete.
"""

from pydantic import BaseModel
from wpostgresql import ForensicModel, WPostgreSQL

DB_CONFIG = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class Document(ForensicModel):
    id: int
    title: str
    content: str


def main():
    db = WPostgreSQL(Document, DB_CONFIG)

    # Insert documents by Admin (User ID 1) and Editor (User ID 42)
    doc1 = Document(id=1, title="Q1 Report", content="Financial results...")
    doc2 = Document(id=2, title="Q2 Roadmap", content="Upcoming features...")

    db.insert(doc1, user_id=1)
    db.insert(doc2, user_id=42)

    print(f"Total active documents: {db.count()}")

    # Update Document 1 by Reviewer (User ID 99)
    doc1_updated = Document(
        id=1, title="Q1 Report Final", content="Financial results verified..."
    )
    db.update(1, doc1_updated, user_id=99)

    doc_retrieved = db.get_by_field(id=1)[0]
    print(
        f"Document 1 updated by: {doc_retrieved.update_by} at {doc_retrieved.update_in}"
    )

    # Soft delete Document 2 by Auditor (User ID 777)
    db.delete(2, user_id=777)

    print(f"Active documents (excludes soft-deleted): {len(db.get_all())}")
    all_docs = db.get_all(include_deleted=True)
    print(f"Total stored documents (including soft-deleted): {len(all_docs)}")

    for d in all_docs:
        print(
            f"Doc ID: {d.id} | Title: {d.title} | Status: {d.status} | CreatedBy: {d.create_by} | DeletedBy: {d.delete_by}"
        )


if __name__ == "__main__":
    main()
