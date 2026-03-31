from typing import Optional

from pydantic import BaseModel, Field

from wpostgresql import WPostgreSQL

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class Person(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool


db = WPostgreSQL(Person, db_config)
db.insert(Person(id=1, name="Ana López", age=25, is_active=True))


class Person(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool
    email: Optional[str]


db = WPostgreSQL(Person, db_config)
db.insert(
    Person(id=2, name="Carlos Ruiz", age=30, is_active=True, email="carlos@example.com")
)

print("Usuarios:", db.get_all())
