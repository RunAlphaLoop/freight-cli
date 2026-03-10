"""Output helpers — JSON for machines, Rich tables for humans."""

import json

import click
from rich.console import Console
from rich.table import Table

console = Console()


class DefaultGroup(click.Group):
    """A Click group that forwards unknown subcommands to a default command.

    If the first arg isn't a known subcommand, it's treated as an argument
    to the default command (e.g. `loopsh crashes 80806` → `loopsh crashes list 80806`).
    """

    def __init__(self, *args, default_cmd=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_cmd = default_cmd

    def parse_args(self, ctx, args):
        if args and self.default_cmd and args[0] not in self.commands and not args[0].startswith("-"):
            args = [self.default_cmd] + args
        return super().parse_args(ctx, args)


def print_json(data):
    """Print data as formatted JSON."""
    if hasattr(data, "to_dict"):
        data = data.to_dict()
    console.print(json.dumps(data, indent=2, default=str))


def print_kv(pairs, title=None):
    """Print key-value pairs as a Rich table."""
    table = Table(show_header=False, title=title, title_style="bold")
    table.add_column("Key", style="bold cyan", no_wrap=True)
    table.add_column("Value")
    for k, v in pairs.items():
        table.add_row(str(k), str(v) if v is not None else "—")
    console.print(table)


def print_list_table(rows, columns, title=None):
    """Print a list of dicts as a Rich table."""
    table = Table(title=title, title_style="bold")
    for col in columns:
        table.add_column(col, no_wrap=(col in ("DOT", "MC", "VIN", "ID")))
    for row in rows:
        vals = []
        for col in columns:
            key = col.lower().replace(" ", "_")
            v = row.get(key) if isinstance(row, dict) else getattr(row, key, None)
            vals.append(str(v) if v is not None else "—")
        table.add_row(*vals)
    console.print(table)
