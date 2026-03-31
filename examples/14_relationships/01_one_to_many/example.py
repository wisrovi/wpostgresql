"""One-to-Many relationship example (Person -> Addresses)."""

from typing import List, Optional
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


class Address(BaseModel):
    id: int
    person_id: int
    street: str
    city: str
    country: str


class Person(BaseModel):
    id: int
    name: str
    age: int


def create_tables():
    """Create person and address tables with foreign key."""
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS address CASCADE")
            cursor.execute("DROP TABLE IF EXISTS person CASCADE")

            cursor.execute("""
                CREATE TABLE person (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER
                )
            """)

            cursor.execute("""
                CREATE TABLE address (
                    id SERIAL PRIMARY KEY,
                    person_id INTEGER REFERENCES person(id),
                    street TEXT NOT NULL,
                    city TEXT NOT NULL,
                    country TEXT NOT NULL
                )
            """)
        conn.commit()


def insert_person_with_addresses(person: Person, addresses: List[dict]):
    """Insert person and their addresses."""
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO person (id, name, age) VALUES (%s, %s, %s)",
                (person.id, person.name, person.age),
            )

            for addr in addresses:
                cursor.execute(
                    "INSERT INTO address (person_id, street, city, country) VALUES (%s, %s, %s, %s)",
                    (person.id, addr["street"], addr["city"], addr["country"]),
                )
        conn.commit()


def get_person_with_addresses(person_id: int) -> tuple:
    """Get person with all their addresses."""
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, age FROM person WHERE id = %s", (person_id,))
            person = cursor.fetchone()

            cursor.execute(
                "SELECT id, person_id, street, city, country FROM address WHERE person_id = %s",
                (person_id,),
            )
            addresses = cursor.fetchall()

    return person, addresses


def get_all_people_with_addresses() -> list:
    """Get all people with their addresses."""
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, age FROM person ORDER BY id")
            people = cursor.fetchall()

            result = []
            for person in people:
                cursor.execute(
                    "SELECT street, city, country FROM address WHERE person_id = %s",
                    (person[0],),
                )
                addresses = cursor.fetchall()
                result.append({"person": person, "addresses": addresses})

    return result


create_tables()

person = Person(id=1, name="Alice", age=30)
addresses = [
    {"street": "123 Main St", "city": "New York", "country": "USA"},
    {"street": "456 Oak Ave", "city": "Los Angeles", "country": "USA"},
]

insert_person_with_addresses(person, addresses)

print("=== One-to-Many Relationship ===\n")

person_data, addr_data = get_person_with_addresses(1)
print(f"Person: id={person_data[0]}, name={person_data[1]}, age={person_data[2]}")
print("Addresses:")
for addr in addr_data:
    print(f"  - {addr[2]}, {addr[3]}, {addr[4]}")

print("\nAll people with addresses:")
for item in get_all_people_with_addresses():
    p = item["person"]
    print(f"  {p[1]} (age {p[2]}): {len(item['addresses'])} addresses")
