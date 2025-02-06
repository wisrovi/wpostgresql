import psycopg2
from pydantic import BaseModel, Field
from typing import Type, List, Any


class WPostgreSQL:
    def __init__(self, model: Type[BaseModel], db_config: dict):
        """
        Inicializa la clase con el modelo Pydantic y la configuración de conexión.
        db_config debe ser un diccionario con parámetros como:
        { 'dbname': 'tu_db', 'user': 'tu_usuario', 'password': 'tu_contraseña', 'host': 'localhost', 'port': 5432 }
        """
        self.model = model
        self.db_config = db_config
        self.table_name = model.__name__.lower()

        self._create_table_if_not_exists()
        self._sync_table_with_model()

    def _get_connection(self):
        """Obtiene una conexión a la base de datos PostgreSQL."""
        return psycopg2.connect(**self.db_config)

    def _create_table_if_not_exists(self):
        """Crea la tabla en PostgreSQL si no existe."""
        fields = ", ".join(
            f"{field} {self._get_sql_type(typ)}"
            for field, typ in self.model.model_fields.items()
        )
        query = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({fields})"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
            conn.commit()

    def _sync_table_with_model(self):
        """
        Sincroniza la tabla con el modelo Pydantic, agregando nuevos campos si es necesario.
        Se consulta information_schema.columns para obtener las columnas existentes.
        """
        query = (
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
        )
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (self.table_name,))
                rows = cursor.fetchall()
                existing_columns = {row[0] for row in rows}

        model_fields = set(self.model.model_fields.keys())
        new_fields = model_fields - existing_columns

        if new_fields:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    for field in new_fields:
                        field_type = self._get_sql_type(self.model.model_fields[field])
                        alter_query = f"ALTER TABLE {self.table_name} ADD COLUMN {field} {field_type} DEFAULT NULL"
                        cursor.execute(alter_query)
                conn.commit()

    def _get_sql_type(self, field):
        """
        Convierte tipos de Pydantic a tipos de PostgreSQL con soporte para restricciones.
        Se mapea int a INTEGER, str a TEXT y bool a BOOLEAN. Se agregan restricciones si la descripción
        del campo contiene palabras clave como "primary", "unique" o "not null".
        """
        type_mapping = {int: "INTEGER", str: "TEXT", bool: "BOOLEAN"}
        sql_type = type_mapping.get(field.annotation, "TEXT")

        constraints = []
        # Se utiliza la descripción del campo para determinar restricciones
        description = (field.description or "").lower()
        if "primary" in description:
            constraints.append("PRIMARY KEY")
        if "unique" in description:
            constraints.append("UNIQUE")
        if "not null" in description:
            constraints.append("NOT NULL")

        return f"{sql_type} {' '.join(constraints)}".strip()

    def insert(self, data: BaseModel):
        """Inserta un nuevo registro en la base de datos."""
        data_dict = data.model_dump()
        fields = ", ".join(data_dict.keys())
        placeholders = ", ".join(["%s"] * len(data_dict))
        values = tuple(data_dict.values())

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
            conn.commit()

    def get_all(self) -> List[BaseModel]:
        """Obtiene todos los registros de la tabla y maneja valores NULL."""
        query = f"SELECT * FROM {self.table_name}"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    def get_by_field(self, **filters) -> List[BaseModel]:
        """Obtiene registros filtrando por cualquier campo."""
        if not filters:
            return self.get_all()

        conditions = " AND ".join(f"{key} = %s" for key in filters.keys())
        values = tuple(filters.values())
        query = f"SELECT * FROM {self.table_name} WHERE {conditions}"

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                rows = cursor.fetchall()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    def update(self, record_id: int, data: BaseModel):
        """Actualiza un registro en la base de datos."""
        data_dict = data.model_dump()
        fields = ", ".join(f"{key} = %s" for key in data_dict.keys())
        values = tuple(data_dict.values()) + (record_id,)
        query = f"UPDATE {self.table_name} SET {fields} WHERE id = %s"

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
            conn.commit()

    def delete(self, record_id: int):
        """Elimina un registro de la base de datos."""
        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (record_id,))
            conn.commit()

    def _default_value(self, field: str) -> Any:
        """
        Devuelve un valor por defecto si el campo es NULL en la base de datos.
        Por ejemplo, una cadena vacía para str, 0 para int o False para bool.
        """
        field_type = self.model.model_fields[field].annotation
        if field_type is str:
            return ""
        elif field_type is int:
            return 0
        elif field_type is bool:
            return False
        return None
