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
db.insert(Person(id=3, name="Pedro Gómez", age=40, is_active=False))

print("Todos los usuarios:", db.get_all())

print("Usuario por nombre:", db.get_by_field(name="Juan Pérez"))

print("Usuarios activos con 25 años:", db.get_by_field(age=25, is_active=True))
