"""Tests for all CLI commands using mocked SDK client."""

import json

import pytest
from click.testing import CliRunner

from alphaloops.cli import main


class TestRootCommands:
    def test_help(self, runner, mock_client):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "loopsh" in result.output or "FMCSA" in result.output

    def test_version(self, runner, mock_client):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "loopsh" in result.output

    def test_no_args_shows_help(self, runner, mock_client):
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        assert "Usage" in result.output or "carriers" in result.output


class TestLogin:
    def test_login_with_arg(self, runner, mock_client, tmp_path, monkeypatch):
        config_path = tmp_path / ".alphaloops"
        monkeypatch.setattr("os.path.expanduser", lambda p: str(config_path) if p == "~/.alphaloops" else p)
        result = runner.invoke(main, ["login", "ak_test_key_12345"])
        assert result.exit_code == 0
        assert config_path.exists()
        data = json.loads(config_path.read_text())
        assert data["api_key"] == "ak_test_key_12345"

    def test_login_prompts_when_no_arg(self, runner, mock_client, tmp_path, monkeypatch):
        config_path = tmp_path / ".alphaloops"
        monkeypatch.setattr("os.path.expanduser", lambda p: str(config_path) if p == "~/.alphaloops" else p)
        result = runner.invoke(main, ["login"], input="ak_prompted_key\n")
        assert result.exit_code == 0
        data = json.loads(config_path.read_text())
        assert data["api_key"] == "ak_prompted_key"


class TestCarriers:
    def test_get(self, runner, mock_client):
        result = runner.invoke(main, ["carriers", "get", "12345"])
        assert result.exit_code == 0
        assert "TEST TRUCKING" in result.output

    def test_get_json(self, runner, mock_client):
        result = runner.invoke(main, ["--json", "carriers", "get", "12345"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["legal_name"] == "TEST TRUCKING LLC"

    def test_mc(self, runner, mock_client):
        result = runner.invoke(main, ["carriers", "mc", "999999"])
        assert result.exit_code == 0
        mock_client.carriers.get_by_mc.assert_called_once()

    def test_search(self, runner, mock_client):
        result = runner.invoke(main, ["carriers", "search", "Test"])
        assert result.exit_code == 0
        assert "TEST TRUCKING" in result.output

    def test_search_with_filters(self, runner, mock_client):
        result = runner.invoke(main, ["carriers", "search", "Test", "--state", "TX", "--limit", "5"])
        assert result.exit_code == 0
        mock_client.carriers.search.assert_called_once_with(
            "Test", domain=None, state="TX", city=None, page=1, limit=5,
        )

    def test_authority(self, runner, mock_client):
        result = runner.invoke(main, ["carriers", "authority", "12345"])
        assert result.exit_code == 0
        mock_client.carriers.authority.assert_called_once()

    def test_news(self, runner, mock_client):
        result = runner.invoke(main, ["carriers", "news", "12345"])
        assert result.exit_code == 0
        mock_client.carriers.news.assert_called_once()

    def test_news_with_dates(self, runner, mock_client):
        result = runner.invoke(main, ["carriers", "news", "12345", "--start-date", "2025-01-01", "--end-date", "2025-06-01"])
        assert result.exit_code == 0
        mock_client.carriers.news.assert_called_once_with(
            "12345", start_date="2025-01-01", end_date="2025-06-01", page=1, limit=25,
        )


class TestFleet:
    def test_trucks(self, runner, mock_client):
        result = runner.invoke(main, ["fleet", "trucks", "12345"])
        assert result.exit_code == 0
        assert "KENWORTH" in result.output

    def test_trucks_json(self, runner, mock_client):
        result = runner.invoke(main, ["--json", "fleet", "trucks", "12345"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["results"][0]["make"] == "KENWORTH"

    def test_trailers(self, runner, mock_client):
        result = runner.invoke(main, ["fleet", "trailers", "12345"])
        assert result.exit_code == 0
        assert "GREAT DANE" in result.output


class TestInspections:
    def test_list(self, runner, mock_client):
        result = runner.invoke(main, ["inspections", "list", "12345"])
        assert result.exit_code == 0
        assert "INS-001" in result.output

    def test_violations(self, runner, mock_client):
        result = runner.invoke(main, ["inspections", "violations", "INS-001"])
        assert result.exit_code == 0
        assert "395.8" in result.output


class TestCrashes:
    def test_list(self, runner, mock_client):
        result = runner.invoke(main, ["crashes", "list", "12345"])
        assert result.exit_code == 0
        assert "INJURY" in result.output

    def test_list_with_severity(self, runner, mock_client):
        result = runner.invoke(main, ["crashes", "list", "12345", "--severity", "FATAL"])
        assert result.exit_code == 0
        mock_client.crashes.list.assert_called_once_with(
            "12345", start_date=None, end_date=None, severity="FATAL", page=1, limit=25,
        )


class TestShortcuts:
    """Test that bare DOT numbers forward to the default subcommand."""

    def test_carriers_shortcut(self, runner, mock_client):
        result = runner.invoke(main, ["carriers", "12345"])
        assert result.exit_code == 0
        assert "TEST TRUCKING" in result.output
        mock_client.carriers.get.assert_called_once()

    def test_crashes_shortcut(self, runner, mock_client):
        result = runner.invoke(main, ["crashes", "12345"])
        assert result.exit_code == 0
        mock_client.crashes.list.assert_called_once()

    def test_fleet_shortcut(self, runner, mock_client):
        result = runner.invoke(main, ["fleet", "12345"])
        assert result.exit_code == 0
        mock_client.fleet.trucks.assert_called_once()

    def test_inspections_shortcut(self, runner, mock_client):
        result = runner.invoke(main, ["inspections", "12345"])
        assert result.exit_code == 0
        mock_client.inspections.list.assert_called_once()

    def test_shortcut_with_options(self, runner, mock_client):
        result = runner.invoke(main, ["crashes", "12345", "--severity", "FATAL"])
        assert result.exit_code == 0
        mock_client.crashes.list.assert_called_once_with(
            "12345", start_date=None, end_date=None, severity="FATAL", page=1, limit=25,
        )


class TestContacts:
    def test_search_by_dot(self, runner, mock_client):
        result = runner.invoke(main, ["contacts", "search", "--dot", "12345"])
        assert result.exit_code == 0
        assert "Jane Doe" in result.output

    def test_search_requires_dot_or_company(self, runner, mock_client):
        result = runner.invoke(main, ["contacts", "search"])
        assert result.exit_code != 0

    def test_enrich(self, runner, mock_client):
        result = runner.invoke(main, ["contacts", "enrich", "contact_123"])
        assert result.exit_code == 0
        assert "jane@test.com" in result.output

    def test_enrich_json(self, runner, mock_client):
        result = runner.invoke(main, ["--json", "contacts", "enrich", "contact_123"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["email"] == "jane@test.com"
