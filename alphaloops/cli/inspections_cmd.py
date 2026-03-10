"""Inspection and violation commands."""

import click

from .codegen import print_python, print_typescript
from .state import pass_state
from .output import DefaultGroup, print_json, print_list_table


@click.group(cls=DefaultGroup, default_cmd="list")
def inspections():
    """Roadside inspections and violation details.

    \b
    Shortcut: loopsh inspections <DOT_NUMBER>
    equals:   loopsh inspections list <DOT_NUMBER>

    \b
    Examples:
      loopsh inspections list 2247505
      loopsh inspections 2247505                        # same thing
      loopsh inspections violations INS-12345
      loopsh --json inspections 2247505
    """
    pass


@inspections.command("list")
@click.argument("dot_number")
@click.option("--limit", default=50, type=int, help="Results per page.")
@click.option("--offset", default=0, type=int, help="Offset.")
@pass_state
def list_inspections(state, dot_number, limit, offset):
    """List roadside inspections for a carrier.

    \b
    Examples:
      loopsh inspections list 2247505
      loopsh inspections 2247505
      loopsh --json inspections list 2247505
    """
    if state.codegen:
        fn = print_python if state.codegen == "python" else print_typescript
        fn("inspections.list", [dot_number], {"limit": limit, "offset": offset})
        return

    result = state.client.inspections.list(dot_number, limit=limit, offset=offset)

    if state.output_json:
        print_json(result)
    else:
        data = result.to_dict() if hasattr(result, "to_dict") else dict(result)
        rows = data.get("results", [])
        if not rows:
            click.echo("No inspections found.")
            return
        print_list_table(rows, ["inspection_id", "date", "state", "oos_total"], title="Inspections")


@inspections.command()
@click.argument("inspection_id")
@click.option("--page", default=1, type=int, help="Page number.")
@click.option("--limit", default=25, type=int, help="Results per page.")
@pass_state
def violations(state, inspection_id, page, limit):
    """List violations for a specific inspection.

    \b
    Examples:
      loopsh inspections violations INS-12345
      loopsh --json inspections violations INS-12345
    """
    if state.codegen:
        fn = print_python if state.codegen == "python" else print_typescript
        fn("inspections.violations", [inspection_id], {"page": page, "limit": limit})
        return

    result = state.client.inspections.violations(inspection_id, page=page, limit=limit)

    if state.output_json:
        print_json(result)
    else:
        data = result.to_dict() if hasattr(result, "to_dict") else dict(result)
        rows = data.get("results", [])
        if not rows:
            click.echo("No violations found.")
            return
        print_list_table(rows, ["code", "description", "basic_category", "oos"], title="Violations")
