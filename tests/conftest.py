"""Shared fixtures for CLI tests."""

import json
import os
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from alphaloops.cli import main


class FakeResult:
    """Fake SDK result that quacks like a response object."""

    def __init__(self, data):
        self._data = data

    def to_dict(self):
        return self._data

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)


def make_fake_client():
    """Build a fully-mocked AlphaLoops client."""
    client = MagicMock()

    # carriers
    client.carriers.get.return_value = FakeResult({
        "dot_number": "12345",
        "legal_name": "TEST TRUCKING LLC",
        "mc_number": "999999",
        "phy_state": "TX",
        "total_trucks": 42,
        "total_drivers": 50,
        "safety_rating": "Satisfactory",
        "operating_status": "AUTHORIZED",
    })
    client.carriers.get_by_mc.return_value = FakeResult({
        "dot_number": "12345",
        "legal_name": "TEST TRUCKING LLC",
        "mc_number": "999999",
        "phy_state": "TX",
        "total_trucks": 42,
        "total_drivers": 50,
    })
    client.carriers.search.return_value = FakeResult({
        "results": [
            {"legal_name": "TEST TRUCKING LLC", "dot_number": "12345", "mc_number": "999999", "phy_state": "TX", "confidence": 0.95},
        ],
    })
    client.carriers.authority.return_value = FakeResult({
        "results": [
            {"authority_type": "COMMON", "status": "ACTIVE", "effective_date": "2020-01-01"},
        ],
    })
    client.carriers.news.return_value = FakeResult({
        "results": [
            {"title": "Test Article", "source": "FreightWaves", "published_date": "2025-06-01"},
        ],
    })

    # fleet
    client.fleet.trucks.return_value = FakeResult({
        "results": [
            {"vin": "1XKAD49X0XJ000001", "make": "KENWORTH", "model_year": "2024", "gvw": "80000"},
        ],
    })
    client.fleet.trailers.return_value = FakeResult({
        "results": [
            {"vin": "1GRAA0622DB000001", "manufacturer": "GREAT DANE", "type": "VAN", "reefer": False},
        ],
    })

    # inspections
    client.inspections.list.return_value = FakeResult({
        "results": [
            {"inspection_id": "INS-001", "date": "2025-03-01", "state": "TX", "oos_total": 0},
        ],
    })
    client.inspections.violations.return_value = FakeResult({
        "results": [
            {"code": "395.8", "description": "Log violation", "basic_category": "HOS", "oos": False},
        ],
    })

    # crashes
    client.crashes.list.return_value = FakeResult({
        "results": [
            {"date": "2025-01-15", "severity": "INJURY", "fatalities": 0, "injuries": 1, "state": "TX"},
        ],
    })

    # contacts
    client.contacts.search.return_value = FakeResult({
        "results": [
            {"name": "Jane Doe", "job_title": "VP Operations", "seniority": "vp"},
        ],
    })
    client.contacts.enrich.return_value = FakeResult({
        "name": "Jane Doe",
        "email": "jane@test.com",
        "phone": "555-1234",
        "job_title": "VP Operations",
        "company_name": "TEST TRUCKING LLC",
        "linkedin_url": "https://linkedin.com/in/janedoe",
    })

    return client


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_client(monkeypatch):
    """Patch ClientState so it uses a fake client instead of hitting the API."""
    client = make_fake_client()

    from alphaloops.cli.state import ClientState
    original_init = ClientState.__init__

    def patched_init(self, api_key=None, output_json=False, output_python=False, output_typescript=False):
        self._api_key = "ak_fake_key_for_testing"
        self.output_json = output_json
        self.output_python = output_python
        self.output_typescript = output_typescript
        self._client = client

    monkeypatch.setattr(ClientState, "__init__", patched_init)
    return client
