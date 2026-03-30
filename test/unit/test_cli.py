"""Tests for CLI module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from wpostgresql.cli.main import cli, load_model


class TestCLI:
    """Tests for CLI commands."""

    def test_cli_help(self):
        """Test CLI shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "wpostgresql" in result.output

    def test_cli_version(self):
        """Test CLI shows version."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.2.0" in result.output

    @patch("wpostgresql.cli.main.ConnectionManager")
    def test_test_connection_success(self, mock_cm):
        """Test test-connection command success."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w") as f:
                f.write('{"dbname": "test"}')

            result = runner.invoke(cli, ["test-connection", "config.json"])
            assert result.exit_code == 0
            assert "Connection successful" in result.output

    @patch("wpostgresql.cli.main.ConnectionManager")
    def test_test_connection_failure(self, mock_cm):
        """Test test-connection command failure."""
        mock_cm.side_effect = Exception("Connection failed")

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w") as f:
                f.write('{"dbname": "test"}')

            result = runner.invoke(cli, ["test-connection", "config.json"])
            assert result.exit_code == 1
            assert "Connection failed" in result.output

    @patch("wpostgresql.cli.main.TableSync")
    def test_init_command(self, mock_sync):
        """Test init command."""
        mock_sync_instance = MagicMock()
        mock_sync.return_value = mock_sync_instance

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w") as f:
                f.write('{"dbname": "test"}')

            from pydantic import BaseModel
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write("""
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
""")
                model_path = f.name

            result = runner.invoke(cli, ["init", "config.json", model_path])
            assert result.exit_code == 0
            assert "created successfully" in result.output.lower()

    @patch("wpostgresql.cli.main.WPostgreSQL")
    def test_list_command(self, mock_wpg):
        """Test list command."""
        mock_db = MagicMock()
        mock_db.get_paginated.return_value = []
        mock_wpg.return_value = mock_db

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w") as f:
                f.write('{"dbname": "test"}')

            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write("""
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
""")
                model_path = f.name

            result = runner.invoke(cli, ["list", "config.json", model_path])
            assert result.exit_code == 0

    @patch("wpostgresql.cli.main.WPostgreSQL")
    def test_count_command(self, mock_wpg):
        """Test count command."""
        mock_db = MagicMock()
        mock_db.count.return_value = 100
        mock_wpg.return_value = mock_db

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w") as f:
                f.write('{"dbname": "test"}')

            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write("""
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
""")
                model_path = f.name

            result = runner.invoke(cli, ["count", "config.json", model_path])
            assert result.exit_code == 0
            assert "100" in result.output

    @patch("wpostgresql.cli.main.WPostgreSQL")
    def test_get_command_found(self, mock_wpg):
        """Test get command with found record."""
        from pydantic import BaseModel

        class Person(BaseModel):
            id: int
            name: str

        mock_db = MagicMock()
        mock_db.get_by_field.return_value = [Person(id=1, name="Alice")]
        mock_wpg.return_value = mock_db

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w") as f:
                f.write('{"dbname": "test"}')

            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write("""
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
""")
                model_path = f.name

            result = runner.invoke(cli, ["get", "config.json", model_path, "1"])
            assert result.exit_code == 0
            assert "Alice" in result.output

    @patch("wpostgresql.cli.main.WPostgreSQL")
    def test_get_command_not_found(self, mock_wpg):
        """Test get command with no record."""
        mock_db = MagicMock()
        mock_db.get_by_field.return_value = []
        mock_wpg.return_value = mock_db

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w") as f:
                f.write('{"dbname": "test"}')

            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write("""
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
""")
                model_path = f.name

            result = runner.invoke(cli, ["get", "config.json", model_path, "1"])
            assert result.exit_code == 1
            assert "not found" in result.output.lower()

    @patch("wpostgresql.cli.main.WPostgreSQL")
    def test_delete_command(self, mock_wpg):
        """Test delete command."""
        mock_db = MagicMock()
        mock_wpg.return_value = mock_db

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w") as f:
                f.write('{"dbname": "test"}')

            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write("""
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
""")
                model_path = f.name

            result = runner.invoke(cli, ["delete", "config.json", model_path, "1"])
            assert result.exit_code == 0
            assert "deleted" in result.output.lower()

    @patch("wpostgresql.cli.main.TableSync")
    @patch("click.confirm")
    def test_drop_command_confirm(self, mock_confirm, mock_sync):
        """Test drop command with confirmation."""
        mock_confirm.return_value = True
        mock_sync_instance = MagicMock()
        mock_sync.return_value = mock_sync_instance

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w") as f:
                f.write('{"dbname": "test"}')

            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write("""
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
""")
                model_path = f.name

            result = runner.invoke(cli, ["drop", "config.json", model_path])
            assert result.exit_code == 0

    @patch("wpostgresql.cli.main.TableSync")
    @patch("click.confirm")
    def test_drop_command_cancel(self, mock_confirm, mock_sync):
        """Test drop command cancelled."""
        mock_confirm.return_value = False

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.json", "w") as f:
                f.write('{"dbname": "test"}')

            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write("""
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
""")
                model_path = f.name

            result = runner.invoke(cli, ["drop", "config.json", model_path])
            assert result.exit_code == 0


class TestLoadModel:
    """Tests for load_model function."""

    def test_load_model_from_file(self):
        """Test loading Pydantic model from file."""
        import tempfile
        from pydantic import BaseModel

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
from pydantic import BaseModel

class Person(BaseModel):
    id: int
    name: str
""")
            model_path = f.name

        model = load_model(model_path)
        assert model.__name__ == "Person"
        assert "id" in model.model_fields
        assert "name" in model.model_fields

    def test_load_model_no_model_found(self):
        """Test loading from file with no Pydantic model."""
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = 1")
            model_path = f.name

        with pytest.raises(ValueError, match="No Pydantic model found"):
            load_model(model_path)
