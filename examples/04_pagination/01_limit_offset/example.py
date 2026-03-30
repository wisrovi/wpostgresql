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

for i in range(1, 11):
    db.insert(Person(id=i, name=f"Person {i}", age=20 + i))

print("Primeros 5 usuarios:", db.get_paginated(limit=5))
print("Saltar primeros 5, mostrar 3:", db.get_paginated(offset=5, limit=3))
print("Ordenados por nombre:", db.get_paginated(limit=5, order_by="name", order_desc=True))
