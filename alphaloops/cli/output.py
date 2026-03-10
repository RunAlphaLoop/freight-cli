"""Output helpers — JSON for machines, Rich tables for humans."""

import json

from rich.console import Console
from rich.table import Table

console = Console()


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
