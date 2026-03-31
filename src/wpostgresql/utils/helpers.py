"""Helper functions for wpostgresql."""

import re


def sanitize_identifier(identifier: str) -> str:
    """Sanitize a database identifier to prevent SQL injection.

    Args:
        identifier: The identifier to sanitize (table name, column name, etc.).

    Returns:
        Sanitized identifier.

    Raises:
        ValueError: If the identifier contains invalid characters.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
        raise ValueError(
            f"Invalid identifier '{identifier}'. "
            "Identifiers must start with a letter or underscore "
            "and contain only alphanumeric characters and underscores."
        )

    return identifier


def to_snake_case(name: str) -> str:
    """Convert a string to snake_case.

    Args:
        name: The string to convert.

    Returns:
        Snake_case version of the string.
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def to_camel_case(name: str) -> str:
    """Convert a string to camelCase.

    Args:
        name: The string to convert.

    Returns:
        CamelCase version of the string.
    """
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])
