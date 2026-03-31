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
    age: int


db = WPostgreSQL(Person, db_config)

db.insert(Person(id=1, name="Juan Pérez", age=30))

try:
    db.insert(Person(id=1, name="Ana López", age=25))
except Exception as e:
    print("Error: No se puede insertar ID duplicado:", e)
