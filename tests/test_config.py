"""Tests for config file resolution and directory walking."""

import json
import os

import pytest

from alphaloops.cli.state import find_config_file, resolve_api_key


class TestFindConfigFile:
    def test_finds_config_in_cwd(self, tmp_path, monkeypatch):
        config = tmp_path / ".alphaloops"
        config.write_text('{"api_key": "ak_test"}')
        monkeypatch.setattr(os, "getcwd", lambda: str(tmp_path))
        monkeypatch.setenv("HOME", str(tmp_path))
        assert find_config_file() == str(config)

    def test_walks_up_to_parent(self, tmp_path, monkeypatch):
        child = tmp_path / "project" / "src"
        child.mkdir(parents=True)
        config = tmp_path / ".alphaloops"
        config.write_text('{"api_key": "ak_test"}')
        monkeypatch.setattr(os, "getcwd", lambda: str(child))
        monkeypatch.setenv("HOME", str(tmp_path))
        assert find_config_file() == str(config)

    def test_stops_at_home(self, tmp_path, monkeypatch):
        home = tmp_path / "home" / "user"
        home.mkdir(parents=True)
        project = home / "code" / "project"
        project.mkdir(parents=True)
        # Config above home — should NOT be found
        above_home_config = tmp_path / ".alphaloops"
        above_home_config.write_text('{"api_key": "ak_nope"}')
        monkeypatch.setattr(os, "getcwd", lambda: str(project))
        monkeypatch.setenv("HOME", str(home))
        # No config in home or below
        assert find_config_file() is None

    def test_falls_back_to_home_config(self, tmp_path, monkeypatch):
        home = tmp_path / "home"
        home.mkdir()
        config = home / ".alphaloops"
        config.write_text('{"api_key": "ak_home"}')
        project = home / "code"
        project.mkdir()
        monkeypatch.setattr(os, "getcwd", lambda: str(project))
        monkeypatch.setenv("HOME", str(home))
        assert find_config_file() == str(config)

    def test_returns_none_when_no_config(self, tmp_path, monkeypatch):
        monkeypatch.setattr(os, "getcwd", lambda: str(tmp_path))
        monkeypatch.setenv("HOME", str(tmp_path))
        assert find_config_file() is None

    def test_prefers_nearest_config(self, tmp_path, monkeypatch):
        home = tmp_path
        project = home / "code" / "myproject"
        project.mkdir(parents=True)
        # Config in home
        home_config = home / ".alphaloops"
        home_config.write_text('{"api_key": "ak_home"}')
        # Config in code/
        code_config = home / "code" / ".alphaloops"
        code_config.write_text('{"api_key": "ak_code"}')
        monkeypatch.setattr(os, "getcwd", lambda: str(project))
        monkeypatch.setenv("HOME", str(home))
        # Should find the nearest one (code/)
        assert find_config_file() == str(code_config)


class TestResolveApiKey:
    def test_explicit_key_wins(self, monkeypatch):
        monkeypatch.setenv("ALPHALOOPS_API_KEY", "ak_env")
        assert resolve_api_key(explicit_key="ak_explicit") == "ak_explicit"

    def test_env_var_second(self, monkeypatch):
        monkeypatch.setenv("ALPHALOOPS_API_KEY", "ak_env")
        assert resolve_api_key() == "ak_env"

    def test_config_file_json(self, tmp_path, monkeypatch):
        monkeypatch.delenv("ALPHALOOPS_API_KEY", raising=False)
        config = tmp_path / ".alphaloops"
        config.write_text(json.dumps({"api_key": "ak_json"}))
        monkeypatch.setattr(os, "getcwd", lambda: str(tmp_path))
        monkeypatch.setenv("HOME", str(tmp_path))
        assert resolve_api_key() == "ak_json"

    def test_config_file_keyvalue(self, tmp_path, monkeypatch):
        monkeypatch.delenv("ALPHALOOPS_API_KEY", raising=False)
        config = tmp_path / ".alphaloops"
        config.write_text("ALPHALOOPS_API_KEY=ak_kv\n")
        monkeypatch.setattr(os, "getcwd", lambda: str(tmp_path))
        monkeypatch.setenv("HOME", str(tmp_path))
        assert resolve_api_key() == "ak_kv"

    def test_returns_none_when_nothing(self, tmp_path, monkeypatch):
        monkeypatch.delenv("ALPHALOOPS_API_KEY", raising=False)
        monkeypatch.setattr(os, "getcwd", lambda: str(tmp_path))
        monkeypatch.setenv("HOME", str(tmp_path))
        assert resolve_api_key() is None
