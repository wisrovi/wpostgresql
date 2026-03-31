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


db = WPostgreSQL(Person, db_config)

users = [
    Person(id=1, name="Alice", age=25),
    Person(id=2, name="Bob", age=30),
    Person(id=3, name="Charlie", age=35),
    Person(id=4, name="Diana", age=28),
    Person(id=5, name="Eve", age=32),
]

db.insert_many(users)

print("Usuarios insertados:", db.get_all())
