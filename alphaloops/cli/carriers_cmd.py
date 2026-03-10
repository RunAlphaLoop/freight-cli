"""Carrier profiles, search, authority, and news commands."""

import click

from .codegen import print_python, print_typescript
from .state import pass_state
from .output import DefaultGroup, print_json, print_kv, print_list_table


@click.group(cls=DefaultGroup, default_cmd="get")
def carriers():
    """Carrier profiles, search, authority history, and news.

    \b
    Shortcut: loopsh carriers <DOT_NUMBER>
    equals:   loopsh carriers get <DOT_NUMBER>

    \b
    Examples:
      loopsh carriers get 2247505
      loopsh carriers 2247505                          # same thing
      loopsh carriers get 2247505 --fields legal_name,total_trucks
      loopsh carriers mc 624748
      loopsh carriers search "Werner Enterprises"
      loopsh carriers search "JB Hunt" --state AR
      loopsh carriers authority 2247505
      loopsh carriers news 2247505 --start-date 2025-01-01
    """
    pass


@carriers.command()
@click.argument("dot_number")
@click.option("--fields", default=None, help="Comma-separated field projection.")
@pass_state
def get(state, dot_number, fields):
    """Look up a carrier by DOT number.

    \b
    Examples:
      loopsh carriers get 2247505
      loopsh carriers 2247505
      loopsh carriers get 2247505 --fields legal_name,phone,total_trucks
      loopsh --json carriers get 2247505 | jq '.legal_name'
    """
    field_list = [f.strip() for f in fields.split(",")] if fields else None

    if state.codegen:
        kwargs = {"fields": field_list} if field_list else {}
        fn = print_python if state.codegen == "python" else print_typescript
        fn("carriers.get", [dot_number], kwargs)
        return

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
    """Look up a carrier by MC/MX docket number.

    \b
    Examples:
      loopsh carriers mc 624748
      loopsh --json carriers mc 624748
    """
    field_list = [f.strip() for f in fields.split(",")] if fields else None

    if state.codegen:
        kwargs = {"fields": field_list} if field_list else {}
        fn = print_python if state.codegen == "python" else print_typescript
        fn("carriers.get_by_mc", [mc_number], kwargs)
        return

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
    """Fuzzy search for carriers by company name.

    \b
    Examples:
      loopsh carriers search "Werner Enterprises"
      loopsh carriers search "JB Hunt" --state AR --limit 5
      loopsh --json carriers search "Swift" | jq '.results[].legal_name'

    \b
    Agent workflow — search then get details:
      DOT=$(loopsh --json carriers search "Swift" | jq -r '.results[0].dot_number')
      loopsh carriers get "$DOT"
    """
    if state.codegen:
        kwargs = {"domain": domain, "state": state_filter, "city": city, "page": page, "limit": limit}
        fn = print_python if state.codegen == "python" else print_typescript
        fn("carriers.search", [company_name], kwargs)
        return

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
    """Authority history for a carrier.

    \b
    Examples:
      loopsh carriers authority 2247505
      loopsh --json carriers authority 2247505
    """
    if state.codegen:
        fn = print_python if state.codegen == "python" else print_typescript
        fn("carriers.authority", [dot_number], {"limit": limit, "offset": offset})
        return

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
    """News articles and press mentions for a carrier.

    \b
    Examples:
      loopsh carriers news 2247505
      loopsh carriers news 2247505 --start-date 2025-01-01
    """
    if state.codegen:
        fn = print_python if state.codegen == "python" else print_typescript
        fn("carriers.news", [dot_number], {"start_date": start_date, "end_date": end_date, "page": page, "limit": limit})
        return

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
