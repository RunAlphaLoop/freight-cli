"""AlphaLoops Freight CLI — command-line interface for FMCSA carrier data."""

__version__ = "0.2.0"

import sys

import click
from rich.console import Console

from .state import ClientState, pass_state
from . import carriers_cmd, fleet_cmd, inspections_cmd, crashes_cmd, contacts_cmd

console = Console(stderr=True)


@click.group(invoke_without_command=True)
@click.option("--json", "output_json", is_flag=True, help="Output raw JSON (for scripts and agents).")
@click.option("--api-key", envvar="ALPHALOOPS_API_KEY", default=None, help="API key (default: env/config file).")
@click.version_option(__version__, prog_name="loopsh")
@click.pass_context
def main(ctx, output_json, api_key):
    """AlphaLoops Freight CLI — FMCSA carrier data at your fingertips."""
    ctx.ensure_object(dict)
    ctx.obj = ClientState(api_key=api_key, output_json=output_json)

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


main.add_command(carriers_cmd.carriers)
main.add_command(fleet_cmd.fleet)
main.add_command(inspections_cmd.inspections)
main.add_command(crashes_cmd.crashes)
main.add_command(contacts_cmd.contacts)


@main.command()
@click.argument("api_key")
def login(api_key):
    """Save your API key to ~/.alphaloops."""
    import os
    config_path = os.path.expanduser("~/.alphaloops")
    with open(config_path, "w") as f:
        f.write(f"api_key={api_key}\n")
    console.print(f"[green]API key saved to {config_path}[/green]")


def cli():
    """Entry point that catches exceptions cleanly."""
    try:
        main(standalone_mode=False)
    except click.ClickException as e:
        console.print(f"[red]Error:[/red] {e.format_message()}")
        sys.exit(e.exit_code)
    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
