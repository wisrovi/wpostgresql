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
    name: str
    email: Optional[str] = Field(None, description="UNIQUE")


db = WPostgreSQL(Person, db_config)

db.insert(Person(id=1, name="Juan Pérez", email="juan@example.com"))

try:
    db.insert(Person(id=2, name="Ana López", email="juan@example.com"))
except Exception as e:
    print("Error: Email duplicado:", e)
