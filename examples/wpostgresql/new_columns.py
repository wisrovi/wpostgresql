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

# Modelo inicial sin el campo email
class SimpleModel4(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool

# Crear la tabla con el modelo inicial e insertar un registro
db = WPostgreSQL(SimpleModel4, db_config)
db.insert(SimpleModel4(id=1, name="Ana López", age=25, is_active=True))

# === AHORA SE AÑADE UN NUEVO CAMPO AL MODELO ===
class SimpleModel4(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool
    email: Optional[str]  # Nuevo campo sin restricciones en la base de datos

# Al instanciar nuevamente WPostgreSQL con el modelo actualizado se sincroniza la tabla
db = WPostgreSQL(SimpleModel4, db_config)

# Insertar un nuevo registro que incluya el nuevo campo
db.insert(SimpleModel4(id=2, name="Ana López", age=25, is_active=True, email="ana@example.com"))

# Mostrar todos los registros después de la actualización
print("Usuarios después de actualizar el modelo:", db.get_all())
