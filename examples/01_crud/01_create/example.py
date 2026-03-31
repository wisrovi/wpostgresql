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
db.insert(Person(id=2, name="Ana López", age=25, is_active=True))

print("Usuarios creados:", db.get_all())
