"""Custom exceptions for wpostgresql."""


class WPostgreSQLError(Exception):
    """Base exception for wpostgresql errors."""

    pass


class ConnectionError(WPostgreSQLError):
    """Exception raised for connection errors."""

    pass


class TableSyncError(WPostgreSQLError):
    """Exception raised during table synchronization."""

    pass


class ValidationError(WPostgreSQLError):
    """Exception raised for validation errors."""

    pass


class OperationError(WPostgreSQLError):
    """Exception raised for database operation errors."""

    pass


__all__ = [
    "WPostgreSQLError",
    "ConnectionError",
    "TableSyncError",
    "ValidationError",
    "OperationError",
]
