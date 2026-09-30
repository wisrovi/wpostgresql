"""One-to-One relationship example (Person <-> Profile) using WPostgreSQL ORM."""

from typing import Optional
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
    email: str = Field(json_schema_extra={"unique": True})


class Profile(BaseModel):
    """Profile model with 1:1 relationship to Person."""

    person_id: int = Field(
        description="Foreign Key to Person (1:1)",
        json_schema_extra={
            "foreign_key": Person,
            "foreign_type": ForeignType.ONE_ONE,
        },
    )
    bio: str
    avatar_url: str
    twitter: Optional[str] = None


def main():
    models = [Person, Profile]

    # Clean existing tables for clean execution
    cleaner = WPostgreSQL(models, db_config)
    for m in reversed(models):
        try:
            cleaner[m]._sync.drop_table()
        except Exception:
            pass

    # Initialize WPostgreSQL ORM in multi-table mode
    db = WPostgreSQL(models, db_config)

    # Insert Person
    person = db.insert(Person(name="Alice", email="alice@example.com"))
    person_id = getattr(person, "id", 1)

    # Insert 1:1 Profile
    profile = Profile(
        person_id=person_id,
        bio="Software developer and tech enthusiast",
        avatar_url="https://example.com/alice.jpg",
        twitter="@alice_dev",
    )
    db.insert(profile)

    print("=== One-to-One Relationship ===\n")

    fetched_person = db[Person].get(person_id)
    profiles = db.profile.filter(person_id=person_id)
    fetched_profile = profiles[0] if profiles else None

    print(f"Person: {fetched_person.name} ({fetched_person.email})")
    if fetched_profile:
        print("Profile:")
        print(f"  Bio: {fetched_profile.bio}")
        print(f"  Avatar: {fetched_profile.avatar_url}")
        print(f"  Twitter: {fetched_profile.twitter}")

    # Update Profile
    updated_profile = Profile(
        person_id=person_id,
        bio="Senior Software Engineer",
        avatar_url=fetched_profile.avatar_url,
        twitter="@alice_eng",
    )
    profile_id = getattr(fetched_profile, "id", 1)
    db.profile.update(profile_id, updated_profile)

    print("\nAfter update:")
    profiles_updated = db.profile.filter(person_id=person_id)
    up = profiles_updated[0] if profiles_updated else None
    if up:
        print(f"  Bio: {up.bio}")
        print(f"  Twitter: {up.twitter}")


if __name__ == "__main__":
    main()
