=================
Relationships
=================

wpostgresql supports various relationship patterns between tables.

One-to-Many Relationship
-------------------------

A person can have multiple addresses:

.. code-block:: python

    from typing import List
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

    def get_person_with_addresses(person_id: int):
        """Get person with all their addresses."""
        with get_connection(db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, name, age FROM person WHERE id = %s", (person_id,))
                person = cursor.fetchone()

                cursor.execute(
                    "SELECT street, city, country FROM address WHERE person_id = %s",
                    (person_id,),
                )
                addresses = cursor.fetchall()

        return person, addresses

    # Usage
    create_tables()

    person = Person(id=1, name="Alice", age=30)
    addresses = [
        {"street": "123 Main St", "city": "New York", "country": "USA"},
        {"street": "456 Oak Ave", "city": "Los Angeles", "country": "USA"},
    ]

    insert_person_with_addresses(person, addresses)

    person_data, addr_data = get_person_with_addresses(1)
    print(f"Person: {person_data[1]}, Age: {person_data[2]}")
    print("Addresses:")
    for addr in addr_data:
        print(f"  - {addr[0]}, {addr[1]}, {addr[2]}")

**Output**::

    Person: Alice, Age: 30
    Addresses:
      - 123 Main St, New York, USA
      - 456 Oak Ave, Los Angeles, USA

Many-to-Many Relationship
--------------------------

Students can enroll in multiple courses:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL
    from wpostgresql.core.connection import get_connection

    class Course(BaseModel):
        id: int
        name: str
        credits: int

    class Student(BaseModel):
        id: int
        name: str
        major: str

    def create_enrollment_tables():
        """Create tables for many-to-many relationship."""
        with get_connection(db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS enrollment CASCADE")
                cursor.execute("DROP TABLE IF EXISTS course CASCADE")
                cursor.execute("DROP TABLE IF EXISTS student CASCADE")

                cursor.execute("""
                    CREATE TABLE student (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        major TEXT
                    )
                """)

                cursor.execute("""
                    CREATE TABLE course (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        credits INTEGER
                    )
                """)

                cursor.execute("""
                    CREATE TABLE enrollment (
                        student_id INTEGER REFERENCES student(id),
                        course_id INTEGER REFERENCES course(id),
                        semester TEXT,
                        PRIMARY KEY (student_id, course_id)
                    )
                """)
            conn.commit()

    def enroll_student_in_courses(student_id: int, course_ids: list[int], semester: str):
        """Enroll a student in multiple courses."""
        with get_connection(db_config) as conn:
            with conn.cursor() as cursor:
                for course_id in course_ids:
                    cursor.execute(
                        "INSERT INTO enrollment (student_id, course_id, semester) VALUES (%s, %s, %s)",
                        (student_id, course_id, semester)
                    )
            conn.commit()

    def get_student_courses(student_id: int):
        """Get all courses for a student."""
        with get_connection(db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.id, c.name, c.credits, e.semester
                    FROM course c
                    JOIN enrollment e ON c.id = e.course_id
                    WHERE e.student_id = %s
                """, (student_id,))
                return cursor.fetchall()

    # Usage
    create_enrollment_tables()

    # Insert students and courses
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO student (name, major) VALUES (%s, %s)", ("John", "CS"))
            cursor.execute("INSERT INTO course (name, credits) VALUES (%s, %s)", ("Python 101", 3))
            cursor.execute("INSERT INTO course (name, credits) VALUES (%s, %s)", ("Database 101", 4))
        conn.commit()

    # Enroll student in courses
    enroll_student_in_courses(1, [1, 2], "Fall 2024")

    # Get enrolled courses
    courses = get_student_courses(1)
    print("Student's courses:")
    for course in courses:
        print(f"  - {course[1]} ({course[2]} credits) - {course[3]}")

**Output**::

    Student's courses:
      - Python 101 (3 credits) - Fall 2024
      - Database 101 (4 credits) - Fall 2024

One-to-One Relationship
------------------------

A user has exactly one profile:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL
    from wpostgresql.core.connection import get_connection

    class User(BaseModel):
        id: int
        username: str
        email: str

    class Profile(BaseModel):
        id: int
        user_id: int
        bio: str
        avatar_url: str

    def create_profile_tables():
        """Create tables for one-to-one relationship."""
        with get_connection(db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS profile CASCADE")
                cursor.execute("DROP TABLE IF EXISTS user_table CASCADE")

                cursor.execute("""
                    CREATE TABLE user_table (
                        id SERIAL PRIMARY KEY,
                        username TEXT NOT NULL,
                        email TEXT NOT NULL
                    )
                """)

                cursor.execute("""
                    CREATE TABLE profile (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER UNIQUE REFERENCES user_table(id),
                        bio TEXT,
                        avatar_url TEXT
                    )
                """)
            conn.commit()

    def create_user_with_profile(user: User, profile: Profile):
        """Create user and their profile atomically."""
        with get_connection(db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO user_table (id, username, email) VALUES (%s, %s, %s)",
                    (user.id, user.username, user.email)
                )
                cursor.execute(
                    "INSERT INTO profile (id, user_id, bio, avatar_url) VALUES (%s, %s, %s, %s)",
                    (profile.id, profile.user_id, profile.bio, profile.avatar_url)
                )
            conn.commit()

    def get_user_with_profile(user_id: int):
        """Get user with their profile."""
        with get_connection(db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM user_table WHERE id = %s", (user_id,))
                user = cursor.fetchone()

                cursor.execute("SELECT * FROM profile WHERE user_id = %s", (user_id,))
                profile = cursor.fetchone()

        return user, profile

    # Usage
    create_profile_tables()

    user = User(id=1, username="johndoe", email="john@example.com")
    profile = Profile(id=1, user_id=1, bio="Software developer", avatar_url="https://example.com/avatar.jpg")

    create_user_with_profile(user, profile)

    user_data, profile_data = get_user_with_profile(1)
    print(f"User: {user_data[1]} ({user_data[2]})")
    print(f"Profile: {profile_data[2]}")
    print(f"Avatar: {profile_data[3]}")

**Output**::

    User: johndoe (john@example.com)
    Profile: Software developer
    Avatar: https://example.com/avatar.jpg