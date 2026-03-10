"""Tests for --python and --typescript code generation."""

import json

import pytest
from click.testing import CliRunner

from alphaloops.cli import main


class TestPythonCodegen:
    def test_carriers_get(self, runner, mock_client):
        result = runner.invoke(main, ["--python", "carriers", "get", "2247505"])
        assert result.exit_code == 0
        assert "from alphaloops.freight import AlphaLoops" in result.output
        assert 'al.carriers.get("2247505")' in result.output

    def test_carriers_search(self, runner, mock_client):
        result = runner.invoke(main, ["--python", "carriers", "search", "Werner"])
        assert result.exit_code == 0
        assert 'al.carriers.search("Werner"' in result.output

    def test_fleet_trucks(self, runner, mock_client):
        result = runner.invoke(main, ["--python", "fleet", "trucks", "12345"])
        assert result.exit_code == 0
        assert 'al.fleet.trucks("12345"' in result.output

    def test_crashes_with_severity(self, runner, mock_client):
        result = runner.invoke(main, ["--python", "crashes", "12345", "--severity", "FATAL"])
        assert result.exit_code == 0
        assert 'al.crashes.list("12345"' in result.output
        assert 'severity="FATAL"' in result.output

    def test_contacts_search(self, runner, mock_client):
        result = runner.invoke(main, ["--python", "contacts", "search", "--dot", "12345"])
        assert result.exit_code == 0
        assert "al.contacts.search(" in result.output
        assert 'dot_number="12345"' in result.output

    def test_contacts_enrich(self, runner, mock_client):
        result = runner.invoke(main, ["--python", "contacts", "enrich", "abc123"])
        assert result.exit_code == 0
        assert 'al.contacts.enrich("abc123")' in result.output

    def test_does_not_call_api(self, runner, mock_client):
        """Code gen should NOT make any API calls."""
        runner.invoke(main, ["--python", "carriers", "get", "12345"])
        mock_client.carriers.get.assert_not_called()


class TestTypescriptCodegen:
    def test_carriers_get(self, runner, mock_client):
        result = runner.invoke(main, ["--typescript", "carriers", "get", "2247505"])
        assert result.exit_code == 0
        assert 'import AlphaLoops from "alphaloops"' in result.output
        assert 'al.carriers.get("2247505")' in result.output

    def test_crashes_with_severity(self, runner, mock_client):
        result = runner.invoke(main, ["--typescript", "crashes", "12345", "--severity", "FATAL"])
        assert result.exit_code == 0
        assert 'al.crashes.list("12345"' in result.output
        assert 'severity: "FATAL"' in result.output

    def test_contacts_search(self, runner, mock_client):
        result = runner.invoke(main, ["--typescript", "contacts", "search", "--dot", "12345"])
        assert result.exit_code == 0
        assert "al.contacts.search(" in result.output
        assert 'dotNumber: "12345"' in result.output
