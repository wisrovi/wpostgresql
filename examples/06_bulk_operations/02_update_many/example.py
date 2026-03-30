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
    status: str


db = WPostgreSQL(Person, db_config)

db.insert(Person(id=1, name="Alice", status="active"))
db.insert(Person(id=2, name="Bob", status="active"))
db.insert(Person(id=3, name="Charlie", status="active"))

updates = [
    {"id": 1, "status": "inactive"},
    {"id": 2, "status": "inactive"},
]
db.update_many(updates, "status")

print("Usuarios actualizados:", db.get_all())
