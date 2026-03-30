from pydantic import BaseModel

from wpostgresql import WPostgreSQL

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
    "minconn": 1,
    "maxconn": 10,
}


class Person(BaseModel):
    id: int
    name: str
    age: int


db = WPostgreSQL(Person, db_config, pool_enabled=True)

for i in range(20):
    db.insert(Person(id=i, name=f"Person {i}", age=20 + i))

print(f"Conexiones activas: {db.get_pool_status()}")
print("Registros:", len(db.get_all()))
