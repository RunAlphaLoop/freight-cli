"""Fleet data commands — trucks and trailers."""

import click

from .state import pass_state
from .output import print_json, print_list_table


@click.group()
def fleet():
    """Truck and trailer fleet data."""
    pass


@fleet.command()
@click.argument("dot_number")
@click.option("--limit", default=50, type=int, help="Results per page.")
@click.option("--offset", default=0, type=int, help="Offset.")
@pass_state
def trucks(state, dot_number, limit, offset):
    """List registered trucks for a carrier."""
    result = state.client.fleet.trucks(dot_number, limit=limit, offset=offset)

    if state.output_json:
        print_json(result)
    else:
        data = result.to_dict() if hasattr(result, "to_dict") else dict(result)
        rows = data.get("results", [])
        if not rows:
            click.echo("No trucks found.")
            return
        print_list_table(rows, ["vin", "make", "model_year", "gvw"], title="Trucks")


@fleet.command()
@click.argument("dot_number")
@click.option("--limit", default=50, type=int, help="Results per page.")
@click.option("--offset", default=0, type=int, help="Offset.")
@pass_state
def trailers(state, dot_number, limit, offset):
    """List registered trailers for a carrier."""
    result = state.client.fleet.trailers(dot_number, limit=limit, offset=offset)

    if state.output_json:
        print_json(result)
    else:
        data = result.to_dict() if hasattr(result, "to_dict") else dict(result)
        rows = data.get("results", [])
        if not rows:
            click.echo("No trailers found.")
            return
        print_list_table(rows, ["vin", "manufacturer", "type", "reefer"], title="Trailers")
