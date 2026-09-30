"""One-to-Many relationship example (Person -> Addresses) using WPostgreSQL ORM."""

from pydantic import BaseModel, Field
from wpostgresql import WPostgreSQL, ForeignType

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class Person(BaseModel):
    """Person model."""

    name: str
    age: int


class Address(BaseModel):
    """Address model related to Person (1:N relationship)."""

    person_id: int = Field(
        description="Foreign Key to Person",
        json_schema_extra={
            "foreign_key": Person,
            "foreign_type": ForeignType.ONE_MANY,
        },
    )
    street: str
    city: str
    country: str


def main():
    # Initialize WPostgreSQL ORM in multi-table mode
    db = WPostgreSQL([Person, Address], db_config)

    # Clean existing tables for clean execution
    for m in [Address, Person]:
        try:
            db[m]._sync.drop_table()
        except Exception:
            pass

    db = WPostgreSQL([Person, Address], db_config)

    # Insert Person
    person = Person(name="Alice", age=30)
    inserted_person = db.insert(person)
    person_id = getattr(inserted_person, "id", 1)

    # Insert Addresses
    addr1 = Address(person_id=person_id, street="123 Main St", city="New York", country="USA")
    addr2 = Address(person_id=person_id, street="456 Oak Ave", city="Los Angeles", country="USA")
    db.insert(addr1)
    db.insert(addr2)

    print("=== One-to-Many Relationship ===\n")

    fetched_person = db[Person].get(person_id)
    addresses = db.address.filter(person_id=person_id)

    print(f"Person: id={getattr(fetched_person, 'id', 1)}, name={fetched_person.name}, age={fetched_person.age}")
    print("Addresses:")
    for addr in addresses:
        print(f"  - {addr.street}, {addr.city}, {addr.country}")

    people = db[Person].get_all()
    print("\nAll people with addresses:")
    for p in people:
        pid = getattr(p, "id", 1)
        p_addrs = db.address.filter(person_id=pid)
        print(f"  {p.name} (age {p.age}): {len(p_addrs)} addresses")


if __name__ == "__main__":
    main()
