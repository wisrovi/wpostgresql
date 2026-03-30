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

for i in range(1, 21):
    db.insert(Person(id=i, name=f"Person {i}", age=20 + i))

page_size = 5
print("Página 1:", db.get_all(page=1, page_size=page_size))
print("Página 2:", db.get_all(page=2, page_size=page_size))
print("Página 3:", db.get_all(page=3, page_size=page_size))
