from pydantic import BaseModel

from wpostgresql import WPostgreSQL, configure_logging

configure_logging(level="DEBUG", format="json")

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

db.insert(Person(id=1, name="Alice", age=25))
db.get_all()
db.update(1, Person(id=1, name="Alice", age=26))
db.delete(1)
