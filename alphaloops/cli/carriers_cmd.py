"""Carrier profiles, search, authority, and news commands."""

import click

from .state import pass_state
from .output import print_json, print_kv, print_list_table


@click.group()
def carriers():
    """Carrier profiles, search, authority history, and news."""
    pass


@carriers.command()
@click.argument("dot_number")
@click.option("--fields", default=None, help="Comma-separated field projection.")
@pass_state
def get(state, dot_number, fields):
    """Look up a carrier by DOT number."""
    field_list = [f.strip() for f in fields.split(",")] if fields else None
    result = state.client.carriers.get(dot_number, fields=field_list)

    if state.output_json:
        print_json(result)
    else:
        data = result.to_dict() if hasattr(result, "to_dict") else dict(result)
        print_kv({
            "Legal Name": data.get("legal_name"),
            "DOT Number": data.get("dot_number"),
            "MC Number": data.get("mc_number"),
            "State": data.get("phy_state"),
            "Total Trucks": data.get("total_trucks"),
            "Total Drivers": data.get("total_drivers"),
            "Safety Rating": data.get("safety_rating"),
            "Operating Status": data.get("operating_status"),
        }, title="Carrier Profile")


@carriers.command()
@click.argument("mc_number")
@click.option("--fields", default=None, help="Comma-separated field projection.")
@pass_state
def mc(state, mc_number, fields):
    """Look up a carrier by MC/MX docket number."""
    field_list = [f.strip() for f in fields.split(",")] if fields else None
    result = state.client.carriers.get_by_mc(mc_number, fields=field_list)

    if state.output_json:
        print_json(result)
    else:
        data = result.to_dict() if hasattr(result, "to_dict") else dict(result)
        print_kv({
            "Legal Name": data.get("legal_name"),
            "DOT Number": data.get("dot_number"),
            "MC Number": data.get("mc_number"),
            "State": data.get("phy_state"),
            "Total Trucks": data.get("total_trucks"),
            "Total Drivers": data.get("total_drivers"),
        }, title="Carrier Profile")


@carriers.command()
@click.argument("company_name")
@click.option("--domain", default=None, help="Company domain filter.")
@click.option("--state", "state_filter", default=None, help="State abbreviation filter.")
@click.option("--city", default=None, help="City filter.")
@click.option("--page", default=1, type=int, help="Page number.")
@click.option("--limit", default=10, type=int, help="Results per page.")
@pass_state
def search(state, company_name, domain, state_filter, city, page, limit):
    """Fuzzy search for carriers by company name."""
    result = state.client.carriers.search(
        company_name, domain=domain, state=state_filter, city=city,
        page=page, limit=limit,
    )

    if state.output_json:
        print_json(result)
    else:
        data = result.to_dict() if hasattr(result, "to_dict") else dict(result)
        rows = data.get("results", [])
        if not rows:
            click.echo("No results found.")
            return
        print_list_table(rows, ["legal_name", "dot_number", "mc_number", "phy_state", "confidence"], title="Search Results")


@carriers.command()
@click.argument("dot_number")
@click.option("--limit", default=50, type=int, help="Results per page.")
@click.option("--offset", default=0, type=int, help="Offset.")
@pass_state
def authority(state, dot_number, limit, offset):
    """Authority history for a carrier."""
    result = state.client.carriers.authority(dot_number, limit=limit, offset=offset)

    if state.output_json:
        print_json(result)
    else:
        data = result.to_dict() if hasattr(result, "to_dict") else dict(result)
        rows = data.get("results", [])
        if not rows:
            click.echo("No authority records found.")
            return
        print_list_table(rows, ["authority_type", "status", "effective_date"], title="Authority History")


@carriers.command()
@click.argument("dot_number")
@click.option("--start-date", default=None, help="Start date (YYYY-MM-DD).")
@click.option("--end-date", default=None, help="End date (YYYY-MM-DD).")
@click.option("--page", default=1, type=int, help="Page number.")
@click.option("--limit", default=25, type=int, help="Results per page.")
@pass_state
def news(state, dot_number, start_date, end_date, page, limit):
    """News articles and press mentions for a carrier."""
    result = state.client.carriers.news(
        dot_number, start_date=start_date, end_date=end_date,
        page=page, limit=limit,
    )

    if state.output_json:
        print_json(result)
    else:
        data = result.to_dict() if hasattr(result, "to_dict") else dict(result)
        rows = data.get("results", [])
        if not rows:
            click.echo("No news articles found.")
            return
        print_list_table(rows, ["title", "source", "published_date"], title="News")
