import pytest
from pydantic import BaseModel

from examples.test.conftest import DB_CONFIG
from wpostgresql.core.connection import get_connection


@pytest.fixture(autouse=True)
def setup():
    with get_connection(DB_CONFIG) as conn:
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
                    person_id INTEGER UNIQUE REFERENCES person(id) ON DELETE CASCADE,
                    bio TEXT,
                    avatar_url TEXT,
                    twitter TEXT
                )
            """)
        conn.commit()
    yield
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS profile CASCADE")
            cursor.execute("DROP TABLE IF EXISTS person CASCADE")
        conn.commit()


def test_create_person_with_profile():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO person (name, email) VALUES (%s, %s)",
                ("Alice", "alice@example.com"),
            )
            cursor.execute("SELECT lastval()")
            person_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO profile (person_id, bio, avatar_url) VALUES (%s, %s, %s)",
                (person_id, "Developer", "https://example.com/alice.jpg"),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM profile WHERE person_id = %s", (person_id,))
            count = cursor.fetchone()[0]

    assert count == 1


def test_get_person_profile():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO person (name, email) VALUES (%s, %s)", ("Bob", "bob@example.com")
            )
            cursor.execute("SELECT lastval()")
            person_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO profile (person_id, bio, avatar_url, twitter) VALUES (%s, %s, %s, %s)",
                (person_id, "Engineer", "https://example.com/bob.jpg", "@bob_dev"),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT bio, twitter FROM profile WHERE person_id = %s", (person_id,))
            profile = cursor.fetchone()

    assert profile[0] == "Engineer"
    assert profile[1] == "@bob_dev"


def test_update_profile():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO person (name, email) VALUES (%s, %s)",
                ("Charlie", "charlie@example.com"),
            )
            cursor.execute("SELECT lastval()")
            person_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO profile (person_id, bio, twitter) VALUES (%s, %s, %s)",
                (person_id, "Developer", "@charlie"),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE profile SET bio = %s, twitter = %s WHERE person_id = %s",
                ("Senior Developer", "@charlie_eng", person_id),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT bio, twitter FROM profile WHERE person_id = %s", (person_id,))
            profile = cursor.fetchone()

    assert profile[0] == "Senior Developer"
    assert profile[1] == "@charlie_eng"


def test_delete_person_deletes_profile():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO person (name, email) VALUES (%s, %s)", ("Diana", "diana@example.com")
            )
            cursor.execute("SELECT lastval()")
            person_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO profile (person_id, bio) VALUES (%s, %s)", (person_id, "Designer")
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM person WHERE id = %s", (person_id,))
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM profile WHERE person_id = %s", (person_id,))
            count = cursor.fetchone()[0]

    assert count == 0
