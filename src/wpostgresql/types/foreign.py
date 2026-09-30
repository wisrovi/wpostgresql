"""Foreign key relationship types for WPostgreSQL schema definition."""

from enum import Enum


class ForeignType(str, Enum):
    """Enum specifying the relationship type for a foreign key field."""

    ONE_ONE = "ONE_ONE"
    ONE_MANY = "ONE_MANY"
    MANY_MANY = "MANY_MANY"


# Alias for backward compatibility / snake_case naming preference
Foreign_type = ForeignType
