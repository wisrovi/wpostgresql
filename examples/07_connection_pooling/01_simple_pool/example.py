from pydantic import BaseModel

from wpostgresql import ConnectionManager, WPostgreSQL

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


pool = ConnectionManager(db_config, min_connections=1, max_connections=10)

conn = pool.get_connection()
print(f"Conexión obtenida del pool: {conn}")

pool.release_connection(conn)
pool.close_all()

db = WPostgreSQL(Person, db_config)

for i in range(20):
    db.insert(Person(id=i, name=f"Person {i}", age=20 + i))

print("Registros:", len(db.get_all()))
