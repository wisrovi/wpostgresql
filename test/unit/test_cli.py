"""Tests for CLI module.

This module contains unit tests for the command-line interface of wpostgresql,
ensuring all commands (init, list, insert, count, get, delete, drop)
behave as expected.
"""

import tempfile
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner
from loguru import logger
from pydantic import BaseModel

from wpostgresql.cli.main import cli, load_model


class TestCLI:
    """Tests for CLI commands.

    This class groups tests that verify the behavior of the wpostgresql CLI tool.
    """

    def test_cli_help(self) -> None:
        """Test CLI shows help message.

        Verifies that the --help flag returns a successful exit code and
        contains the tool name.
        """
        logger.info("Testing CLI --help...")
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "wpostgresql" in result.output
        logger.success("CLI --help test passed.")

    def test_cli_version(self) -> None:
        """Test CLI shows correct version.

        Verifies that the --version flag returns the expected version number.
        """
        logger.info("Testing CLI --version...")
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.3.0" in result.output
        logger.success("CLI --version test passed.")

    @patch("wpostgresql.cli.main.ConnectionManager")
    def test_test_connection_success(self, _mock_cm: Mock) -> None:
        """Test test-connection command success.

        Args:
            _mock_cm: Mocked ConnectionManager.
        """
        logger.info("Testing test-connection success...")
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w", encoding="utf-8") as f:
                f.write('{"dbname": "test"}')

            result = runner.invoke(cli, ["test-connection", "config.json"])
            assert result.exit_code == 0
            assert "Connection successful" in result.output
        logger.success("test-connection success test passed.")

    @patch("wpostgresql.cli.main.ConnectionManager")
    def test_test_connection_failure(self, mock_cm: Mock) -> None:
        """Test test-connection command failure.

        Args:
            mock_cm: Mocked ConnectionManager.
        """
        logger.info("Testing test-connection failure...")
        mock_cm.side_effect = Exception("Connection failed")

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w", encoding="utf-8") as f:
                f.write('{"dbname": "test"}')

            result = runner.invoke(cli, ["test-connection", "config.json"])
            assert result.exit_code == 1
            assert "Connection failed" in result.output
        logger.success("test-connection failure test passed.")

    @patch("wpostgresql.cli.main.TableSync")
    def test_init_command(self, mock_sync: Mock) -> None:
        """Test init command.

        Args:
            mock_sync: Mocked TableSync class.
        """
        logger.info("Testing init command...")
        mock_sync_instance = MagicMock()
        mock_sync.return_value = mock_sync_instance

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w", encoding="utf-8") as f:
                f.write('{"dbname": "test"}')

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(
                    """
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
"""
                )
                model_path = f.name

            result = runner.invoke(cli, ["init", "config.json", model_path])
            assert result.exit_code == 0
            assert "created successfully" in result.output.lower()
        logger.success("init command test passed.")

    @patch("wpostgresql.cli.main.WPostgreSQL")
    def test_list_command(self, mock_wpg: Mock) -> None:
        """Test list command.

        Args:
            mock_wpg: Mocked WPostgreSQL class.
        """
        logger.info("Testing list command...")

        class Person(BaseModel):
            """Test model."""

            id: int
            name: str

        mock_db = MagicMock()
        mock_db.get_paginated.return_value = [Person(id=1, name="Alice")]
        mock_wpg.return_value = mock_db

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w", encoding="utf-8") as f:
                f.write('{"dbname": "test"}')

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(
                    """
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
"""
                )
                model_path = f.name

            result = runner.invoke(cli, ["list", "config.json", model_path])
            assert result.exit_code == 0
            assert "Alice" in result.output
        logger.success("list command test passed.")

    @patch("wpostgresql.cli.main.WPostgreSQL")
    def test_insert_command(self, mock_wpg: Mock) -> None:
        """Test insert command.

        Args:
            mock_wpg: Mocked WPostgreSQL class.
        """
        logger.info("Testing insert command...")
        mock_db = MagicMock()
        mock_wpg.return_value = mock_db

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w", encoding="utf-8") as f:
                f.write('{"dbname": "test"}')

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(
                    """
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
"""
                )
                model_path = f.name

            result = runner.invoke(
                cli, ["insert", "config.json", model_path, '{"id": 1, "name": "Alice"}']
            )
            assert result.exit_code == 0
            assert "successfully" in result.output
        logger.success("insert command test passed.")

    @patch("wpostgresql.cli.main.WPostgreSQL")
    def test_count_command(self, mock_wpg: Mock) -> None:
        """Test count command.

        Args:
            mock_wpg: Mocked WPostgreSQL class.
        """
        logger.info("Testing count command...")
        mock_db = MagicMock()
        mock_db.count.return_value = 100
        mock_wpg.return_value = mock_db

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w", encoding="utf-8") as f:
                f.write('{"dbname": "test"}')

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(
                    """
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
"""
                )
                model_path = f.name

            result = runner.invoke(cli, ["count", "config.json", model_path])
            assert result.exit_code == 0
            assert "100" in result.output
        logger.success("count command test passed.")

    @patch("wpostgresql.cli.main.WPostgreSQL")
    def test_get_command_found(self, mock_wpg: Mock) -> None:
        """Test get command with found record.

        Args:
            mock_wpg: Mocked WPostgreSQL class.
        """
        logger.info("Testing get command (found)...")

        class Person(BaseModel):
            """Test model."""

            id: int
            name: str

        mock_db = MagicMock()
        mock_db.get_by_field.return_value = [Person(id=1, name="Alice")]
        mock_wpg.return_value = mock_db

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w", encoding="utf-8") as f:
                f.write('{"dbname": "test"}')

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(
                    """
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
"""
                )
                model_path = f.name

            result = runner.invoke(cli, ["get", "config.json", model_path, "1"])
            assert result.exit_code == 0
            assert "Alice" in result.output
        logger.success("get command (found) test passed.")

    @patch("wpostgresql.cli.main.WPostgreSQL")
    def test_get_command_not_found(self, mock_wpg: Mock) -> None:
        """Test get command with no record.

        Args:
            mock_wpg: Mocked WPostgreSQL class.
        """
        logger.info("Testing get command (not found)...")
        mock_db = MagicMock()
        mock_db.get_by_field.return_value = []
        mock_wpg.return_value = mock_db

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w", encoding="utf-8") as f:
                f.write('{"dbname": "test"}')

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(
                    """
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
"""
                )
                model_path = f.name

            result = runner.invoke(cli, ["get", "config.json", model_path, "1"])
            assert result.exit_code == 1
            assert "not found" in result.output.lower()
        logger.success("get command (not found) test passed.")

    @patch("wpostgresql.cli.main.WPostgreSQL")
    def test_delete_command(self, mock_wpg: Mock) -> None:
        """Test delete command.

        Args:
            mock_wpg: Mocked WPostgreSQL class.
        """
        logger.info("Testing delete command...")
        mock_db = MagicMock()
        mock_wpg.return_value = mock_db

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w", encoding="utf-8") as f:
                f.write('{"dbname": "test"}')

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(
                    """
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
"""
                )
                model_path = f.name

            result = runner.invoke(cli, ["delete", "config.json", model_path, "1"])
            assert result.exit_code == 0
            assert "deleted" in result.output.lower()
        logger.success("delete command test passed.")

    @patch("wpostgresql.cli.main.TableSync")
    @patch("click.confirm")
    def test_drop_command_confirm(self, mock_confirm: Mock, mock_sync: Mock) -> None:
        """Test drop command with confirmation.

        Args:
            mock_confirm: Mocked click.confirm.
            mock_sync: Mocked TableSync class.
        """
        logger.info("Testing drop command (confirmed)...")
        mock_confirm.return_value = True
        mock_sync_instance = MagicMock()
        mock_sync.return_value = mock_sync_instance

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w", encoding="utf-8") as f:
                f.write('{"dbname": "test"}')

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(
                    """
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
"""
                )
                model_path = f.name

            result = runner.invoke(cli, ["drop", "config.json", model_path])
            assert result.exit_code == 0
        logger.success("drop command (confirmed) test passed.")

    @patch("wpostgresql.cli.main.TableSync")
    @patch("click.confirm")
    def test_drop_command_cancel(self, mock_confirm: Mock, _mock_sync: Mock) -> None:
        """Test drop command cancelled.

        Args:
            mock_confirm: Mocked click.confirm.
            _mock_sync: Mocked TableSync class.
        """
        logger.info("Testing drop command (cancelled)...")
        mock_confirm.return_value = False

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w", encoding="utf-8") as f:
                f.write('{"dbname": "test"}')

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(
                    """
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
"""
                )
                model_path = f.name

            result = runner.invoke(cli, ["drop", "config.json", model_path])
            assert result.exit_code == 0
        logger.success("drop command (cancelled) test passed.")


class TestLoadModel:
    """Tests for load_model function.

    This class groups tests that verify correctly loading Pydantic models
    from external Python files.
    """

    def test_load_model_from_file(self) -> None:
        """Test loading Pydantic model from file.

        Verifies that load_model correctly imports and identifies
        the Pydantic model in a temporary file.
        """
        logger.info("Testing load_model from file...")
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                """
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
"""
            )
            model_path = f.name

        model: type[BaseModel] = load_model(model_path)
        assert model.__name__ == "Person"
        assert "id" in model.model_fields
        assert "name" in model.model_fields
        logger.success("load_model from file test passed.")

    def test_load_model_no_model_found(self) -> None:
        """Test loading from file with no Pydantic model.

        Ensures that a ValueError is raised when the file doesn't
        contain a Pydantic model.
        """
        logger.info("Testing load_model with no model...")
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("x = 1")
            model_path = f.name

        with pytest.raises(ValueError, match="No Pydantic model found"):
            load_model(model_path)
        logger.success("load_model with no model test passed.")
