"""SQL type mapping from Pydantic to PostgreSQL."""

from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID


def get_field_foreign_key(field: Any) -> Any:
    """Extract foreign key reference (Model class or str) from Pydantic FieldInfo."""
    if hasattr(field, "foreign_key") and getattr(field, "foreign_key") is not None:
        return getattr(field, "foreign_key")
    extra = getattr(field, "json_schema_extra", None)
    if isinstance(extra, dict) and "foreign_key" in extra:
        return extra["foreign_key"]
    return None


def get_field_foreign_type(field: Any) -> Any:
    """Extract foreign type Enum/str (ONE_ONE, ONE_MANY, MANY_MANY) from Pydantic FieldInfo."""
    if hasattr(field, "foreign_type") and getattr(field, "foreign_type") is not None:
        return getattr(field, "foreign_type")
    extra = getattr(field, "json_schema_extra", None)
    if isinstance(extra, dict) and "foreign_type" in extra:
        return extra["foreign_type"]
    return None


def resolve_foreign_key_sql(field: Any) -> Optional[str]:
    """Resolve REFERENCES clause for a foreign key field definition."""
    fk = get_field_foreign_key(field)
    if fk is None:
        return None

    if isinstance(fk, str):
        if "." in fk:
            tbl, col = fk.split(".", 1)
        else:
            tbl, col = fk, "id"
    elif hasattr(fk, "__tablename__"):
        tbl = fk.__tablename__
        col = "id"
    elif hasattr(fk, "__name__"):
        tbl = fk.__name__.lower()
        col = "id"
    else:
        tbl = str(fk).lower()
        col = "id"

    ft = get_field_foreign_type(field)
    ft_str = str(ft.value if hasattr(ft, "value") else ft).upper()

    extra_constraint = ""
    if "ONE_ONE" in ft_str or "1:1" in ft_str:
        extra_constraint = " UNIQUE"

    return f"REFERENCES {tbl}({col}){extra_constraint}"


def get_sql_type(field: Any) -> str:
    """Convert Pydantic field type to PostgreSQL type.

    Maps Pydantic types to PostgreSQL types:
    - int -> INTEGER
    - float -> DOUBLE PRECISION
    - str -> TEXT
    - bool -> BOOLEAN
    - datetime -> TIMESTAMP WITH TIME ZONE
    - date -> DATE
    - dict, list -> JSONB
    - UUID -> UUID

    Supports constraints via field description, unique attribute, and foreign keys.

    Args:
        field: Pydantic field info object.

    Returns:
        PostgreSQL type string with constraints.
    """
    annotation = getattr(field, "annotation", Any)

    # Handle Optional[T] / Union[T, None]
    if hasattr(annotation, "__origin__") and str(annotation.__origin__).endswith("Union"):
        args = getattr(annotation, "__args__", ())
        non_none_args = [a for a in args if a is not type(None)]
        if non_none_args:
            annotation = non_none_args[0]

    type_mapping = {
        int: "INTEGER",
        float: "DOUBLE PRECISION",
        str: "TEXT",
        bool: "BOOLEAN",
        datetime: "TIMESTAMP WITH TIME ZONE",
        date: "DATE",
        bytes: "BYTEA",
        UUID: "UUID",
        dict: "JSONB",
        list: "JSONB",
    }
    sql_type = type_mapping.get(annotation, "TEXT")

    constraints = []
    description = (field.description or "").lower()

    if getattr(field, "primary_key", False) or "primary" in description:
        constraints.append("PRIMARY KEY")
    if getattr(field, "unique", False) or "unique" in description:
        constraints.append("UNIQUE")
    if "not null" in description:
        constraints.append("NOT NULL")

    fk_sql = resolve_foreign_key_sql(field)
    if fk_sql:
        constraints.append(fk_sql)

    return f"{sql_type} {' '.join(constraints)}".strip()
