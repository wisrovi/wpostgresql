import pytest
from pydantic import BaseModel

from examples.test.conftest import DB_CONFIG
from wpostgresql.core.connection import get_connection


@pytest.fixture(autouse=True)
def setup():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS enrollment CASCADE")
            cursor.execute("DROP TABLE IF EXISTS course CASCADE")
            cursor.execute("DROP TABLE IF EXISTS student CASCADE")

            cursor.execute("""
                CREATE TABLE student (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    grade INTEGER
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
                    grade TEXT,
                    PRIMARY KEY (student_id, course_id)
                )
            """)
        conn.commit()
    yield
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS enrollment CASCADE")
            cursor.execute("DROP TABLE IF EXISTS course CASCADE")
            cursor.execute("DROP TABLE IF EXISTS student CASCADE")
        conn.commit()


def test_enroll_student_in_course():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO student (name, grade) VALUES (%s, %s)", ("Alice", 10))
            cursor.execute("SELECT lastval()")
            student_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO course (name, credits) VALUES (%s, %s)", ("Math", 4))
            cursor.execute("SELECT lastval()")
            course_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO enrollment (student_id, course_id, grade) VALUES (%s, %s, %s)",
                (student_id, course_id, "A"),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM enrollment WHERE student_id = %s AND course_id = %s",
                (student_id, course_id),
            )
            count = cursor.fetchone()[0]

    assert count == 1


def test_get_student_courses():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO student (name, grade) VALUES (%s, %s)", ("Bob", 11))
            cursor.execute("SELECT lastval()")
            student_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO course (name, credits) VALUES (%s, %s)", ("Physics", 3))
            cursor.execute("SELECT lastval()")
            course1_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO course (name, credits) VALUES (%s, %s)", ("Chemistry", 3))
            cursor.execute("SELECT lastval()")
            course2_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO enrollment (student_id, course_id, grade) VALUES (%s, %s, %s)",
                (student_id, course1_id, "B+"),
            )
            cursor.execute(
                "INSERT INTO enrollment (student_id, course_id, grade) VALUES (%s, %s, %s)",
                (student_id, course2_id, "A"),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.name FROM course c
                JOIN enrollment e ON c.id = e.course_id
                WHERE e.student_id = %s
                """,
                (student_id,),
            )
            courses = cursor.fetchall()

    assert len(courses) == 2


def test_get_course_students():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO course (name, credits) VALUES (%s, %s)", ("Biology", 4))
            cursor.execute("SELECT lastval()")
            course_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO student (name, grade) VALUES (%s, %s)", ("Charlie", 10))
            cursor.execute("SELECT lastval()")
            s1 = cursor.fetchone()[0]

            cursor.execute("INSERT INTO student (name, grade) VALUES (%s, %s)", ("Diana", 11))
            cursor.execute("SELECT lastval()")
            s2 = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO enrollment (student_id, course_id, grade) VALUES (%s, %s, %s)",
                (s1, course_id, "A"),
            )
            cursor.execute(
                "INSERT INTO enrollment (student_id, course_id, grade) VALUES (%s, %s, %s)",
                (s2, course_id, "B+"),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT s.name FROM student s
                JOIN enrollment e ON s.id = e.student_id
                WHERE e.course_id = %s
                """,
                (course_id,),
            )
            students = cursor.fetchall()

    assert len(students) == 2
