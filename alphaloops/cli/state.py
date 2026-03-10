"""Client state — lazy SDK initialization and output mode."""

import os

import click
from alphaloops.freight import AlphaLoops
from alphaloops.freight.config import resolve_config


def find_config_file():
    """Walk from cwd up to home looking for .alphaloops config file."""
    home = os.path.expanduser("~")
    current = os.getcwd()

    while True:
        candidate = os.path.join(current, ".alphaloops")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current or not current.startswith(home):
            break
        current = parent

    # Fall back to ~/.alphaloops
    home_config = os.path.join(home, ".alphaloops")
    if os.path.isfile(home_config):
        return home_config
    return None


def resolve_api_key(explicit_key=None):
    """Resolve API key: explicit arg → env var → directory walk → ~/.alphaloops."""
    if explicit_key:
        return explicit_key

    env_key = os.environ.get("ALPHALOOPS_API_KEY")
    if env_key:
        return env_key

    config_path = find_config_file()
    if config_path:
        # Use the SDK's own parser but point it at the found file
        import json
        try:
            with open(config_path) as f:
                text = f.read().strip()
            if text.startswith("{"):
                data = json.loads(text)
                return data.get("api_key")
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip().lower()
                value = value.strip().strip("'\"")
                if key in ("api_key", "alphaloops_api_key"):
                    return value
        except OSError:
            pass

    return None


class ClientState:
    def __init__(self, api_key=None, output_json=False, output_python=False, output_typescript=False):
        self._api_key = resolve_api_key(explicit_key=api_key)
        self.output_json = output_json
        self.output_python = output_python
        self.output_typescript = output_typescript
        self._client = None

    @property
    def codegen(self):
        """Return 'python', 'typescript', or None."""
        if self.output_python:
            return "python"
        if self.output_typescript:
            return "typescript"
        return None

    @property
    def client(self):
        if self._client is None:
            self._client = AlphaLoops(api_key=self._api_key)
        return self._client


pass_state = click.make_pass_decorator(ClientState)
