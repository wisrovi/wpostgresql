"""Many-to-Many relationship example (Students <-> Courses)."""

from pydantic import BaseModel

from wpostgresql.core.connection import get_connection

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class Student(BaseModel):
    id: int
    name: str
    grade: int


class Course(BaseModel):
    id: int
    name: str
    credits: int


class Enrollment(BaseModel):
    student_id: int
    course_id: int
    grade: str = None


def create_tables():
    """Create many-to-many relationship tables."""
    with get_connection(db_config) as conn:
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


def insert_student(name: str, grade: int) -> int:
    """Insert a student and return their ID."""
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO student (name, grade) VALUES (%s, %s) RETURNING id",
                (name, grade),
            )
            result = cursor.fetchone()
        conn.commit()
    return result[0]


def insert_course(name: str, credits: int) -> int:
    """Insert a course and return its ID."""
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO course (name, credits) VALUES (%s, %s) RETURNING id",
                (name, credits),
            )
            result = cursor.fetchone()
        conn.commit()
    return result[0]


def enroll_student(student_id: int, course_id: int, grade: str = None):
    """Enroll a student in a course."""
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO enrollment (student_id, course_id, grade) VALUES (%s, %s, %s)",
                (student_id, course_id, grade),
            )
        conn.commit()


def get_student_courses(student_id: int) -> list:
    """Get all courses for a student."""
    with get_connection(db_config) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
                SELECT c.id, c.name, c.credits, e.grade
                FROM course c
                JOIN enrollment e ON c.id = e.course_id
                WHERE e.student_id = %s
                """,
            (student_id,),
        )
        return cursor.fetchall()


def get_course_students(course_id: int) -> list:
    """Get all students in a course."""
    with get_connection(db_config) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
                SELECT s.id, s.name, s.grade, e.grade
                FROM student s
                JOIN enrollment e ON s.id = e.student_id
                WHERE e.course_id = %s
                """,
            (course_id,),
        )
        return cursor.fetchall()


create_tables()

student1_id = insert_student("Alice", 10)
student2_id = insert_student("Bob", 11)
student3_id = insert_student("Charlie", 10)

course1_id = insert_course("Mathematics", 4)
course2_id = insert_course("Physics", 3)
course3_id = insert_course("Chemistry", 3)

enroll_student(student1_id, course1_id, "A")
enroll_student(student1_id, course2_id, "A-")
enroll_student(student2_id, course1_id, "B+")
enroll_student(student2_id, course3_id, "B")
enroll_student(student3_id, course2_id, "A")

print("=== Many-to-Many Relationship ===\n")

print("Alice's courses:")
for course in get_student_courses(student1_id):
    print(f"  - {course[1]} ({course[2]} credits): {course[3]}")

print("\nPhysics students:")
for student in get_course_students(course2_id):
    print(f"  - {student[1]} (grade {student[2]}): {student[3]}")
