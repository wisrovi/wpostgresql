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


class SQLInjectionError(WPostgreSQLError):
    """Exception raised when SQL injection is detected."""

    pass


class TransactionError(WPostgreSQLError):
    """Exception raised for transaction errors."""

    pass


__all__ = [
    "WPostgreSQLError",
    "ConnectionError",
    "TableSyncError",
    "ValidationError",
    "OperationError",
    "SQLInjectionError",
    "TransactionError",
]
