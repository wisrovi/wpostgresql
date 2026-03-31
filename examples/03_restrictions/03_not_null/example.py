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


db = WPostgreSQL(Person, db_config)

db.insert(Person(id=1, name="Juan Pérez", age=30))

try:
    db.insert(Person(id=2, name="", age=25))
except Exception as e:
    print("Error: Name no puede ser vacío:", e)
