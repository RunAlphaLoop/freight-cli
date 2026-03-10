"""Crash history commands."""

import click

from .state import pass_state
from .output import print_json, print_list_table


@click.group()
def crashes():
    """Carrier crash history."""
    pass


@crashes.command("list")
@click.argument("dot_number")
@click.option("--start-date", default=None, help="Start date (YYYY-MM-DD).")
@click.option("--end-date", default=None, help="End date (YYYY-MM-DD).")
@click.option("--severity", default=None, type=click.Choice(["FATAL", "INJURY", "TOW", "PROPERTY_DAMAGE"], case_sensitive=False), help="Severity filter.")
@click.option("--page", default=1, type=int, help="Page number.")
@click.option("--limit", default=25, type=int, help="Results per page.")
@pass_state
def list_crashes(state, dot_number, start_date, end_date, severity, page, limit):
    """List reported crashes for a carrier."""
    result = state.client.crashes.list(
        dot_number, start_date=start_date, end_date=end_date,
        severity=severity, page=page, limit=limit,
    )

    if state.output_json:
        print_json(result)
    else:
        data = result.to_dict() if hasattr(result, "to_dict") else dict(result)
        rows = data.get("results", [])
        if not rows:
            click.echo("No crashes found.")
            return
        print_list_table(rows, ["date", "severity", "fatalities", "injuries", "state"], title="Crashes")
