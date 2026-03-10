"""Client state — lazy SDK initialization and output mode."""

import click


class ClientState:
    def __init__(self, api_key=None, output_json=False):
        self._api_key = api_key
        self.output_json = output_json
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from alphaloops.freight import AlphaLoops
            self._client = AlphaLoops(api_key=self._api_key)
        return self._client


pass_state = click.make_pass_decorator(ClientState)
