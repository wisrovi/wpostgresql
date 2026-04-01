from loguru import logger
from pydantic import BaseModel

from wpostgresql import WPostgreSQL

logger.add("app.log", rotation="500 MB", level="DEBUG")

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

logger.info("Insertando usuario")
db.insert(Person(id=1, name="Alice", age=25))

logger.info("Consultando usuarios")
users = db.get_all()
logger.debug(f"Usuarios encontrados: {len(users)}")

logger.info("Actualizando usuario")
db.update(1, Person(id=1, name="Alice", age=26))

logger.info("Eliminando usuario")
db.delete(1)
