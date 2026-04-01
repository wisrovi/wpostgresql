"""Raw SQL execution examples."""

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


db = WPostgreSQL(Person, db_config)

db.insert(Person(id=1, name="Alice", age=30))
db.insert(Person(id=2, name="Bob", age=25))


# Using get_connection directly for raw SQL
print("=== Raw SQL Examples ===\n")

# 1. Simple query
with get_connection(db_config) as conn, conn.cursor() as cursor:
    cursor.execute("SELECT * FROM person")
    rows = cursor.fetchall()
    print("1. All records:")
    for row in rows:
        print(f"   {row}")

# 2. Query with parameters
with get_connection(db_config) as conn, conn.cursor() as cursor:
    cursor.execute("SELECT * FROM person WHERE age > %s", (26,))
    rows = cursor.fetchall()
    print("\n2. People older than 26:")
    for row in rows:
        print(f"   {row}")

# 3. Query with string parameter
with get_connection(db_config) as conn, conn.cursor() as cursor:
    cursor.execute("SELECT * FROM person WHERE name = %s", ("Alice",))
    row = cursor.fetchone()
    print("\n3. Person named Alice:")
    print(f"   {row}")

# 4. INSERT with RETURNING
with get_connection(db_config) as conn:
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO person (name, age) VALUES (%s, %s) RETURNING id, name", ("Charlie", 35)
        )
        row = cursor.fetchone()
        print("\n4. Insert with RETURNING:")
        print(f"   Inserted: id={row[0]}, name={row[1]}")
    conn.commit()

# 5. UPDATE with RETURNING
with get_connection(db_config) as conn:
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE person SET age = %s WHERE name = %s RETURNING id, name, age", (36, "Charlie")
        )
        row = cursor.fetchone()
        print("\n5. Update with RETURNING:")
        print(f"   Updated: id={row[0]}, name={row[1]}, age={row[2]}")
    conn.commit()

# 6. DELETE with RETURNING
with get_connection(db_config) as conn:
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM person WHERE name = %s RETURNING id, name", ("Bob",))
        row = cursor.fetchone()
        print("\n6. Delete with RETURNING:")
        print(f"   Deleted: id={row[0]}, name={row[1]}")
    conn.commit()

# 7. Transaction with multiple operations
print("\n7. Transaction with multiple operations:")
db.execute_transaction(
    [
        ("INSERT INTO person (name, age) VALUES (%s, %s)", ("Diana", 28)),
        ("INSERT INTO person (name, age) VALUES (%s, %s)", ("Eve", 22)),
        ("UPDATE person SET age = age + 1 WHERE name = %s", ("Alice",)),
    ]
)

with get_connection(db_config) as conn, conn.cursor() as cursor:
    cursor.execute("SELECT * FROM person ORDER BY id")
    rows = cursor.fetchall()
    print("   Final state:")
    for row in rows:
        print(f"   {row}")

# 8. Using execute_transaction
print("\n8. Using execute_transaction:")
results = db.execute_transaction(
    [
        ("SELECT COUNT(*) FROM person", None),
    ]
)
print(f"   Count: {results[0][0]}")
