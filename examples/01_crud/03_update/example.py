from pydantic import BaseModel

from wpostgresql import WPostgreSQL

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class Person(BaseModel):
    id: int
    name: str
    age: int
    is_active: bool


db = WPostgreSQL(Person, db_config)

db.insert(Person(id=1, name="Juan Pérez", age=30, is_active=True))

print("Antes de actualizar:", db.get_by_field(id=1))

db.update(1, Person(id=1, name="Juan Pérez", age=31, is_active=False))

print("Después de actualizar:", db.get_by_field(id=1))
