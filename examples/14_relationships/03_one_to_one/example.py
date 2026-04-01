"""One-to-One relationship example (Person <-> Profile)."""

from typing import Optional

from pydantic import BaseModel

from wpostgresql.core.connection import get_connection

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class Profile(BaseModel):
    id: int
    person_id: int
    bio: str
    avatar_url: str
    twitter: Optional[str] = None


class Person(BaseModel):
    id: int
    name: str
    email: str


def create_tables():
    """Create person and profile tables with one-to-one relationship."""
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS profile CASCADE")
            cursor.execute("DROP TABLE IF EXISTS person CASCADE")

            cursor.execute("""
                CREATE TABLE person (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE profile (
                    id SERIAL PRIMARY KEY,
                    person_id INTEGER UNIQUE REFERENCES person(id),
                    bio TEXT,
                    avatar_url TEXT,
                    twitter TEXT
                )
            """)
        conn.commit()


def create_person_with_profile(person: Person, profile_data: dict) -> int:
    """Create a person with their profile in a transaction."""
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO person (id, name, email) VALUES (%s, %s, %s)",
                (person.id, person.name, person.email),
            )

            cursor.execute(
                "INSERT INTO profile (person_id, bio, avatar_url, twitter) VALUES (%s, %s, %s, %s)",
                (
                    person.id,
                    profile_data["bio"],
                    profile_data["avatar_url"],
                    profile_data.get("twitter"),
                ),
            )
        conn.commit()


def get_person_with_profile(person_id: int) -> tuple:
    """Get person with their profile."""
    with get_connection(db_config) as conn, conn.cursor() as cursor:
        cursor.execute("SELECT id, name, email FROM person WHERE id = %s", (person_id,))
        person = cursor.fetchone()

        cursor.execute(
            "SELECT bio, avatar_url, twitter FROM profile WHERE person_id = %s", (person_id,)
        )
        profile = cursor.fetchone()

    return person, profile


def update_profile(person_id: int, bio: str = None, twitter: str = None):
    """Update a person's profile."""
    set_clauses = []
    params = []

    if bio is not None:
        set_clauses.append("bio = %s")
        params.append(bio)
    if twitter is not None:
        set_clauses.append("twitter = %s")
        params.append(twitter)

    if set_clauses:
        query = f"UPDATE profile SET {', '.join(set_clauses)} WHERE person_id = %s"
        params.append(person_id)

        with get_connection(db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
            conn.commit()


def delete_person_with_profile(person_id: int):
    """Delete person and their profile (profile cascades)."""
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM person WHERE id = %s", (person_id,))
        conn.commit()


create_tables()

person = Person(id=1, name="Alice", email="alice@example.com")
profile_data = {
    "bio": "Software developer and tech enthusiast",
    "avatar_url": "https://example.com/alice.jpg",
    "twitter": "@alice_dev",
}

create_person_with_profile(person, profile_data)

print("=== One-to-One Relationship ===\n")

person_data, profile_data = get_person_with_profile(1)
print(f"Person: {person_data[1]} ({person_data[2]})")
print("Profile:")
print(f"  Bio: {profile_data[0]}")
print(f"  Avatar: {profile_data[1]}")
print(f"  Twitter: {profile_data[2]}")

update_profile(1, bio="Senior Software Engineer", twitter="@alice_eng")

print("\nAfter update:")
person_data, profile_data = get_person_with_profile(1)
print(f"  Bio: {profile_data[0]}")
print(f"  Twitter: {profile_data[2]}")
