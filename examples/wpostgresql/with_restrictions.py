from pydantic import BaseModel, Field
from typing import Optional
from wpostgresql import WPostgreSQL

db_config = {
    'dbname': 'wpostgresql',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}

# Definir el modelo con restricciones
class SimpleModel5(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool
    email: Optional[str] = Field(None, description="UNIQUE")  # Email debe ser único

# Crear la base de datos y sincronizar con el modelo
db = WPostgreSQL(SimpleModel5, db_config)

# Insertar un registro válido
db.insert(SimpleModel5(id=1, name="Juan Pérez", age=30, is_active=True, email="juan@example.com"))

# Intentar insertar un registro con un email duplicado (esto debería fallar)
try:
    db.insert(SimpleModel5(id=2, name="Ana López", age=25, is_active=True, email="juan@example.com"))
except Exception as e:
    print("Error al insertar usuario duplicado:", e)

# Insertar otro registro con un email único (esto funcionará)
db.insert(SimpleModel5(id=3, name="Pedro Gómez", age=40, is_active=False, email="pedro@example.com"))

# Mostrar los registros almacenados
print("Usuarios en la base de datos:", db.get_all())
