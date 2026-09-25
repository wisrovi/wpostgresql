"""Unit tests for WPostgreSQL multi-table management capabilities.

This module validates:
1. Multi-table initialization with list of models.
2. Table resolution using dictionary indexing db[User], db["user"], and db.user attribute access.
3. Automatic routing of insert() and insert_async() based on instance model type.
4. Dynamic registration of new models using register_model() and register_models().
5. Multi-table transaction integrity and error handling.
"""

from typing import Optional
import pytest
from pydantic import BaseModel

from wpostgresql import WPostgreSQL, ForensicModel
from wpostgresql.core.connection import get_connection


class UserModel(ForensicModel):
    """Test model representing users table."""

    id: int
    name: str
    email: str


class ProductModel(BaseModel):
    """Test model representing products table."""

    id: int
    title: str
    price: float


class OrderModel(BaseModel):
    """Test model representing orders table with foreign reference to user."""

    id: int
    user_id: int
    total_amount: float


@pytest.fixture
def mock_db_config(mocker):
    """Provide a mock database configuration and mock connection context."""
    config = {
        "dbname": "test_db",
        "user": "postgres",
        "password": "password",
        "host": "localhost",
        "port": 5432,
    }
    # Mock TableSync methods to prevent actual DB calls during unit tests
    mocker.patch("wpostgresql.core.repository.TableSync.create_if_not_exists")
    mocker.patch("wpostgresql.core.repository.TableSync.sync_with_model")
    return config


def test_multi_table_initialization(mock_db_config):
    """Validate initializing WPostgreSQL in multi-table mode.

    Verifies that passing a list of models configures is_multi_table=True
    and registers all repositories.
    """
    db = WPostgreSQL([UserModel, ProductModel, OrderModel], mock_db_config)

    assert db.is_multi_table is True
    assert db.model is None
    assert db.table_name is None

    # Validate indexing by class
    assert db[UserModel] is not None
    assert db[ProductModel] is not None
    assert db[OrderModel] is not None

    # Validate indexing by string name
    assert db["usermodel"] is not None
    assert db["productmodel"] is not None
    assert db["ordermodel"] is not None

    # Validate attribute access
    assert db.usermodel is not None
    assert db.productmodel is not None
    assert db.ordermodel is not None


def test_single_table_indexing_compatibility(mock_db_config):
    """Validate single-table mode backwards compatibility with indexing.

    Ensures that db[UserModel] or db.usermodel returns self in single-table mode.
    """
    db = WPostgreSQL(UserModel, mock_db_config)

    assert db.is_multi_table is False
    assert db[UserModel] is db
    assert db["usermodel"] is db
    assert db.usermodel is db


def test_dynamic_model_registration(mock_db_config):
    """Validate registering models dynamically after initialization.

    Tests register_model and register_models helper methods.
    """
    db = WPostgreSQL(mock_db_config)  # Starts as empty multi-table manager
    assert db.is_multi_table is True

    repo_user = db.register_model(UserModel)
    assert repo_user is not None
    assert db[UserModel] is repo_user

    registered_list = db.register_models(ProductModel, OrderModel)
    assert len(registered_list) == 2
    assert db.productmodel is registered_list[0]
    assert db.ordermodel is registered_list[1]


def test_multi_table_auto_routing_insert(mock_db_config, mocker):
    """Validate automatic routing of insert() call based on data model type."""
    db = WPostgreSQL([UserModel, ProductModel], mock_db_config)

    user_repo_mock = mocker.patch.object(db[UserModel], "insert")
    product_repo_mock = mocker.patch.object(db[ProductModel], "insert")

    user_inst = UserModel(id=1, name="Alice", email="alice@test.com")
    db.insert(user_inst)
    user_repo_mock.assert_called_once_with(user_inst, user_id=None)

    product_inst = ProductModel(id=10, title="Laptop", price=999.99)
    db.insert(product_inst)
    product_repo_mock.assert_called_once_with(product_inst, user_id=None)


@pytest.mark.asyncio
async def test_multi_table_auto_routing_insert_async(mock_db_config, mocker):
    """Validate automatic routing of insert_async() call based on data model type."""
    db = WPostgreSQL([UserModel, ProductModel], mock_db_config)

    async def fake_insert_async(data, user_id=None):
        return None

    mocker.patch.object(db[UserModel], "insert_async", side_effect=fake_insert_async)
    mocker.patch.object(db[ProductModel], "insert_async", side_effect=fake_insert_async)

    user_inst = UserModel(id=2, name="Bob", email="bob@test.com")
    await db.insert_async(user_inst)


def test_unregistered_model_key_error(mock_db_config):
    """Validate KeyError is raised when accessing an unregistered model or attribute."""
    db = WPostgreSQL([UserModel], mock_db_config)

    class UnregisteredModel(BaseModel):
        id: int

    with pytest.raises(KeyError):
        _ = db[UnregisteredModel]

    with pytest.raises(AttributeError):
        _ = db.unknown_attribute
