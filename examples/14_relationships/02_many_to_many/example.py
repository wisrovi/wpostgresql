"""Many-to-Many relationship example (Students <-> Courses) using WPostgreSQL ORM."""

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


class Student(BaseModel):
    """Student model."""

    name: str
    grade: int


class Course(BaseModel):
    """Course model."""

    name: str
    credits: int


class Enrollment(BaseModel):
    """Junction table model for N:M relationship between Student and Course."""

    student_id: int = Field(
        description="Foreign Key to Student",
        json_schema_extra={
            "foreign_key": Student,
            "foreign_type": ForeignType.MANY_MANY,
        },
    )
    course_id: int = Field(
        description="Foreign Key to Course",
        json_schema_extra={
            "foreign_key": Course,
            "foreign_type": ForeignType.MANY_MANY,
        },
    )
    grade: Optional[str] = None


def main():
    models = [Student, Course, Enrollment]

    # Clean existing tables for clean execution
    cleaner = WPostgreSQL(models, db_config)
    for m in reversed(models):
        try:
            cleaner[m]._sync.drop_table()
        except Exception:
            pass

    # Initialize WPostgreSQL ORM in multi-table mode
    db = WPostgreSQL(models, db_config)

    # Insert Students
    s1 = db.insert(Student(name="Alice", grade=10))
    s2 = db.insert(Student(name="Bob", grade=11))
    s3 = db.insert(Student(name="Charlie", grade=10))

    s1_id = getattr(s1, "id", 1)
    s2_id = getattr(s2, "id", 2)
    s3_id = getattr(s3, "id", 3)

    # Insert Courses
    c1 = db.insert(Course(name="Mathematics", credits=4))
    c2 = db.insert(Course(name="Physics", credits=3))
    c3 = db.insert(Course(name="Chemistry", credits=3))

    c1_id = getattr(c1, "id", 1)
    c2_id = getattr(c2, "id", 2)
    c3_id = getattr(c3, "id", 3)

    # Enroll Students
    db.insert(Enrollment(student_id=s1_id, course_id=c1_id, grade="A"))
    db.insert(Enrollment(student_id=s1_id, course_id=c2_id, grade="A-"))
    db.insert(Enrollment(student_id=s2_id, course_id=c1_id, grade="B+"))
    db.insert(Enrollment(student_id=s2_id, course_id=c3_id, grade="B"))
    db.insert(Enrollment(student_id=s3_id, course_id=c2_id, grade="A"))

    print("=== Many-to-Many Relationship ===\n")

    print("Alice's courses:")
    s1_enrollments = db.enrollment.filter(student_id=s1_id)
    for en in s1_enrollments:
        course = db[Course].get(en.course_id)
        if course:
            print(f"  - {course.name} ({course.credits} credits): {en.grade}")

    print("\nPhysics students:")
    c2_enrollments = db.enrollment.filter(course_id=c2_id)
    for en in c2_enrollments:
        student = db[Student].get(en.student_id)
        if student:
            print(f"  - {student.name} (grade {student.grade}): {en.grade}")


if __name__ == "__main__":
    main()
