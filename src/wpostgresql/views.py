"""Database View decorator and utilities for WPostgreSQL."""

from typing import Any, Callable, Optional, Union


def view(
    name: Optional[Union[str, Callable]] = None,
    query: Optional[str] = None,
    depends_on: Optional[list[type]] = None,
) -> Callable:
    """Decorator to define a PostgreSQL Database View on a Pydantic model.

    Args:
        name: Optional custom name for the view in PostgreSQL. Defaults to snake_case of class name.
        query: SQL SELECT query string for the view.
        depends_on: Optional list of Pydantic model classes that the view depends on for topological DDL ordering.

    Returns:
        Callable: Decorator function.
    """

    def decorator(cls: type) -> type:
        # Resolve view name
        if isinstance(name, str) and name:
            v_name = name
        else:
            # Convert CamelCase to snake_case if name not provided
            import re

            v_name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

        # Resolve view query (can be passed in decorator or declared in class body)
        v_query = query or getattr(cls, "query", getattr(cls, "__view_query__", None))
        if isinstance(v_query, str):
            v_query = v_query.strip()

        # Resolve dependencies (can be passed in decorator or declared in class body)
        v_deps = depends_on or getattr(
            cls, "depends_on", getattr(cls, "__depends_on__", [])
        )

        setattr(cls, "__view_name__", v_name)
        setattr(cls, "__view_query__", v_query)
        setattr(cls, "__depends_on__", v_deps)
        return cls

    if callable(name) and not isinstance(name, str):
        cls_arg = name
        name = None
        return decorator(cls_arg)

    return decorator
